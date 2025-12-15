"""自定义异常类

定义系统中使用的所有自定义异常类型
"""

from typing import Any, Dict, Optional


class BaseAppException(Exception):
    """应用基础异常类
    
    所有自定义异常的基类
    """
    
    def __init__(
        self,
        message: str,
        error_code: str,
        details: Optional[Dict[str, Any]] = None,
        original_error: Optional[Exception] = None,
    ):
        """初始化异常
        
        Args:
            message: 错误消息
            error_code: 错误代码
            details: 错误详情
            original_error: 原始异常
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        self.original_error = original_error
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        result = {
            "error": self.__class__.__name__,
            "message": self.message,
            "error_code": self.error_code,
            "details": self.details,
        }
        
        if self.original_error:
            result["original_error"] = str(self.original_error)
        
        return result


# 数据验证错误
class DataValidationError(BaseAppException):
    """数据验证错误
    
    当输入数据格式不正确或缺少必需字段时抛出
    """
    
    def __init__(
        self,
        message: str,
        field_name: Optional[str] = None,
        expected_format: Optional[str] = None,
        actual_value: Optional[Any] = None,
        original_error: Optional[Exception] = None,
    ):
        details = {}
        if field_name:
            details["field_name"] = field_name
        if expected_format:
            details["expected_format"] = expected_format
        if actual_value is not None:
            details["actual_value"] = str(actual_value)
        
        super().__init__(
            message=message,
            error_code="DATA_VALIDATION_ERROR",
            details=details,
            original_error=original_error,
        )


# LLM服务错误
class LLMServiceError(BaseAppException):
    """LLM服务错误
    
    当大语言模型API调用失败时抛出
    """
    
    def __init__(
        self,
        message: str,
        model: Optional[str] = None,
        retry_count: Optional[int] = None,
        original_error: Optional[Exception] = None,
    ):
        details = {}
        if model:
            details["model"] = model
        if retry_count is not None:
            details["retry_count"] = retry_count
        
        super().__init__(
            message=message,
            error_code="LLM_SERVICE_ERROR",
            details=details,
            original_error=original_error,
        )


class LLMTimeoutError(LLMServiceError):
    """LLM超时错误"""
    
    def __init__(
        self,
        message: str = "LLM request timed out",
        model: Optional[str] = None,
        timeout: Optional[float] = None,
        original_error: Optional[Exception] = None,
    ):
        details = {}
        if model:
            details["model"] = model
        if timeout is not None:
            details["timeout"] = timeout
        
        super().__init__(
            message=message,
            model=model,
            original_error=original_error,
        )
        self.error_code = "LLM_TIMEOUT"
        self.details.update(details)


class LLMQuotaExceededError(LLMServiceError):
    """LLM配额超限错误"""
    
    def __init__(
        self,
        message: str = "LLM API quota exceeded",
        model: Optional[str] = None,
        original_error: Optional[Exception] = None,
    ):
        super().__init__(
            message=message,
            model=model,
            original_error=original_error,
        )
        self.error_code = "LLM_QUOTA_EXCEEDED"


class LLMParseError(LLMServiceError):
    """LLM响应解析错误"""
    
    def __init__(
        self,
        message: str,
        response_text: Optional[str] = None,
        expected_fields: Optional[list] = None,
        original_error: Optional[Exception] = None,
    ):
        details = {}
        if response_text:
            # 只保留前500个字符避免日志过大
            details["response_text"] = response_text[:500]
        if expected_fields:
            details["expected_fields"] = expected_fields
        
        super().__init__(
            message=message,
            original_error=original_error,
        )
        self.error_code = "LLM_PARSE_ERROR"
        self.details.update(details)


# 图数据库错误
class DatabaseError(BaseAppException):
    """数据库错误基类"""
    
    def __init__(
        self,
        message: str,
        error_code: str = "DB_ERROR",
        query: Optional[str] = None,
        original_error: Optional[Exception] = None,
    ):
        details = {}
        if query:
            # 只保留前500个字符
            details["query"] = query[:500]
        
        super().__init__(
            message=message,
            error_code=error_code,
            details=details,
            original_error=original_error,
        )


class DatabaseConnectionError(DatabaseError):
    """数据库连接错误"""
    
    def __init__(
        self,
        message: str = "Failed to connect to database",
        original_error: Optional[Exception] = None,
    ):
        super().__init__(
            message=message,
            error_code="DB_CONNECTION_ERROR",
            original_error=original_error,
        )


class DatabaseQueryTimeoutError(DatabaseError):
    """数据库查询超时错误"""
    
    def __init__(
        self,
        message: str = "Database query timed out",
        query: Optional[str] = None,
        timeout: Optional[float] = None,
        original_error: Optional[Exception] = None,
    ):
        super().__init__(
            message=message,
            error_code="DB_QUERY_TIMEOUT",
            query=query,
            original_error=original_error,
        )
        if timeout is not None:
            self.details["timeout"] = timeout


class DatabaseConstraintViolationError(DatabaseError):
    """数据库约束违反错误"""
    
    def __init__(
        self,
        message: str,
        constraint_name: Optional[str] = None,
        original_error: Optional[Exception] = None,
    ):
        super().__init__(
            message=message,
            error_code="DB_CONSTRAINT_VIOLATION",
            original_error=original_error,
        )
        if constraint_name:
            self.details["constraint_name"] = constraint_name


# 数据冲突错误
class DataConflictError(BaseAppException):
    """数据冲突错误
    
    当同一实体的数据在不同时间点有不同的值时抛出
    """
    
    def __init__(
        self,
        message: str,
        entity_id: Optional[str] = None,
        field_name: Optional[str] = None,
        existing_value: Optional[Any] = None,
        new_value: Optional[Any] = None,
        original_error: Optional[Exception] = None,
    ):
        details = {}
        if entity_id:
            details["entity_id"] = entity_id
        if field_name:
            details["field_name"] = field_name
        if existing_value is not None:
            details["existing_value"] = str(existing_value)
        if new_value is not None:
            details["new_value"] = str(new_value)
        
        super().__init__(
            message=message,
            error_code="DATA_CONFLICT",
            details=details,
            original_error=original_error,
        )


# 资源限制错误
class ResourceLimitError(BaseAppException):
    """资源限制错误
    
    当内存、磁盘空间或处理队列满时抛出
    """
    
    def __init__(
        self,
        message: str,
        resource_type: Optional[str] = None,
        current_usage: Optional[Any] = None,
        limit: Optional[Any] = None,
        original_error: Optional[Exception] = None,
    ):
        details = {}
        if resource_type:
            details["resource_type"] = resource_type
        if current_usage is not None:
            details["current_usage"] = str(current_usage)
        if limit is not None:
            details["limit"] = str(limit)
        
        super().__init__(
            message=message,
            error_code="RESOURCE_LIMIT_EXCEEDED",
            details=details,
            original_error=original_error,
        )


class QueueFullError(ResourceLimitError):
    """队列满错误"""
    
    def __init__(
        self,
        message: str = "Processing queue is full",
        queue_name: Optional[str] = None,
        queue_size: Optional[int] = None,
        original_error: Optional[Exception] = None,
    ):
        super().__init__(
            message=message,
            resource_type="queue",
            original_error=original_error,
        )
        self.error_code = "QUEUE_FULL"
        if queue_name:
            self.details["queue_name"] = queue_name
        if queue_size is not None:
            self.details["queue_size"] = queue_size


# 节点/关系不存在错误
class NodeNotFoundError(BaseAppException):
    """节点不存在错误"""
    
    def __init__(
        self,
        message: str,
        node_id: Optional[str] = None,
        node_type: Optional[str] = None,
        original_error: Optional[Exception] = None,
    ):
        details = {}
        if node_id:
            details["node_id"] = node_id
        if node_type:
            details["node_type"] = node_type
        
        super().__init__(
            message=message,
            error_code="NODE_NOT_FOUND",
            details=details,
            original_error=original_error,
        )


class RelationshipNotFoundError(BaseAppException):
    """关系不存在错误"""
    
    def __init__(
        self,
        message: str,
        relationship_id: Optional[str] = None,
        relationship_type: Optional[str] = None,
        original_error: Optional[Exception] = None,
    ):
        details = {}
        if relationship_id:
            details["relationship_id"] = relationship_id
        if relationship_type:
            details["relationship_type"] = relationship_type
        
        super().__init__(
            message=message,
            error_code="RELATIONSHIP_NOT_FOUND",
            details=details,
            original_error=original_error,
        )


# 缓存错误
class CacheError(BaseAppException):
    """缓存错误"""
    
    def __init__(
        self,
        message: str,
        cache_key: Optional[str] = None,
        operation: Optional[str] = None,
        original_error: Optional[Exception] = None,
    ):
        details = {}
        if cache_key:
            details["cache_key"] = cache_key
        if operation:
            details["operation"] = operation
        
        super().__init__(
            message=message,
            error_code="CACHE_ERROR",
            details=details,
            original_error=original_error,
        )


# 配置错误
class ConfigurationError(BaseAppException):
    """配置错误"""
    
    def __init__(
        self,
        message: str,
        config_key: Optional[str] = None,
        original_error: Optional[Exception] = None,
    ):
        details = {}
        if config_key:
            details["config_key"] = config_key
        
        super().__init__(
            message=message,
            error_code="CONFIGURATION_ERROR",
            details=details,
            original_error=original_error,
        )
