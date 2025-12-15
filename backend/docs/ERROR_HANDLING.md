# 错误处理和日志系统

本文档描述了教育知识图谱系统的错误处理和日志记录机制。

## 概述

系统实现了全面的错误处理和日志记录功能，包括：

1. **自定义异常类** - 明确的错误类型和详细的错误信息
2. **全局异常处理器** - 统一的异常处理和HTTP响应
3. **重试机制** - 指数退避的自动重试
4. **断路器模式** - 防止级联失败
5. **降级策略** - 服务不可用时的备用方案
6. **审计日志** - 记录所有关键操作
7. **操作日志** - 自动记录函数调用

## 自定义异常

### 异常层次结构

```
BaseAppException (基础异常)
├── DataValidationError (数据验证错误)
├── LLMServiceError (LLM服务错误)
│   ├── LLMTimeoutError (LLM超时错误)
│   ├── LLMQuotaExceededError (LLM配额超限错误)
│   └── LLMParseError (LLM响应解析错误)
├── DatabaseError (数据库错误)
│   ├── DatabaseConnectionError (数据库连接错误)
│   ├── DatabaseQueryTimeoutError (数据库查询超时错误)
│   └── DatabaseConstraintViolationError (数据库约束违反错误)
├── DataConflictError (数据冲突错误)
├── ResourceLimitError (资源限制错误)
│   └── QueueFullError (队列满错误)
├── NodeNotFoundError (节点不存在错误)
├── RelationshipNotFoundError (关系不存在错误)
├── CacheError (缓存错误)
└── ConfigurationError (配置错误)
```

### 使用示例

```python
from app.utils.exceptions import DataValidationError, NodeNotFoundError

# 抛出数据验证错误
raise DataValidationError(
    message="Invalid email format",
    field_name="email",
    expected_format="email@example.com",
    actual_value="invalid",
)

# 抛出节点不存在错误
raise NodeNotFoundError(
    message="Student node not found",
    node_id="123",
    node_type="Student",
)
```

### 异常属性

所有自定义异常都包含以下属性：

- `message`: 错误消息
- `error_code`: 错误代码（用于API响应）
- `details`: 错误详情字典
- `original_error`: 原始异常（如果有）

## 全局异常处理器

系统在 `main.py` 中实现了全局异常处理器，自动捕获所有未处理的异常：

```python
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """全局异常处理器"""
    # 记录详细错误信息
    logger.error("unhandled_exception", ...)
    
    # 根据异常类型返回不同的HTTP状态码
    # 404: NodeNotFoundError, RelationshipNotFoundError
    # 400: DataValidationError
    # 503: DatabaseConnectionError, LLMServiceError
    # 500: 其他异常
```

### HTTP状态码映射

| 异常类型 | HTTP状态码 | 说明 |
|---------|-----------|------|
| NodeNotFoundError | 404 | 资源不存在 |
| RelationshipNotFoundError | 404 | 资源不存在 |
| DataValidationError | 400 | 请求数据无效 |
| DatabaseConnectionError | 503 | 服务不可用 |
| LLMServiceError | 503 | 服务不可用 |
| 其他异常 | 500 | 内部服务器错误 |

## 重试机制

### 配置重试

```python
from app.utils.error_handlers import retry_on_exception, RetryConfig

@retry_on_exception(
    exceptions=(LLMServiceError, DatabaseConnectionError),
    config=RetryConfig(
        max_retries=3,           # 最大重试次数
        initial_delay=1.0,       # 初始延迟（秒）
        max_delay=60.0,          # 最大延迟（秒）
        exponential_base=2.0,    # 指数退避基数
        jitter=True,             # 添加随机抖动
    ),
)
async def call_external_service():
    # 可能失败的操作
    pass
```

### 重试策略

系统使用**指数退避**算法计算重试延迟：

```
delay = min(initial_delay * (exponential_base ^ attempt), max_delay)
```

例如，使用默认配置：
- 第1次重试: 1秒后
- 第2次重试: 2秒后
- 第3次重试: 4秒后

添加随机抖动可以避免雷鸣群效应（多个客户端同时重试）。

## 断路器模式

断路器用于防止级联失败，在连续失败超过阈值时暂停调用：

```python
from app.utils.error_handlers import CircuitBreaker

# 创建断路器
breaker = CircuitBreaker(
    failure_threshold=5,      # 失败阈值
    recovery_timeout=60.0,    # 恢复超时时间（秒）
    expected_exception=LLMServiceError,
)

# 使用断路器保护调用
try:
    result = await breaker.call_async(llm_service.analyze, text)
except Exception as e:
    # 断路器打开或调用失败
    pass
```

### 断路器状态

1. **Closed（关闭）**: 正常状态，允许所有调用
2. **Open（打开）**: 失败次数超过阈值，拒绝所有调用
3. **Half-Open（半开）**: 恢复超时后，允许一次尝试调用

## 降级策略

当服务不可用时，系统提供降级策略：

### LLM服务降级

```python
from app.utils.error_handlers import FallbackHandler

try:
    result = await llm_service.analyze_interaction(text)
except LLMServiceError as e:
    # 使用基于规则的备用分析
    result = await FallbackHandler.llm_fallback(
        error=e,
        input_text=text,
        analysis_type="interaction",
    )
```

降级策略：
- **互动分析**: 基于关键词的简单情感分析
- **错误分析**: 返回通用错误类型，标记需要人工审核
- **知识点提取**: 返回空列表

### 缓存服务降级

```python
try:
    await cache_service.set(key, value)
except CacheError as e:
    # 记录日志但不影响主流程
    await FallbackHandler.cache_fallback(e, "set")
```

### 数据库服务降级

```python
try:
    await graph_service.create_node(...)
except DatabaseConnectionError as e:
    # 将数据缓存到消息队列
    await FallbackHandler.database_fallback(e, "create_node", data)
```

## 优雅错误处理

使用装饰器优雅处理异常，返回降级值而不是让异常传播：

```python
from app.utils.error_handlers import handle_exception_gracefully

@handle_exception_gracefully(fallback_value={}, log_level="warning")
async def get_optional_data():
    # 可能失败的操作
    return await fetch_data()

# 如果失败，返回 {} 而不是抛出异常
result = await get_optional_data()
```

## 操作日志

### 自动记录操作

```python
from app.utils.error_handlers import log_operation

@log_operation(
    operation_name="create_node",
    include_args=True,      # 包含参数
    include_result=True,    # 包含返回值
)
async def create_node(node_type, properties):
    # 函数实现
    pass
```

装饰器会自动记录：
- 操作开始时间
- 操作参数（可选）
- 操作结果（可选）
- 操作耗时
- 操作状态（成功/失败）
- 错误信息（如果失败）

## 审计日志

审计日志记录系统中的所有关键操作，用于审计和追踪。

### 记录节点操作

```python
from app.utils.audit_log import audit_log, OperationType

audit_log.log_node_operation(
    operation=OperationType.NODE_CREATE,
    node_type="Student",
    node_id="123",
    properties={"name": "张三"},
    user_id="admin",
    status="success",
)
```

### 记录关系操作

```python
audit_log.log_relationship_operation(
    operation=OperationType.RELATIONSHIP_CREATE,
    relationship_type="LEARNS",
    relationship_id="456",
    from_node_id="123",
    to_node_id="789",
    status="success",
)
```

### 记录LLM操作

```python
audit_log.log_llm_operation(
    model="qwen-turbo",
    analysis_type="interaction",
    input_length=100,
    output_length=50,
    cache_hit=True,
    retry_count=0,
    status="success",
)
```

### 记录数据导入

```python
audit_log.log_data_import(
    import_id="import-123",
    total_records=1000,
    successful_records=950,
    failed_records=50,
    status="completed",
)
```

### 记录查询操作

```python
audit_log.log_query_operation(
    query_type="node_query",
    filters={"type": "Student"},
    result_count=10,
    execution_time=0.5,
    status="success",
)
```

### 记录系统事件

```python
audit_log.log_system_event(
    event_type=OperationType.SYSTEM_START,
    details={"version": "0.1.0"},
)
```

## 日志格式

系统使用 `structlog` 进行结构化日志记录。

### JSON格式（生产环境）

```json
{
  "timestamp": "2024-12-03T12:00:00.000Z",
  "level": "error",
  "event": "llm_call_failed",
  "model": "qwen-turbo",
  "attempt": 3,
  "error": "Connection timeout"
}
```

### Console格式（开发环境）

```
2024-12-03 12:00:00 [error    ] llm_call_failed        model=qwen-turbo attempt=3 error=Connection timeout
```

### 配置日志格式

在 `.env` 文件中配置：

```bash
LOG_LEVEL=INFO          # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FORMAT=json         # json 或 console
```

## 错误处理最佳实践

### 1. 使用具体的异常类型

❌ 不好：
```python
raise Exception("Node not found")
```

✅ 好：
```python
raise NodeNotFoundError(
    message="Student node not found",
    node_id=student_id,
    node_type="Student",
)
```

### 2. 记录详细的错误上下文

❌ 不好：
```python
logger.error("Error occurred")
```

✅ 好：
```python
logger.error(
    "node_creation_failed",
    node_type=node_type,
    properties=properties,
    error=str(e),
)
```

### 3. 使用重试机制处理临时错误

```python
@retry_on_exception(
    exceptions=(LLMTimeoutError, DatabaseConnectionError),
    config=RetryConfig(max_retries=3),
)
async def call_external_service():
    pass
```

### 4. 使用断路器防止级联失败

```python
breaker = CircuitBreaker(failure_threshold=5)
result = await breaker.call_async(external_service.call)
```

### 5. 提供降级策略

```python
try:
    result = await primary_service.call()
except ServiceError:
    result = await fallback_service.call()
```

### 6. 记录审计日志

```python
audit_log.log_node_operation(
    operation=OperationType.NODE_CREATE,
    node_type=node_type,
    node_id=node_id,
    status="success",
)
```

## 监控和告警

### 关键指标

1. **错误率**: 每分钟错误数量
2. **重试率**: 需要重试的操作比例
3. **断路器状态**: 断路器打开的次数
4. **降级使用率**: 使用降级策略的比例
5. **响应时间**: 操作平均耗时

### 告警规则

- 错误率 > 5% 时发送警告
- 断路器打开时发送紧急告警
- 降级使用率 > 10% 时发送警告
- 响应时间 > 5秒时发送警告

## 故障排查

### 查看错误日志

```bash
# 查看最近的错误
grep "level.*error" logs/app.log | tail -20

# 查看特定类型的错误
grep "llm_call_failed" logs/app.log

# 查看审计日志
grep "audit_log" logs/app.log
```

### 常见问题

#### 1. LLM服务频繁失败

**症状**: 大量 `llm_call_failed` 日志

**排查步骤**:
1. 检查API密钥是否有效
2. 检查网络连接
3. 检查是否超过配额
4. 查看重试次数和延迟

**解决方案**:
- 增加重试次数
- 使用断路器
- 启用降级策略

#### 2. 数据库连接失败

**症状**: `database_connection_failed` 日志

**排查步骤**:
1. 检查数据库是否运行
2. 检查连接配置
3. 检查网络连接
4. 查看连接池状态

**解决方案**:
- 重启数据库
- 检查防火墙规则
- 增加连接池大小

#### 3. 缓存服务不可用

**症状**: `cache_error` 日志

**排查步骤**:
1. 检查Redis是否运行
2. 检查连接配置
3. 查看内存使用情况

**解决方案**:
- 重启Redis
- 清理过期数据
- 增加内存限制

## 参考资料

- [需求文档 8.1-8.5](../.kiro/specs/education-knowledge-graph/requirements.md)
- [设计文档 - 错误处理](../.kiro/specs/education-knowledge-graph/design.md#错误处理)
- [structlog文档](https://www.structlog.org/)
- [断路器模式](https://martinfowler.com/bliki/CircuitBreaker.html)
