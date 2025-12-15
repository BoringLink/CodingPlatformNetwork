# Redis缓存快速开始指南

## 快速启动

### 1. 启动Redis服务

```bash
# 使用Docker Compose启动Redis
docker-compose up -d redis

# 验证Redis正在运行
docker-compose ps redis
```

### 2. 运行演示脚本

```bash
cd backend
source venv/bin/activate
python demo_cache.py
```

### 3. 运行测试

```bash
cd backend
source venv/bin/activate
python -m pytest tests/test_cache_service.py -v
```

## 基本使用

### 在代码中使用缓存

```python
from app.services.cache_service import get_cache_service

# 获取缓存服务实例
cache = get_cache_service()

# 设置缓存
await cache.set("my_key", "my_value")

# 获取缓存
value = await cache.get("my_key")

# 删除缓存
await cache.delete("my_key")

# 获取统计信息
stats = cache.get_statistics()
print(f"命中率: {stats['hit_rate']:.2%}")
```

### LLM服务自动使用缓存

```python
from app.services.llm_service import get_llm_service

# LLM服务已自动集成缓存
llm = get_llm_service()

# 第一次调用会请求API并缓存结果
result1 = await llm.analyze_interaction("学生讨论数学问题")

# 相同内容的第二次调用会从缓存返回（无需调用API）
result2 = await llm.analyze_interaction("学生讨论数学问题")
```

## 配置

在`.env`文件中配置：

```env
# Redis连接
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=  # 可选

# 缓存策略
CACHE_TTL=3600  # 默认过期时间（秒）
CACHE_ENABLED=true  # 是否启用缓存
```

## 监控

### 查看缓存统计

```python
stats = cache.get_statistics()
print(f"命中率: {stats['hit_rate']:.2%}")
print(f"总请求: {stats['total_requests']}")
```

### 查看Redis服务器信息

```python
info = await cache.get_info()
print(f"Redis版本: {info['redis_version']}")
print(f"内存使用: {info['used_memory_human']}")
```

## 常见问题

### Q: Redis连接失败怎么办？

**A**: 确保Redis服务正在运行：
```bash
docker-compose up -d redis
docker-compose ps redis
```

### Q: 如何清理缓存？

**A**: 使用模式匹配删除：
```python
# 删除所有LLM缓存
await cache.clear_pattern("interaction_analysis:*")
await cache.clear_pattern("error_analysis:*")
await cache.clear_pattern("knowledge_extraction:*")
```

### Q: 如何调整缓存过期时间？

**A**: 在`.env`文件中修改`CACHE_TTL`，或在代码中指定：
```python
# 设置10分钟过期
await cache.set("key", "value", ex=600)
```

### Q: 如何禁用缓存？

**A**: 在`.env`文件中设置：
```env
CACHE_ENABLED=false
```

## 更多信息

- 完整文档: `REDIS_CACHE_IMPLEMENTATION.md`
- 实现总结: `CACHE_IMPLEMENTATION_SUMMARY.md`
- 演示脚本: `demo_cache.py`
- 单元测试: `tests/test_cache_service.py`
