"""审计日志

记录系统中的关键操作，用于审计和追踪
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional
from uuid import uuid4
import structlog

logger = structlog.get_logger(__name__)


class OperationType(str, Enum):
    """操作类型枚举"""
    
    # 节点操作
    NODE_CREATE = "node_create"
    NODE_UPDATE = "node_update"
    NODE_DELETE = "node_delete"
    NODE_MERGE = "node_merge"
    
    # 关系操作
    RELATIONSHIP_CREATE = "relationship_create"
    RELATIONSHIP_UPDATE = "relationship_update"
    RELATIONSHIP_DELETE = "relationship_delete"
    
    # 数据导入操作
    DATA_IMPORT_START = "data_import_start"
    DATA_IMPORT_COMPLETE = "data_import_complete"
    DATA_IMPORT_FAILED = "data_import_failed"
    
    # LLM操作
    LLM_ANALYSIS = "llm_analysis"
    LLM_RETRY = "llm_retry"
    LLM_FALLBACK = "llm_fallback"
    
    # 查询操作
    QUERY_EXECUTE = "query_execute"
    SUBGRAPH_QUERY = "subgraph_query"
    
    # 缓存操作
    CACHE_HIT = "cache_hit"
    CACHE_MISS = "cache_miss"
    CACHE_SET = "cache_set"
    CACHE_CLEAR = "cache_clear"
    
    # 系统操作
    SYSTEM_START = "system_start"
    SYSTEM_SHUTDOWN = "system_shutdown"
    SYSTEM_ERROR = "system_error"


class AuditLog:
    """审计日志记录器"""
    
    @staticmethod
    def log_operation(
        operation_type: OperationType,
        user_id: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        status: str = "success",
        error_message: Optional[str] = None,
    ) -> str:
        """记录操作日志
        
        Args:
            operation_type: 操作类型
            user_id: 用户ID（如果适用）
            resource_type: 资源类型（如节点类型、关系类型）
            resource_id: 资源ID
            details: 操作详情
            status: 操作状态（success, failed, pending）
            error_message: 错误消息（如果失败）
        
        Returns:
            审计日志ID
        """
        audit_id = str(uuid4())
        timestamp = datetime.utcnow()
        
        log_data = {
            "audit_id": audit_id,
            "timestamp": timestamp.isoformat(),
            "operation_type": operation_type.value,
            "status": status,
        }
        
        if user_id:
            log_data["user_id"] = user_id
        
        if resource_type:
            log_data["resource_type"] = resource_type
        
        if resource_id:
            log_data["resource_id"] = resource_id
        
        if details:
            log_data["details"] = details
        
        if error_message:
            log_data["error_message"] = error_message
        
        # 记录到结构化日志
        logger.info("audit_log", **log_data)
        
        return audit_id
    
    @staticmethod
    def log_node_operation(
        operation: OperationType,
        node_type: str,
        node_id: str,
        properties: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None,
        status: str = "success",
        error_message: Optional[str] = None,
    ) -> str:
        """记录节点操作
        
        Args:
            operation: 操作类型
            node_type: 节点类型
            node_id: 节点ID
            properties: 节点属性
            user_id: 用户ID
            status: 操作状态
            error_message: 错误消息
        
        Returns:
            审计日志ID
        """
        details = {
            "node_type": node_type,
        }
        
        if properties:
            # 只记录关键属性，避免日志过大
            details["properties_count"] = len(properties)
            details["property_keys"] = list(properties.keys())
        
        return AuditLog.log_operation(
            operation_type=operation,
            user_id=user_id,
            resource_type="node",
            resource_id=node_id,
            details=details,
            status=status,
            error_message=error_message,
        )
    
    @staticmethod
    def log_relationship_operation(
        operation: OperationType,
        relationship_type: str,
        relationship_id: str,
        from_node_id: str,
        to_node_id: str,
        properties: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None,
        status: str = "success",
        error_message: Optional[str] = None,
    ) -> str:
        """记录关系操作
        
        Args:
            operation: 操作类型
            relationship_type: 关系类型
            relationship_id: 关系ID
            from_node_id: 起始节点ID
            to_node_id: 目标节点ID
            properties: 关系属性
            user_id: 用户ID
            status: 操作状态
            error_message: 错误消息
        
        Returns:
            审计日志ID
        """
        details = {
            "relationship_type": relationship_type,
            "from_node_id": from_node_id,
            "to_node_id": to_node_id,
        }
        
        if properties:
            details["properties_count"] = len(properties)
            details["property_keys"] = list(properties.keys())
        
        return AuditLog.log_operation(
            operation_type=operation,
            user_id=user_id,
            resource_type="relationship",
            resource_id=relationship_id,
            details=details,
            status=status,
            error_message=error_message,
        )
    
    @staticmethod
    def log_llm_operation(
        model: str,
        analysis_type: str,
        input_length: int,
        output_length: Optional[int] = None,
        cache_hit: bool = False,
        retry_count: int = 0,
        fallback_used: bool = False,
        status: str = "success",
        error_message: Optional[str] = None,
    ) -> str:
        """记录LLM操作
        
        Args:
            model: 模型名称
            analysis_type: 分析类型
            input_length: 输入长度
            output_length: 输出长度
            cache_hit: 是否命中缓存
            retry_count: 重试次数
            fallback_used: 是否使用降级策略
            status: 操作状态
            error_message: 错误消息
        
        Returns:
            审计日志ID
        """
        details = {
            "model": model,
            "analysis_type": analysis_type,
            "input_length": input_length,
            "cache_hit": cache_hit,
            "retry_count": retry_count,
            "fallback_used": fallback_used,
        }
        
        if output_length is not None:
            details["output_length"] = output_length
        
        return AuditLog.log_operation(
            operation_type=OperationType.LLM_ANALYSIS,
            resource_type="llm",
            details=details,
            status=status,
            error_message=error_message,
        )
    
    @staticmethod
    def log_data_import(
        import_id: str,
        total_records: int,
        successful_records: Optional[int] = None,
        failed_records: Optional[int] = None,
        status: str = "started",
        error_message: Optional[str] = None,
    ) -> str:
        """记录数据导入操作
        
        Args:
            import_id: 导入ID
            total_records: 总记录数
            successful_records: 成功记录数
            failed_records: 失败记录数
            status: 操作状态
            error_message: 错误消息
        
        Returns:
            审计日志ID
        """
        details = {
            "total_records": total_records,
        }
        
        if successful_records is not None:
            details["successful_records"] = successful_records
        
        if failed_records is not None:
            details["failed_records"] = failed_records
        
        operation_type = OperationType.DATA_IMPORT_START
        if status == "completed":
            operation_type = OperationType.DATA_IMPORT_COMPLETE
        elif status == "failed":
            operation_type = OperationType.DATA_IMPORT_FAILED
        
        return AuditLog.log_operation(
            operation_type=operation_type,
            resource_type="data_import",
            resource_id=import_id,
            details=details,
            status=status,
            error_message=error_message,
        )
    
    @staticmethod
    def log_query_operation(
        query_type: str,
        filters: Optional[Dict[str, Any]] = None,
        result_count: Optional[int] = None,
        execution_time: Optional[float] = None,
        status: str = "success",
        error_message: Optional[str] = None,
    ) -> str:
        """记录查询操作
        
        Args:
            query_type: 查询类型
            filters: 查询过滤条件
            result_count: 结果数量
            execution_time: 执行时间（秒）
            status: 操作状态
            error_message: 错误消息
        
        Returns:
            审计日志ID
        """
        details = {
            "query_type": query_type,
        }
        
        if filters:
            details["filters"] = filters
        
        if result_count is not None:
            details["result_count"] = result_count
        
        if execution_time is not None:
            details["execution_time"] = f"{execution_time:.3f}s"
        
        return AuditLog.log_operation(
            operation_type=OperationType.QUERY_EXECUTE,
            resource_type="query",
            details=details,
            status=status,
            error_message=error_message,
        )
    
    @staticmethod
    def log_cache_operation(
        operation: OperationType,
        cache_key: str,
        hit: Optional[bool] = None,
        ttl: Optional[int] = None,
        status: str = "success",
        error_message: Optional[str] = None,
    ) -> str:
        """记录缓存操作
        
        Args:
            operation: 操作类型
            cache_key: 缓存键
            hit: 是否命中（仅用于查询操作）
            ttl: 过期时间（仅用于设置操作）
            status: 操作状态
            error_message: 错误消息
        
        Returns:
            审计日志ID
        """
        details = {
            "cache_key": cache_key,
        }
        
        if hit is not None:
            details["hit"] = hit
        
        if ttl is not None:
            details["ttl"] = ttl
        
        return AuditLog.log_operation(
            operation_type=operation,
            resource_type="cache",
            details=details,
            status=status,
            error_message=error_message,
        )
    
    @staticmethod
    def log_system_event(
        event_type: OperationType,
        details: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None,
    ) -> str:
        """记录系统事件
        
        Args:
            event_type: 事件类型
            details: 事件详情
            error_message: 错误消息
        
        Returns:
            审计日志ID
        """
        status = "success" if not error_message else "failed"
        
        return AuditLog.log_operation(
            operation_type=event_type,
            resource_type="system",
            details=details,
            status=status,
            error_message=error_message,
        )


# 全局审计日志实例
audit_log = AuditLog()
