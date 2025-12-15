# Redis缓存实现文档

## 概述

本文档描述了教育知识图谱系统中Redis缓存的实现，包括配置、功能和使用方法。

## 实现的功能

### 1. Redis连接管理
- 异步连接池管理
- 自动连接验证（ping）
- 优雅的连接关闭
- 连接错误处理和日志记录

### 2. 基本缓存操作
- **get(key)**: 获取缓存值
- **set(key, value, ex)**: 设置缓存值，支持自定义过期时间
- **delete(key)**: 删除缓存值
- **exists(key)**: 检查键是否存在
- **clear_pattern(pattern)**: 批量删除匹配模式的键

### 3. 缓存过期策略
- 默认TTL配置（通过`settings.cache_ttl`设置，默认3600秒）
- 支持为每个键设置自定义过期时间
- **get_ttl(key)**: 查询键的剩余生存时间
- **set_ttl(key, seconds)**: 动态修改键的过期时间

### 4. 缓存统计和监控

#### 统计指标
- **hits**: 缓存命中次数
- **misses**: 缓存未命中次数
- **sets**: 缓存设置次数
- **deletes**: 缓存删除次数
- **errors**: 错误次数
- **total_requests**: 总请求数（hits + misses）
- **hit_rate**: 缓存命中率
- **miss_rate**: 缓存未命中率
- **uptime_seconds**: 统计开始以来的运行时间

#### 监控功能
- **get_statistics()**: 获取缓存统计信息
- **reset_statistics()**: 重置统计信息
- **get_info()**: 获取Redis服务器信息
- **get_key_count(pattern)**: 获取匹配模式的键数量
- **get_memory_usage(key)**: 获取键的内存使用量

## 配置

### 环境变量配置

在`.env`文件中配置以下参数：

```env
# Redis配置
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=  # 可选，如果Redis设置了密码
REDIS_MAX_CONNECTIONS=50

# 缓存配置
CACHE_TTL=3600  # 默认过期时间（秒）
CACHE_ENABLED=true  # 是否启用缓存
```

### 代码配置

在`app/config.py`中定义的配置项：

```python
class Settings(BaseSettings):
    # Redis配置
    redis_host: str = Field(default="localhost")
    redis_port: int = Field(default=6379)
    redis_db: int = Field(default=0)
    redis_password: str | None = Field(default=None)
    redis_max_connections: int = Field(default=50)
    
    # 缓存配置
    cache_ttl: int = Field(default=3600, ge=0)
    cache_enabled: bool = Field(default=True)
```

## 使用方法

### 1. 初始化缓存服务

在应用启动时初始化（已在`app/main.py`中实现）：

```python
from app.services.cache_service import CacheService

# 创建实例
cache_service = CacheService()

# 连接Redis
await cache_service.connect()

# 应用关闭时断开连接
await cache_service.close()
```

### 2. 基本操作示例

```python
from app.services.cache_service import get_cache_service

# 获取缓存服务实例
cache = get_cache_service()

# 设置缓存（使用默认TTL）
await cache.set("user:123", "John Doe")

# 设置缓存（自定义TTL为600秒）
await cache.set("session:abc", "session_data", ex=600)

# 获取缓存
value = await cache.get("user:123")

# 检查键是否存在
exists = await cache.exists("user:123")

# 删除缓存
await cache.delete("user:123")

# 批量删除（删除所有user:*键）
count = await cache.clear_pattern("user:*")
```

### 3. LLM响应缓存

LLM服务已集成缓存功能（基于内容哈希）：

```python
from app.services.llm_service import LLMAnalysisService

# LLM服务会自动使用缓存
llm_service = LLMAnalysisService(cache_service=cache_service)

# 第一次调用会请求LLM API
analysis1 = await llm_service.analyze_interaction("学生讨论数学问题")

# 相同内容的第二次调用会从缓存返回（无需调用API）
analysis2 = await llm_service.analyze_interaction("学生讨论数学问题")
```

缓存键生成策略：
- 使用SHA256哈希算法
- 基于内容和参数生成唯一键
- 格式：`{prefix}:{content_hash}`
- 示例：`interaction_analysis:a3f5b2c1...`

### 4. 监控和统计

```python
# 获取缓存统计信息
stats = cache.get_statistics()
print(f"命中率: {stats['hit_rate']:.2%}")
print(f"总请求: {stats['total_requests']}")
print(f"命中: {stats['hits']}, 未命中: {stats['misses']}")

# 获取Redis服务器信息
info = await cache.get_info()
print(f"Redis版本: {info['redis_version']}")
print(f"内存使用: {info['used_memory_human']}")
print(f"连接客户端: {info['connected_clients']}")

# 获取键数量
total_keys = await cache.get_key_count("*")
llm_cache_keys = await cache.get_key_count("interaction_analysis:*")

# 重置统计信息
cache.reset_statistics()
```

### 5. 高级功能

```python
# 查询键的剩余生存时间
ttl = await cache.get_ttl("user:123")
if ttl > 0:
    print(f"键将在{ttl}秒后过期")
elif ttl == -1:
    print("键永不过期")
elif ttl == -2:
    print("键不存在")

# 动态设置过期时间
await cache.set_ttl("user:123", 1800)  # 设置为30分钟

# 查询键的内存使用
memory = await cache.get_memory_usage("user:123")
print(f"键占用内存: {memory} 字节")
```

## 测试

### 运行测试

确保Redis服务正在运行，然后执行：

```bash
# 使用Docker Compose启动Redis
docker-compose up -d redis

# 运行缓存服务测试
cd backend
source venv/bin/activate
python -m pytest tests/test_cache_service.py -v

# 运行所有测试
python -m pytest tests/ -v
```

### 测试覆盖

测试文件`tests/test_cache_service.py`包含以下测试：

1. **test_cache_connection**: Redis连接测试
2. **test_cache_set_and_get**: 设置和获取缓存
3. **test_cache_miss**: 缓存未命中
4. **test_cache_delete**: 删除缓存
5. **test_cache_expiration**: 缓存过期
6. **test_cache_default_ttl**: 默认TTL
7. **test_cache_pattern_clear**: 模式匹配清除
8. **test_cache_statistics**: 统计信息
9. **test_cache_key_count**: 键数量统计
10. **test_cache_info**: Redis服务器信息
11. **test_cache_set_ttl**: 设置TTL
12. **test_cache_exists**: 键存在性检查
13. **test_cache_statistics_class**: 统计类测试
14. **test_cache_concurrent_operations**: 并发操作
15. **test_cache_error_handling**: 错误处理

## 性能优化

### 1. LLM响应缓存

- **缓存键**: 基于输入内容的SHA256哈希
- **缓存时间**: 默认1小时（可配置）
- **缓存效果**: 相同输入无需重复调用LLM API，节省成本和时间

### 2. 连接池管理

- 使用Redis连接池，最大连接数可配置（默认50）
- 自动连接复用，减少连接开销

### 3. 批量操作

- `clear_pattern()`: 使用SCAN命令批量删除，避免阻塞
- 支持并发操作，提高吞吐量

## 监控建议

### 1. 关键指标监控

- **命中率**: 应保持在70%以上
- **错误率**: 应接近0
- **内存使用**: 监控Redis内存使用情况
- **键数量**: 定期检查缓存键数量

### 2. 告警设置

- 命中率低于50%时告警
- 错误率超过1%时告警
- Redis内存使用超过80%时告警
- Redis连接失败时告警

### 3. 日志监控

缓存服务使用structlog记录结构化日志：

```python
# 连接成功
logger.info("redis_connected", host=..., port=..., db=...)

# 缓存命中
logger.debug("cache_hit", key=...)

# 缓存未命中
logger.debug("cache_miss", key=...)

# 缓存设置
logger.debug("cache_set", key=..., ttl=...)

# 错误日志
logger.warning("redis_get_error", key=..., error=...)
logger.error("redis_connection_failed", error=...)
```

## 故障排查

### 1. 连接失败

**问题**: `redis.exceptions.ConnectionError: Error connecting to localhost:6379`

**解决方案**:
- 检查Redis是否正在运行：`docker-compose ps redis`
- 启动Redis：`docker-compose up -d redis`
- 检查端口是否被占用：`lsof -i :6379`
- 检查配置是否正确：`.env`文件中的Redis配置

### 2. 缓存未命中率高

**问题**: 命中率低于预期

**可能原因**:
- TTL设置过短，缓存过早过期
- 缓存键生成不一致
- Redis内存不足，触发淘汰策略

**解决方案**:
- 增加`CACHE_TTL`配置
- 检查缓存键生成逻辑
- 增加Redis内存限制
- 配置合适的淘汰策略（如`allkeys-lru`）

### 3. 内存使用过高

**问题**: Redis内存使用持续增长

**解决方案**:
- 设置合理的TTL，避免永久缓存
- 定期清理过期键
- 使用`clear_pattern()`清理不需要的缓存
- 配置Redis最大内存限制和淘汰策略

## 最佳实践

### 1. 缓存键命名

使用清晰的命名规范：
- 使用冒号分隔命名空间：`{namespace}:{identifier}`
- 示例：`interaction_analysis:abc123`, `error_analysis:def456`
- 便于使用模式匹配批量操作

### 2. TTL设置

根据数据特性设置合理的TTL：
- LLM响应：1小时（3600秒）
- 会话数据：30分钟（1800秒）
- 临时数据：5分钟（300秒）
- 静态数据：24小时（86400秒）

### 3. 错误处理

- 缓存失败不应影响核心功能
- 使用try-except捕获异常
- 记录错误日志但继续执行
- LLM服务在缓存失败时仍能正常调用API

### 4. 监控和维护

- 定期检查缓存统计信息
- 监控Redis服务器健康状态
- 设置合理的告警阈值
- 定期清理无用的缓存键

## 相关文件

- `backend/app/services/cache_service.py`: 缓存服务实现
- `backend/app/services/llm_service.py`: LLM服务（集成缓存）
- `backend/app/config.py`: 配置管理
- `backend/app/main.py`: 应用入口（初始化缓存服务）
- `backend/tests/test_cache_service.py`: 缓存服务测试
- `docker-compose.yml`: Docker配置（包含Redis服务）

## 总结

Redis缓存实现提供了完整的缓存管理功能，包括：
- ✅ Redis连接管理
- ✅ 基本缓存操作（get、set、delete、exists）
- ✅ 缓存过期策略（默认TTL、自定义TTL、动态修改）
- ✅ 缓存统计和监控（命中率、服务器信息、内存使用）
- ✅ LLM响应缓存（基于内容哈希）
- ✅ 批量操作（模式匹配清除）
- ✅ 错误处理和日志记录
- ✅ 完整的单元测试

该实现满足了任务需求中的所有要点，为系统提供了高效的缓存支持，特别是优化了LLM API调用的性能和成本。
