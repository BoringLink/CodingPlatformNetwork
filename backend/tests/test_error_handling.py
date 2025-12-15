"""错误处理测试"""

import pytest
import asyncio
from app.utils.exceptions import (
    DataValidationError,
    LLMServiceError,
    DatabaseConnectionError,
    NodeNotFoundError,
)
from app.utils.error_handlers import (
    RetryConfig,
    retry_on_exception,
    CircuitBreaker,
    FallbackHandler,
    handle_exception_gracefully,
    log_operation,
)
from app.utils.audit_log import AuditLog, OperationType


class TestExceptions:
    """测试自定义异常"""
    
    def test_data_validation_error(self):
        """测试数据验证错误"""
        error = DataValidationError(
            message="Invalid field",
            field_name="email",
            expected_format="email@example.com",
            actual_value="invalid",
        )
        
        assert error.message == "Invalid field"
        assert error.error_code == "DATA_VALIDATION_ERROR"
        assert error.details["field_name"] == "email"
        assert error.details["expected_format"] == "email@example.com"
        
        error_dict = error.to_dict()
        assert error_dict["error"] == "DataValidationError"
        assert error_dict["message"] == "Invalid field"
    
    def test_llm_service_error(self):
        """测试LLM服务错误"""
        error = LLMServiceError(
            message="LLM call failed",
            model="qwen-turbo",
            retry_count=3,
        )
        
        assert error.message == "LLM call failed"
        assert error.error_code == "LLM_SERVICE_ERROR"
        assert error.details["model"] == "qwen-turbo"
        assert error.details["retry_count"] == 3
    
    def test_node_not_found_error(self):
        """测试节点不存在错误"""
        error = NodeNotFoundError(
            message="Node not found",
            node_id="123",
            node_type="Student",
        )
        
        assert error.message == "Node not found"
        assert error.error_code == "NODE_NOT_FOUND"
        assert error.details["node_id"] == "123"
        assert error.details["node_type"] == "Student"


class TestRetryMechanism:
    """测试重试机制"""
    
    @pytest.mark.asyncio
    async def test_retry_success_on_second_attempt(self):
        """测试第二次尝试成功"""
        attempt_count = 0
        
        @retry_on_exception(
            exceptions=ValueError,
            config=RetryConfig(max_retries=3, initial_delay=0.1),
        )
        async def flaky_function():
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count < 2:
                raise ValueError("Temporary error")
            return "success"
        
        result = await flaky_function()
        assert result == "success"
        assert attempt_count == 2
    
    @pytest.mark.asyncio
    async def test_retry_exhausted(self):
        """测试重试耗尽"""
        attempt_count = 0
        
        @retry_on_exception(
            exceptions=ValueError,
            config=RetryConfig(max_retries=2, initial_delay=0.1),
        )
        async def always_fails():
            nonlocal attempt_count
            attempt_count += 1
            raise ValueError("Permanent error")
        
        with pytest.raises(ValueError, match="Permanent error"):
            await always_fails()
        
        assert attempt_count == 3  # 初始尝试 + 2次重试
    
    @pytest.mark.asyncio
    async def test_retry_with_exponential_backoff(self):
        """测试指数退避"""
        config = RetryConfig(
            max_retries=3,
            initial_delay=0.1,
            exponential_base=2.0,
            jitter=False,
        )
        
        # 测试延迟计算
        assert config.calculate_delay(0) == 0.1
        assert config.calculate_delay(1) == 0.2
        assert config.calculate_delay(2) == 0.4
    
    def test_retry_sync_function(self):
        """测试同步函数重试"""
        attempt_count = 0
        
        @retry_on_exception(
            exceptions=ValueError,
            config=RetryConfig(max_retries=2, initial_delay=0.1),
        )
        def sync_flaky_function():
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count < 2:
                raise ValueError("Temporary error")
            return "success"
        
        result = sync_flaky_function()
        assert result == "success"
        assert attempt_count == 2


class TestCircuitBreaker:
    """测试断路器"""
    
    def test_circuit_breaker_opens_after_threshold(self):
        """测试达到阈值后断路器打开"""
        breaker = CircuitBreaker(
            failure_threshold=3,
            recovery_timeout=1.0,
            expected_exception=ValueError,
        )
        
        def failing_function():
            raise ValueError("Error")
        
        # 前3次失败
        for _ in range(3):
            with pytest.raises(ValueError):
                breaker.call(failing_function)
        
        # 断路器应该打开
        assert breaker.state == "open"
        
        # 第4次调用应该直接失败
        with pytest.raises(Exception, match="Circuit breaker is open"):
            breaker.call(failing_function)
    
    def test_circuit_breaker_half_open_recovery(self):
        """测试断路器半开状态恢复"""
        import time
        
        breaker = CircuitBreaker(
            failure_threshold=2,
            recovery_timeout=0.5,
            expected_exception=ValueError,
        )
        
        def failing_function():
            raise ValueError("Error")
        
        # 触发断路器打开
        for _ in range(2):
            with pytest.raises(ValueError):
                breaker.call(failing_function)
        
        assert breaker.state == "open"
        
        # 等待恢复超时
        time.sleep(0.6)
        
        # 下次调用应该进入半开状态
        def success_function():
            return "success"
        
        result = breaker.call(success_function)
        assert result == "success"
        assert breaker.state == "closed"


class TestFallbackHandler:
    """测试降级处理器"""
    
    @pytest.mark.asyncio
    async def test_llm_fallback_interaction(self):
        """测试LLM互动分析降级"""
        result = await FallbackHandler.llm_fallback(
            error=Exception("LLM unavailable"),
            input_text="这个作业很好",
            analysis_type="interaction",
        )
        
        assert result is not None
        assert "sentiment" in result
        assert result["sentiment"] == "positive"
        assert result["fallback"] is True
        assert result["confidence"] < 0.5
    
    @pytest.mark.asyncio
    async def test_llm_fallback_error(self):
        """测试LLM错误分析降级"""
        result = await FallbackHandler.llm_fallback(
            error=Exception("LLM unavailable"),
            input_text="学生计算错误",
            analysis_type="error",
        )
        
        assert result is not None
        assert "error_type" in result
        assert result["fallback"] is True
        assert result["confidence"] < 0.5


class TestGracefulErrorHandling:
    """测试优雅错误处理"""
    
    @pytest.mark.asyncio
    async def test_handle_exception_gracefully_async(self):
        """测试异步函数优雅处理异常"""
        @handle_exception_gracefully(fallback_value={"status": "error"})
        async def failing_function():
            raise ValueError("Something went wrong")
        
        result = await failing_function()
        assert result == {"status": "error"}
    
    def test_handle_exception_gracefully_sync(self):
        """测试同步函数优雅处理异常"""
        @handle_exception_gracefully(fallback_value="default")
        def failing_function():
            raise ValueError("Something went wrong")
        
        result = failing_function()
        assert result == "default"


class TestOperationLogging:
    """测试操作日志"""
    
    @pytest.mark.asyncio
    async def test_log_operation_decorator_async(self):
        """测试异步函数操作日志装饰器"""
        @log_operation("test_operation", include_args=True, include_result=True)
        async def test_function(x, y):
            return x + y
        
        result = await test_function(1, 2)
        assert result == 3
    
    def test_log_operation_decorator_sync(self):
        """测试同步函数操作日志装饰器"""
        @log_operation("test_operation", include_args=True, include_result=True)
        def test_function(x, y):
            return x + y
        
        result = test_function(1, 2)
        assert result == 3


class TestAuditLog:
    """测试审计日志"""
    
    def test_log_node_operation(self):
        """测试记录节点操作"""
        audit_id = AuditLog.log_node_operation(
            operation=OperationType.NODE_CREATE,
            node_type="Student",
            node_id="123",
            properties={"name": "Test Student"},
            status="success",
        )
        
        assert audit_id is not None
        assert len(audit_id) > 0
    
    def test_log_relationship_operation(self):
        """测试记录关系操作"""
        audit_id = AuditLog.log_relationship_operation(
            operation=OperationType.RELATIONSHIP_CREATE,
            relationship_type="LEARNS",
            relationship_id="456",
            from_node_id="123",
            to_node_id="789",
            status="success",
        )
        
        assert audit_id is not None
        assert len(audit_id) > 0
    
    def test_log_llm_operation(self):
        """测试记录LLM操作"""
        audit_id = AuditLog.log_llm_operation(
            model="qwen-turbo",
            analysis_type="interaction",
            input_length=100,
            output_length=50,
            cache_hit=True,
            retry_count=0,
            status="success",
        )
        
        assert audit_id is not None
        assert len(audit_id) > 0
    
    def test_log_data_import(self):
        """测试记录数据导入操作"""
        audit_id = AuditLog.log_data_import(
            import_id="import-123",
            total_records=1000,
            successful_records=950,
            failed_records=50,
            status="completed",
        )
        
        assert audit_id is not None
        assert len(audit_id) > 0
    
    def test_log_query_operation(self):
        """测试记录查询操作"""
        audit_id = AuditLog.log_query_operation(
            query_type="node_query",
            filters={"type": "Student"},
            result_count=10,
            execution_time=0.5,
            status="success",
        )
        
        assert audit_id is not None
        assert len(audit_id) > 0
    
    def test_log_system_event(self):
        """测试记录系统事件"""
        audit_id = AuditLog.log_system_event(
            event_type=OperationType.SYSTEM_START,
            details={"version": "0.1.0"},
        )
        
        assert audit_id is not None
        assert len(audit_id) > 0
