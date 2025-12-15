"""LLM分析异步任务

本模块实现LLM分析的异步任务，支持：
- 互动内容分析
- 错误记录分析
- 知识点提取
- 批量分析
- 速率限制
"""

from typing import Any, Dict, List, Optional
import structlog

from celery import Task, group
from celery.exceptions import Reject

from app.celery_app import celery_app

logger = structlog.get_logger(__name__)


class LLMAnalysisTask(Task):
    """LLM分析任务基类
    
    提供自动重试、错误处理和速率限制功能
    """
    
    autoretry_for = (Exception,)
    retry_kwargs = {"max_retries": 3}
    retry_backoff = True  # 指数退避
    retry_backoff_max = 600  # 最大退避时间10分钟
    retry_jitter = True  # 添加随机抖动
    
    # 速率限制：每分钟100个请求（符合需求7.2）
    rate_limit = "100/m"
    
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """任务失败时的回调"""
        logger.error(
            "llm_analysis_task_failed",
            task_id=task_id,
            exception=str(exc),
            args=args,
            kwargs=kwargs,
        )
        super().on_failure(exc, task_id, args, kwargs, einfo)
    
    def on_retry(self, exc, task_id, args, kwargs, einfo):
        """任务重试时的回调"""
        logger.warning(
            "llm_analysis_task_retry",
            task_id=task_id,
            exception=str(exc),
            retry_count=self.request.retries,
        )
        super().on_retry(exc, task_id, args, kwargs, einfo)


@celery_app.task(
    base=LLMAnalysisTask,
    name="app.tasks.llm_analysis.analyze_interaction_task",
    bind=True,
    queue="llm_analysis",
)
def analyze_interaction_task(
    self,
    text: str,
    interaction_id: str,
) -> Dict[str, Any]:
    """分析互动内容任务
    
    异步分析学生互动或师生互动内容
    
    Args:
        self: 任务实例
        text: 互动内容文本
        interaction_id: 互动记录ID
    
    Returns:
        分析结果字典
    
    Raises:
        Reject: 如果输入无效（不重试）
    """
    logger.info(
        "analyze_interaction_task_started",
        task_id=self.request.id,
        interaction_id=interaction_id,
        text_length=len(text),
    )
    
    if not text or not text.strip():
        logger.error(
            "invalid_interaction_text",
            task_id=self.request.id,
            interaction_id=interaction_id,
        )
        raise Reject("Interaction text cannot be empty", requeue=False)
    
    try:
        # 导入LLM服务
        from app.services.llm_service import get_llm_service
        
        llm_service = get_llm_service()
        
        # 执行分析（异步函数需要在同步上下文中运行）
        import asyncio
        analysis = asyncio.run(llm_service.analyze_interaction(text))
        
        result = {
            "task_id": self.request.id,
            "interaction_id": interaction_id,
            "sentiment": analysis.sentiment.value,
            "topics": analysis.topics,
            "confidence": analysis.confidence,
        }
        
        logger.info(
            "analyze_interaction_task_completed",
            task_id=self.request.id,
            interaction_id=interaction_id,
            sentiment=analysis.sentiment.value,
            topics_count=len(analysis.topics),
        )
        
        return result
    
    except Reject:
        raise
    except Exception as e:
        logger.error(
            "analyze_interaction_task_error",
            task_id=self.request.id,
            interaction_id=interaction_id,
            error=str(e),
        )
        raise


@celery_app.task(
    base=LLMAnalysisTask,
    name="app.tasks.llm_analysis.analyze_error_task",
    bind=True,
    queue="llm_analysis",
)
def analyze_error_task(
    self,
    error_text: str,
    error_id: str,
    course_id: str,
    course_name: str,
    course_description: Optional[str] = None,
) -> Dict[str, Any]:
    """分析错误记录任务
    
    异步分析学生错误记录，识别错误类型和相关知识点
    
    Args:
        self: 任务实例
        error_text: 错误记录文本
        error_id: 错误记录ID
        course_id: 课程ID
        course_name: 课程名称
        course_description: 课程描述（可选）
    
    Returns:
        分析结果字典
    
    Raises:
        Reject: 如果输入无效（不重试）
    """
    logger.info(
        "analyze_error_task_started",
        task_id=self.request.id,
        error_id=error_id,
        course_id=course_id,
        error_text_length=len(error_text),
    )
    
    if not error_text or not error_text.strip():
        logger.error(
            "invalid_error_text",
            task_id=self.request.id,
            error_id=error_id,
        )
        raise Reject("Error text cannot be empty", requeue=False)
    
    try:
        # 导入LLM服务
        from app.services.llm_service import get_llm_service, CourseContext
        
        llm_service = get_llm_service()
        
        # 创建课程上下文
        context = CourseContext(
            course_id=course_id,
            course_name=course_name,
            description=course_description,
        )
        
        # 执行分析
        import asyncio
        analysis = asyncio.run(llm_service.analyze_error(error_text, context))
        
        result = {
            "task_id": self.request.id,
            "error_id": error_id,
            "course_id": course_id,
            "error_type": analysis.error_type,
            "related_knowledge_points": analysis.related_knowledge_points,
            "difficulty": analysis.difficulty.value,
            "confidence": analysis.confidence,
        }
        
        logger.info(
            "analyze_error_task_completed",
            task_id=self.request.id,
            error_id=error_id,
            error_type=analysis.error_type,
            knowledge_points_count=len(analysis.related_knowledge_points),
        )
        
        return result
    
    except Reject:
        raise
    except Exception as e:
        logger.error(
            "analyze_error_task_error",
            task_id=self.request.id,
            error_id=error_id,
            error=str(e),
        )
        raise


@celery_app.task(
    base=LLMAnalysisTask,
    name="app.tasks.llm_analysis.extract_knowledge_points_task",
    bind=True,
    queue="llm_analysis",
)
def extract_knowledge_points_task(
    self,
    course_content: str,
    course_id: str,
) -> Dict[str, Any]:
    """提取知识点任务
    
    异步从课程内容中提取知识点
    
    Args:
        self: 任务实例
        course_content: 课程内容文本
        course_id: 课程ID
    
    Returns:
        提取结果字典
    
    Raises:
        Reject: 如果输入无效（不重试）
    """
    logger.info(
        "extract_knowledge_points_task_started",
        task_id=self.request.id,
        course_id=course_id,
        content_length=len(course_content),
    )
    
    if not course_content or not course_content.strip():
        logger.error(
            "invalid_course_content",
            task_id=self.request.id,
            course_id=course_id,
        )
        raise Reject("Course content cannot be empty", requeue=False)
    
    try:
        # 导入LLM服务
        from app.services.llm_service import get_llm_service
        
        llm_service = get_llm_service()
        
        # 执行提取
        import asyncio
        knowledge_points = asyncio.run(
            llm_service.extract_knowledge_points(course_content)
        )
        
        result = {
            "task_id": self.request.id,
            "course_id": course_id,
            "knowledge_points": [
                {
                    "id": kp.id,
                    "name": kp.name,
                    "description": kp.description,
                    "dependencies": kp.dependencies,
                }
                for kp in knowledge_points
            ],
        }
        
        logger.info(
            "extract_knowledge_points_task_completed",
            task_id=self.request.id,
            course_id=course_id,
            knowledge_points_count=len(knowledge_points),
        )
        
        return result
    
    except Reject:
        raise
    except Exception as e:
        logger.error(
            "extract_knowledge_points_task_error",
            task_id=self.request.id,
            course_id=course_id,
            error=str(e),
        )
        raise


@celery_app.task(
    name="app.tasks.llm_analysis.batch_analyze_interactions_task",
    queue="llm_analysis",
)
def batch_analyze_interactions_task(
    interactions: List[Dict[str, str]],
) -> str:
    """批量分析互动内容
    
    并行分析多个互动内容
    
    Args:
        interactions: 互动列表，每个包含 text 和 interaction_id
    
    Returns:
        任务组ID
    """
    logger.info(
        "batch_analyze_interactions_started",
        interactions_count=len(interactions),
    )
    
    # 创建任务组
    job = group(
        analyze_interaction_task.s(
            text=interaction["text"],
            interaction_id=interaction["interaction_id"],
        )
        for interaction in interactions
    )
    
    # 执行任务组
    result = job.apply_async()
    
    logger.info(
        "batch_analyze_interactions_dispatched",
        group_id=result.id,
        interactions_count=len(interactions),
    )
    
    return result.id


@celery_app.task(
    name="app.tasks.llm_analysis.batch_analyze_errors_task",
    queue="llm_analysis",
)
def batch_analyze_errors_task(
    errors: List[Dict[str, Any]],
) -> str:
    """批量分析错误记录
    
    并行分析多个错误记录
    
    Args:
        errors: 错误列表，每个包含 error_text, error_id, course_id, course_name
    
    Returns:
        任务组ID
    """
    logger.info(
        "batch_analyze_errors_started",
        errors_count=len(errors),
    )
    
    # 创建任务组
    job = group(
        analyze_error_task.s(
            error_text=error["error_text"],
            error_id=error["error_id"],
            course_id=error["course_id"],
            course_name=error["course_name"],
            course_description=error.get("course_description"),
        )
        for error in errors
    )
    
    # 执行任务组
    result = job.apply_async()
    
    logger.info(
        "batch_analyze_errors_dispatched",
        group_id=result.id,
        errors_count=len(errors),
    )
    
    return result.id
