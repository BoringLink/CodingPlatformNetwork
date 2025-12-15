"""Celery应用配置

本模块配置Celery任务队列，用于异步处理：
- 数据导入任务
- LLM分析任务
- 批量处理任务
"""

from celery import Celery
from celery.signals import task_prerun, task_postrun, task_failure
import structlog

from app.config import settings

logger = structlog.get_logger(__name__)

# 创建Celery应用实例
celery_app = Celery(
    "education_kg",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)

# Celery配置
celery_app.conf.update(
    # 任务序列化
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    
    # 时区设置
    timezone="UTC",
    enable_utc=True,
    
    # 任务结果配置
    result_expires=3600,  # 结果保留1小时
    result_backend_transport_options={
        "master_name": "mymaster",
        "visibility_timeout": 3600,
    },
    
    # 任务执行配置
    task_acks_late=True,  # 任务完成后才确认
    task_reject_on_worker_lost=True,  # worker丢失时拒绝任务
    task_track_started=True,  # 跟踪任务开始状态
    
    # 重试配置
    task_default_retry_delay=60,  # 默认重试延迟60秒
    task_max_retries=3,  # 默认最大重试3次
    
    # 速率限制
    task_default_rate_limit="100/m",  # 默认每分钟100个任务
    
    # Worker配置
    worker_prefetch_multiplier=1,  # 每次只预取1个任务（避免阻塞）
    worker_max_tasks_per_child=1000,  # 每个worker子进程最多处理1000个任务后重启
    
    # 任务路由
    task_routes={
        "app.tasks.data_import.*": {"queue": "data_import"},
        "app.tasks.llm_analysis.*": {"queue": "llm_analysis"},
    },
    
    # 任务优先级
    task_queue_max_priority=10,
    task_default_priority=5,
    
    # 监控配置
    worker_send_task_events=True,
    task_send_sent_event=True,
)

# 自动发现任务模块
celery_app.autodiscover_tasks(["app.tasks"])


@task_prerun.connect
def task_prerun_handler(sender=None, task_id=None, task=None, args=None, kwargs=None, **extra):
    """任务开始前的钩子"""
    logger.info(
        "task_started",
        task_id=task_id,
        task_name=task.name,
        args=args,
        kwargs=kwargs,
    )


@task_postrun.connect
def task_postrun_handler(
    sender=None,
    task_id=None,
    task=None,
    args=None,
    kwargs=None,
    retval=None,
    **extra,
):
    """任务完成后的钩子"""
    logger.info(
        "task_completed",
        task_id=task_id,
        task_name=task.name,
        result=str(retval)[:200] if retval else None,
    )


@task_failure.connect
def task_failure_handler(
    sender=None,
    task_id=None,
    exception=None,
    args=None,
    kwargs=None,
    traceback=None,
    einfo=None,
    **extra,
):
    """任务失败时的钩子"""
    logger.error(
        "task_failed",
        task_id=task_id,
        task_name=sender.name if sender else None,
        exception=str(exception),
        args=args,
        kwargs=kwargs,
    )
