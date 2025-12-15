"""数据导入异步任务

本模块实现数据导入的异步任务，支持：
- 批量数据导入
- 进度跟踪
- 错误处理和重试
"""

from typing import Any, Dict, List
from datetime import datetime
import structlog

from celery import Task, group, chord
from celery.exceptions import Reject

from app.celery_app import celery_app
from app.services.data_import_service import (
    DataImportService,
    RawRecord,
    RecordType,
)

logger = structlog.get_logger(__name__)


class DataImportTask(Task):
    """数据导入任务基类
    
    提供自动重试和错误处理功能
    """
    
    autoretry_for = (Exception,)
    retry_kwargs = {"max_retries": 3}
    retry_backoff = True  # 指数退避
    retry_backoff_max = 600  # 最大退避时间10分钟
    retry_jitter = True  # 添加随机抖动
    
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """任务失败时的回调"""
        logger.error(
            "data_import_task_failed",
            task_id=task_id,
            exception=str(exc),
            args=args,
            kwargs=kwargs,
        )
        super().on_failure(exc, task_id, args, kwargs, einfo)
    
    def on_retry(self, exc, task_id, args, kwargs, einfo):
        """任务重试时的回调"""
        logger.warning(
            "data_import_task_retry",
            task_id=task_id,
            exception=str(exc),
            retry_count=self.request.retries,
        )
        super().on_retry(exc, task_id, args, kwargs, einfo)


@celery_app.task(
    base=DataImportTask,
    name="app.tasks.data_import.import_batch_task",
    bind=True,
    queue="data_import",
)
def import_batch_task(
    self,
    records_data: List[Dict[str, Any]],
    batch_size: int = 1000,
) -> Dict[str, Any]:
    """导入数据批次任务
    
    异步导入一批原始记录到图数据库
    
    Args:
        self: 任务实例
        records_data: 原始记录数据列表（字典格式）
        batch_size: 批处理大小
    
    Returns:
        导入结果字典
    
    Raises:
        Reject: 如果数据验证失败（不重试）
    """
    logger.info(
        "import_batch_task_started",
        task_id=self.request.id,
        records_count=len(records_data),
        batch_size=batch_size,
    )
    
    try:
        # 将字典数据转换为RawRecord对象
        records = []
        for record_data in records_data:
            try:
                record = RawRecord(
                    type=RecordType(record_data["type"]),
                    timestamp=datetime.fromisoformat(record_data["timestamp"]),
                    data=record_data["data"],
                )
                records.append(record)
            except (ValueError, KeyError) as e:
                logger.error(
                    "invalid_record_data",
                    task_id=self.request.id,
                    error=str(e),
                    record_data=record_data,
                )
                # 数据格式错误不重试
                raise Reject(f"Invalid record data: {e}", requeue=False)
        
        # 创建数据导入服务实例
        import_service = DataImportService()
        
        # 执行导入（这是一个异步函数，需要在同步上下文中运行）
        import asyncio
        result = asyncio.run(import_service.import_batch(records, batch_size))
        
        logger.info(
            "import_batch_task_completed",
            task_id=self.request.id,
            success_count=result.success_count,
            failure_count=result.failure_count,
            total_time=result.total_time,
        )
        
        return {
            "task_id": self.request.id,
            "success_count": result.success_count,
            "failure_count": result.failure_count,
            "total_time": result.total_time,
            "records_per_second": result.records_per_second,
            "errors": [
                {
                    "record_index": err.record_index,
                    "record_type": err.record_type.value,
                    "error_message": err.error_message,
                }
                for err in result.errors[:10]  # 只返回前10个错误
            ],
        }
    
    except Reject:
        raise
    except Exception as e:
        logger.error(
            "import_batch_task_error",
            task_id=self.request.id,
            error=str(e),
        )
        raise


@celery_app.task(
    name="app.tasks.data_import.import_records_async",
    queue="data_import",
)
def import_records_async(
    records_data: List[Dict[str, Any]],
    batch_size: int = 1000,
    parallel_batches: int = 4,
) -> str:
    """异步导入大量记录
    
    将大量记录分割成多个批次，并行处理
    
    Args:
        records_data: 原始记录数据列表
        batch_size: 每批处理的记录数
        parallel_batches: 并行处理的批次数
    
    Returns:
        任务组ID
    """
    logger.info(
        "import_records_async_started",
        total_records=len(records_data),
        batch_size=batch_size,
        parallel_batches=parallel_batches,
    )
    
    # 分割数据为多个批次
    batches = []
    for i in range(0, len(records_data), batch_size):
        batch = records_data[i : i + batch_size]
        batches.append(batch)
    
    logger.info(
        "import_records_batches_created",
        total_batches=len(batches),
    )
    
    # 创建任务组并行处理
    job = group(
        import_batch_task.s(batch, batch_size)
        for batch in batches
    )
    
    # 执行任务组
    result = job.apply_async()
    
    logger.info(
        "import_records_async_dispatched",
        group_id=result.id,
        batches_count=len(batches),
    )
    
    return result.id


@celery_app.task(
    name="app.tasks.data_import.aggregate_import_results",
    queue="data_import",
)
def aggregate_import_results(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """聚合导入结果
    
    用于chord的回调，聚合所有批次的导入结果
    
    Args:
        results: 各批次的导入结果列表
    
    Returns:
        聚合后的结果
    """
    total_success = sum(r["success_count"] for r in results)
    total_failure = sum(r["failure_count"] for r in results)
    total_time = max(r["total_time"] for r in results)
    
    all_errors = []
    for r in results:
        all_errors.extend(r.get("errors", []))
    
    logger.info(
        "import_results_aggregated",
        total_success=total_success,
        total_failure=total_failure,
        total_time=total_time,
        total_errors=len(all_errors),
    )
    
    return {
        "total_success": total_success,
        "total_failure": total_failure,
        "total_time": total_time,
        "total_records": total_success + total_failure,
        "errors": all_errors[:50],  # 只返回前50个错误
    }


@celery_app.task(
    name="app.tasks.data_import.import_records_with_callback",
    queue="data_import",
)
def import_records_with_callback(
    records_data: List[Dict[str, Any]],
    batch_size: int = 1000,
) -> str:
    """异步导入记录并聚合结果
    
    使用chord模式：先并行处理所有批次，然后聚合结果
    
    Args:
        records_data: 原始记录数据列表
        batch_size: 每批处理的记录数
    
    Returns:
        Chord任务ID
    """
    logger.info(
        "import_records_with_callback_started",
        total_records=len(records_data),
        batch_size=batch_size,
    )
    
    # 分割数据为多个批次
    batches = []
    for i in range(0, len(records_data), batch_size):
        batch = records_data[i : i + batch_size]
        batches.append(batch)
    
    # 创建chord：先并行处理，然后聚合
    job = chord(
        (import_batch_task.s(batch, batch_size) for batch in batches),
        aggregate_import_results.s(),
    )
    
    # 执行chord
    result = job.apply_async()
    
    logger.info(
        "import_records_with_callback_dispatched",
        chord_id=result.id,
        batches_count=len(batches),
    )
    
    return result.id
