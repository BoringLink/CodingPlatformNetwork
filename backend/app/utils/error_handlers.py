"""错误处理器

提供全局异常处理、重试机制和降级策略
"""

import asyncio
import time
from functools import wraps
from typing import Any, Callable, Optional, Type, TypeVar, Union
import structlog

from app.utils.exceptions import (
    BaseAppException,
    LLMServiceError,
    LLMTimeoutError,
    LLMQuotaExceededError,
    DatabaseConnectionError,
    DatabaseQueryTimeoutError,
    CacheError,
)

logger = structlog.get_logger(__name__)

T = TypeVar('T')


class RetryConfig:
    """重试配置"""
    
    def __init__(
        self,
        max_retries: int = 3,
        initial_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        jitter: bool = True,
    ):
        """初始化重试配置
        
        Args:
            max_retries: 最大重试次数
            initial_delay: 初始延迟（秒）
            max_delay: 最大延迟（秒）
            exponential_base: 指数退避基数
            jitter: 是否添加随机抖动
        """
        self.max_retries = max_retries
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter
    
    def calculate_delay(self, attempt: int) -> float:
        """计算延迟时间
        
        使用指数退避算法计算延迟时间
        
        Args:
            attempt: 当前尝试次数（从0开始）
        
        Returns:
            延迟时间（秒）
        """
        import random
        
        # 指数退避
        delay = min(
            self.initial_delay * (self.exponential_base ** attempt),
            self.max_delay,
        )
        
        # 添加随机抖动（避免雷鸣群效应）
        if self.jitter:
            delay = delay * (0.5 + random.random() * 0.5)
        
        return delay


def retry_on_exception(
    exceptions: Union[Type[Exception], tuple[Type[Exception], ...]] = Exception,
    config: Optional[RetryConfig] = None,
    on_retry: Optional[Callable[[Exception, int], None]] = None,
) -> Callable:
    """重试装饰器
    
    在指定异常发生时自动重试函数调用
    
    Args:
        exceptions: 需要重试的异常类型
        config: 重试配置
        on_retry: 重试时的回调函数
    
    Returns:
        装饰器函数
    
    Example:
        @retry_on_exception(
            exceptions=(LLMServiceError, DatabaseConnectionError),
            config=RetryConfig(max_retries=3, initial_delay=1.0),
        )
        async def call_llm_api():
            ...
    """
    if config is None:
        config = RetryConfig()
    
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def async_wrapper(*args, **kwargs) -> T:
            last_exception = None
            
            for attempt in range(config.max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                
                except exceptions as e:
                    last_exception = e
                    
                    # 如果是最后一次尝试，直接抛出异常
                    if attempt >= config.max_retries:
                        logger.error(
                            "retry_exhausted",
                            function=func.__name__,
                            attempt=attempt + 1,
                            max_retries=config.max_retries,
                            error=str(e),
                        )
                        raise
                    
                    # 计算延迟时间
                    delay = config.calculate_delay(attempt)
                    
                    logger.warning(
                        "retry_attempt",
                        function=func.__name__,
                        attempt=attempt + 1,
                        max_retries=config.max_retries,
                        delay=delay,
                        error=str(e),
                    )
                    
                    # 调用重试回调
                    if on_retry:
                        on_retry(e, attempt + 1)
                    
                    # 等待后重试
                    await asyncio.sleep(delay)
            
            # 理论上不会到达这里
            raise last_exception
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs) -> T:
            last_exception = None
            
            for attempt in range(config.max_retries + 1):
                try:
                    return func(*args, **kwargs)
                
                except exceptions as e:
                    last_exception = e
                    
                    # 如果是最后一次尝试，直接抛出异常
                    if attempt >= config.max_retries:
                        logger.error(
                            "retry_exhausted",
                            function=func.__name__,
                            attempt=attempt + 1,
                            max_retries=config.max_retries,
                            error=str(e),
                        )
                        raise
                    
                    # 计算延迟时间
                    delay = config.calculate_delay(attempt)
                    
                    logger.warning(
                        "retry_attempt",
                        function=func.__name__,
                        attempt=attempt + 1,
                        max_retries=config.max_retries,
                        delay=delay,
                        error=str(e),
                    )
                    
                    # 调用重试回调
                    if on_retry:
                        on_retry(e, attempt + 1)
                    
                    # 等待后重试
                    time.sleep(delay)
            
            # 理论上不会到达这里
            raise last_exception
        
        # 根据函数类型返回相应的包装器
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


class CircuitBreaker:
    """断路器
    
    实现断路器模式，在连续失败超过阈值时暂停调用
    """
    
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
        expected_exception: Type[Exception] = Exception,
    ):
        """初始化断路器
        
        Args:
            failure_threshold: 失败阈值
            recovery_timeout: 恢复超时时间（秒）
            expected_exception: 预期的异常类型
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        
        self.failure_count = 0
        self.last_failure_time: Optional[float] = None
        self.state = "closed"  # closed, open, half_open
    
    def call(self, func: Callable[..., T], *args, **kwargs) -> T:
        """调用函数（带断路器保护）
        
        Args:
            func: 要调用的函数
            *args: 位置参数
            **kwargs: 关键字参数
        
        Returns:
            函数返回值
        
        Raises:
            Exception: 如果断路器打开或函数调用失败
        """
        # 检查断路器状态
        if self.state == "open":
            # 检查是否可以尝试恢复
            if self.last_failure_time and \
               time.time() - self.last_failure_time >= self.recovery_timeout:
                logger.info(
                    "circuit_breaker_half_open",
                    function=func.__name__,
                )
                self.state = "half_open"
            else:
                logger.warning(
                    "circuit_breaker_open",
                    function=func.__name__,
                    failure_count=self.failure_count,
                )
                raise Exception("Circuit breaker is open")
        
        try:
            result = func(*args, **kwargs)
            
            # 调用成功，重置失败计数
            if self.state == "half_open":
                logger.info(
                    "circuit_breaker_closed",
                    function=func.__name__,
                )
                self.state = "closed"
                self.failure_count = 0
                self.last_failure_time = None
            
            return result
        
        except self.expected_exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()
            
            logger.warning(
                "circuit_breaker_failure",
                function=func.__name__,
                failure_count=self.failure_count,
                threshold=self.failure_threshold,
            )
            
            # 检查是否达到失败阈值
            if self.failure_count >= self.failure_threshold:
                logger.error(
                    "circuit_breaker_opened",
                    function=func.__name__,
                    failure_count=self.failure_count,
                )
                self.state = "open"
            
            raise
    
    async def call_async(self, func: Callable[..., T], *args, **kwargs) -> T:
        """异步调用函数（带断路器保护）
        
        Args:
            func: 要调用的异步函数
            *args: 位置参数
            **kwargs: 关键字参数
        
        Returns:
            函数返回值
        
        Raises:
            Exception: 如果断路器打开或函数调用失败
        """
        # 检查断路器状态
        if self.state == "open":
            # 检查是否可以尝试恢复
            if self.last_failure_time and \
               time.time() - self.last_failure_time >= self.recovery_timeout:
                logger.info(
                    "circuit_breaker_half_open",
                    function=func.__name__,
                )
                self.state = "half_open"
            else:
                logger.warning(
                    "circuit_breaker_open",
                    function=func.__name__,
                    failure_count=self.failure_count,
                )
                raise Exception("Circuit breaker is open")
        
        try:
            result = await func(*args, **kwargs)
            
            # 调用成功，重置失败计数
            if self.state == "half_open":
                logger.info(
                    "circuit_breaker_closed",
                    function=func.__name__,
                )
                self.state = "closed"
                self.failure_count = 0
                self.last_failure_time = None
            
            return result
        
        except self.expected_exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()
            
            logger.warning(
                "circuit_breaker_failure",
                function=func.__name__,
                failure_count=self.failure_count,
                threshold=self.failure_threshold,
            )
            
            # 检查是否达到失败阈值
            if self.failure_count >= self.failure_threshold:
                logger.error(
                    "circuit_breaker_opened",
                    function=func.__name__,
                    failure_count=self.failure_count,
                )
                self.state = "open"
            
            raise


class FallbackHandler:
    """降级处理器
    
    提供服务降级策略
    """
    
    @staticmethod
    async def llm_fallback(
        error: Exception,
        input_text: str,
        analysis_type: str,
    ) -> Optional[dict]:
        """LLM服务降级策略
        
        当LLM服务不可用时，使用基于规则的备用分析方法
        
        Args:
            error: 原始错误
            input_text: 输入文本
            analysis_type: 分析类型
        
        Returns:
            降级分析结果，如果无法降级则返回 None
        """
        logger.warning(
            "llm_fallback_triggered",
            analysis_type=analysis_type,
            error=str(error),
        )
        
        # 简单的基于规则的分析
        if analysis_type == "interaction":
            # 情感分析降级：基于关键词
            positive_keywords = ["好", "棒", "谢谢", "感谢", "赞", "优秀"]
            negative_keywords = ["不", "差", "错", "难", "问题", "失败"]
            
            sentiment = "neutral"
            for keyword in positive_keywords:
                if keyword in input_text:
                    sentiment = "positive"
                    break
            
            for keyword in negative_keywords:
                if keyword in input_text:
                    sentiment = "negative"
                    break
            
            return {
                "sentiment": sentiment,
                "topics": ["未分析"],
                "confidence": 0.3,  # 低置信度
                "fallback": True,
            }
        
        elif analysis_type == "error":
            # 错误分析降级：返回通用结果
            return {
                "error_type": "未分类错误",
                "related_knowledge_points": ["需要人工审核"],
                "difficulty": "medium",
                "confidence": 0.2,  # 低置信度
                "fallback": True,
            }
        
        elif analysis_type == "knowledge_extraction":
            # 知识点提取降级：返回空列表
            return {
                "knowledge_points": [],
                "fallback": True,
            }
        
        return None
    
    @staticmethod
    async def cache_fallback(
        error: Exception,
        operation: str,
    ) -> None:
        """缓存服务降级策略
        
        当缓存服务不可用时，记录日志但不影响主流程
        
        Args:
            error: 原始错误
            operation: 操作类型
        """
        logger.warning(
            "cache_fallback_triggered",
            operation=operation,
            error=str(error),
            message="Continuing without cache",
        )
    
    @staticmethod
    async def database_fallback(
        error: Exception,
        operation: str,
        data: Optional[dict] = None,
    ) -> None:
        """数据库服务降级策略
        
        当图数据库不可用时，将数据缓存到消息队列
        
        Args:
            error: 原始错误
            operation: 操作类型
            data: 要缓存的数据
        """
        logger.error(
            "database_fallback_triggered",
            operation=operation,
            error=str(error),
            message="Data will be queued for later processing",
        )
        
        # TODO: 实现将数据发送到消息队列的逻辑
        # 这里可以使用 Celery 或 Redis 队列
        pass


def handle_exception_gracefully(
    fallback_value: Optional[Any] = None,
    log_level: str = "error",
) -> Callable:
    """优雅处理异常装饰器
    
    捕获异常并返回降级值，而不是让异常传播
    
    Args:
        fallback_value: 发生异常时返回的降级值
        log_level: 日志级别
    
    Returns:
        装饰器函数
    
    Example:
        @handle_exception_gracefully(fallback_value={})
        async def get_user_data(user_id: str):
            ...
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def async_wrapper(*args, **kwargs) -> T:
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                log_func = getattr(logger, log_level, logger.error)
                log_func(
                    "exception_handled_gracefully",
                    function=func.__name__,
                    error=str(e),
                    error_type=type(e).__name__,
                    fallback_value=fallback_value,
                )
                return fallback_value
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs) -> T:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                log_func = getattr(logger, log_level, logger.error)
                log_func(
                    "exception_handled_gracefully",
                    function=func.__name__,
                    error=str(e),
                    error_type=type(e).__name__,
                    fallback_value=fallback_value,
                )
                return fallback_value
        
        # 根据函数类型返回相应的包装器
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


def log_operation(
    operation_name: str,
    include_args: bool = False,
    include_result: bool = False,
) -> Callable:
    """操作日志装饰器
    
    自动记录函数调用的开始、结束和错误
    
    Args:
        operation_name: 操作名称
        include_args: 是否包含参数
        include_result: 是否包含返回值
    
    Returns:
        装饰器函数
    
    Example:
        @log_operation("create_node", include_args=True)
        async def create_node(node_type, properties):
            ...
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def async_wrapper(*args, **kwargs) -> T:
            start_time = time.time()
            
            log_data = {
                "operation": operation_name,
                "function": func.__name__,
            }
            
            if include_args:
                log_data["args"] = str(args)[:200]
                log_data["kwargs"] = str(kwargs)[:200]
            
            logger.info("operation_started", **log_data)
            
            try:
                result = await func(*args, **kwargs)
                
                elapsed_time = time.time() - start_time
                log_data["elapsed_time"] = f"{elapsed_time:.3f}s"
                log_data["status"] = "success"
                
                if include_result:
                    log_data["result"] = str(result)[:200]
                
                logger.info("operation_completed", **log_data)
                
                return result
            
            except Exception as e:
                elapsed_time = time.time() - start_time
                log_data["elapsed_time"] = f"{elapsed_time:.3f}s"
                log_data["status"] = "failed"
                log_data["error"] = str(e)
                log_data["error_type"] = type(e).__name__
                
                logger.error("operation_failed", **log_data)
                
                raise
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs) -> T:
            start_time = time.time()
            
            log_data = {
                "operation": operation_name,
                "function": func.__name__,
            }
            
            if include_args:
                log_data["args"] = str(args)[:200]
                log_data["kwargs"] = str(kwargs)[:200]
            
            logger.info("operation_started", **log_data)
            
            try:
                result = func(*args, **kwargs)
                
                elapsed_time = time.time() - start_time
                log_data["elapsed_time"] = f"{elapsed_time:.3f}s"
                log_data["status"] = "success"
                
                if include_result:
                    log_data["result"] = str(result)[:200]
                
                logger.info("operation_completed", **log_data)
                
                return result
            
            except Exception as e:
                elapsed_time = time.time() - start_time
                log_data["elapsed_time"] = f"{elapsed_time:.3f}s"
                log_data["status"] = "failed"
                log_data["error"] = str(e)
                log_data["error_type"] = type(e).__name__
                
                logger.error("operation_failed", **log_data)
                
                raise
        
        # 根据函数类型返回相应的包装器
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator
