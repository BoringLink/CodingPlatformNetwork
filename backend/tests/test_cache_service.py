"""测试Redis缓存服务

测试缓存服务的核心功能：
- Redis连接管理
- 基本缓存操作（get、set、delete）
- 缓存过期策略
- 缓存统计和监控
- 模式匹配清除
"""

import pytest
import asyncio
from app.services.cache_service import CacheService, CacheStatistics
from app.config import settings


@pytest.fixture
async def cache_service():
    """创建并连接缓存服务实例"""
    service = CacheService()
    await service.connect()
    
    # 清理测试数据
    await service.clear_pattern("test:*")
    service.reset_statistics()
    
    yield service
    
    # 清理测试数据（如果连接仍然存在）
    try:
        if service._client and service._client.connection:
            await service.clear_pattern("test:*")
            await service.close()
    except (RuntimeError, Exception):
        # 如果连接已关闭或出现其他错误，忽略
        pass


@pytest.mark.asyncio
async def test_cache_connection(cache_service):
    """测试Redis连接"""
    # 连接应该已经建立
    assert cache_service._client is not None
    
    # 测试ping
    result = await cache_service._client.ping()
    assert result is True


@pytest.mark.asyncio
async def test_cache_set_and_get(cache_service):
    """测试缓存设置和获取"""
    key = "test:simple_key"
    value = "test_value"
    
    # 设置缓存
    result = await cache_service.set(key, value)
    assert result is True
    
    # 获取缓存
    cached_value = await cache_service.get(key)
    assert cached_value == value
    
    # 验证统计信息
    stats = cache_service.get_statistics()
    assert stats["sets"] == 1
    assert stats["hits"] == 1
    assert stats["misses"] == 0


@pytest.mark.asyncio
async def test_cache_miss(cache_service):
    """测试缓存未命中"""
    key = "test:nonexistent_key"
    
    # 获取不存在的键
    value = await cache_service.get(key)
    assert value is None
    
    # 验证统计信息
    stats = cache_service.get_statistics()
    assert stats["misses"] == 1
    assert stats["hits"] == 0


@pytest.mark.asyncio
async def test_cache_delete(cache_service):
    """测试缓存删除"""
    key = "test:delete_key"
    value = "test_value"
    
    # 设置缓存
    await cache_service.set(key, value)
    
    # 验证存在
    exists = await cache_service.exists(key)
    assert exists is True
    
    # 删除缓存
    result = await cache_service.delete(key)
    assert result is True
    
    # 验证已删除
    exists = await cache_service.exists(key)
    assert exists is False
    
    # 验证统计信息
    stats = cache_service.get_statistics()
    assert stats["deletes"] == 1


@pytest.mark.asyncio
async def test_cache_expiration(cache_service):
    """测试缓存过期"""
    key = "test:expiring_key"
    value = "test_value"
    ttl = 2  # 2秒过期
    
    # 设置带过期时间的缓存
    await cache_service.set(key, value, ex=ttl)
    
    # 立即获取应该存在
    cached_value = await cache_service.get(key)
    assert cached_value == value
    
    # 检查TTL
    remaining_ttl = await cache_service.get_ttl(key)
    assert remaining_ttl is not None
    assert 0 < remaining_ttl <= ttl
    
    # 等待过期
    await asyncio.sleep(ttl + 0.5)
    
    # 再次获取应该不存在
    cached_value = await cache_service.get(key)
    assert cached_value is None


@pytest.mark.asyncio
async def test_cache_default_ttl(cache_service):
    """测试默认TTL"""
    key = "test:default_ttl_key"
    value = "test_value"
    
    # 设置缓存（不指定TTL，应使用默认值）
    await cache_service.set(key, value)
    
    # 检查TTL
    ttl = await cache_service.get_ttl(key)
    assert ttl is not None
    assert ttl > 0
    assert ttl <= settings.cache_ttl


@pytest.mark.asyncio
async def test_cache_pattern_clear(cache_service):
    """测试模式匹配清除"""
    # 设置多个键
    keys = [
        ("test:pattern:key1", "value1"),
        ("test:pattern:key2", "value2"),
        ("test:pattern:key3", "value3"),
        ("test:other:key", "value4"),
    ]
    
    for key, value in keys:
        await cache_service.set(key, value)
    
    # 清除匹配模式的键
    deleted_count = await cache_service.clear_pattern("test:pattern:*")
    assert deleted_count == 3
    
    # 验证匹配的键已删除
    for key, _ in keys[:3]:
        exists = await cache_service.exists(key)
        assert exists is False
    
    # 验证不匹配的键仍存在
    exists = await cache_service.exists("test:other:key")
    assert exists is True


@pytest.mark.asyncio
async def test_cache_statistics(cache_service):
    """测试缓存统计"""
    # 执行一系列操作
    await cache_service.set("test:stats:key1", "value1")
    await cache_service.set("test:stats:key2", "value2")
    await cache_service.get("test:stats:key1")  # hit
    await cache_service.get("test:stats:key1")  # hit
    await cache_service.get("test:stats:nonexistent")  # miss
    await cache_service.delete("test:stats:key1")
    
    # 获取统计信息
    stats = cache_service.get_statistics()
    
    assert stats["sets"] == 2
    assert stats["hits"] == 2
    assert stats["misses"] == 1
    assert stats["deletes"] == 1
    assert stats["total_requests"] == 3
    assert stats["hit_rate"] == pytest.approx(2/3, rel=0.01)
    assert stats["miss_rate"] == pytest.approx(1/3, rel=0.01)
    
    # 重置统计
    cache_service.reset_statistics()
    stats = cache_service.get_statistics()
    
    assert stats["sets"] == 0
    assert stats["hits"] == 0
    assert stats["misses"] == 0
    assert stats["deletes"] == 0


@pytest.mark.asyncio
async def test_cache_key_count(cache_service):
    """测试键数量统计"""
    # 设置多个键
    for i in range(5):
        await cache_service.set(f"test:count:key{i}", f"value{i}")
    
    # 获取匹配模式的键数量
    count = await cache_service.get_key_count("test:count:*")
    assert count == 5
    
    # 获取所有测试键的数量
    total_count = await cache_service.get_key_count("test:*")
    assert total_count >= 5


@pytest.mark.asyncio
async def test_cache_info(cache_service):
    """测试Redis服务器信息"""
    info = await cache_service.get_info()
    
    # 验证关键字段存在
    assert "redis_version" in info
    assert "used_memory_human" in info
    assert "connected_clients" in info
    
    # 验证数值字段
    assert isinstance(info.get("connected_clients", 0), int)


@pytest.mark.asyncio
async def test_cache_set_ttl(cache_service):
    """测试设置TTL"""
    key = "test:set_ttl_key"
    value = "test_value"
    
    # 设置缓存（无过期时间）
    await cache_service.set(key, value, ex=None)
    
    # 设置TTL
    result = await cache_service.set_ttl(key, 10)
    assert result is True
    
    # 验证TTL
    ttl = await cache_service.get_ttl(key)
    assert ttl is not None
    assert 0 < ttl <= 10


@pytest.mark.asyncio
async def test_cache_exists(cache_service):
    """测试键存在性检查"""
    key = "test:exists_key"
    value = "test_value"
    
    # 键不存在
    exists = await cache_service.exists(key)
    assert exists is False
    
    # 设置键
    await cache_service.set(key, value)
    
    # 键存在
    exists = await cache_service.exists(key)
    assert exists is True


@pytest.mark.asyncio
async def test_cache_statistics_class():
    """测试CacheStatistics类"""
    stats = CacheStatistics()
    
    # 初始状态
    assert stats.hits == 0
    assert stats.misses == 0
    assert stats.total_requests == 0
    assert stats.hit_rate == 0.0
    assert stats.miss_rate == 0.0
    
    # 模拟操作
    stats.hits = 7
    stats.misses = 3
    stats.sets = 5
    stats.deletes = 2
    
    # 验证计算
    assert stats.total_requests == 10
    assert stats.hit_rate == 0.7
    assert stats.miss_rate == 0.3
    
    # 验证to_dict
    stats_dict = stats.to_dict()
    assert stats_dict["hits"] == 7
    assert stats_dict["misses"] == 3
    assert stats_dict["hit_rate"] == 0.7
    assert stats_dict["miss_rate"] == 0.3
    
    # 重置
    stats.reset()
    assert stats.hits == 0
    assert stats.misses == 0
    assert stats.total_requests == 0


@pytest.mark.asyncio
async def test_cache_concurrent_operations(cache_service):
    """测试并发操作"""
    keys = [f"test:concurrent:key{i}" for i in range(10)]
    
    # 并发设置
    await asyncio.gather(*[
        cache_service.set(key, f"value{i}")
        for i, key in enumerate(keys)
    ])
    
    # 并发获取
    values = await asyncio.gather(*[
        cache_service.get(key)
        for key in keys
    ])
    
    # 验证所有值都正确
    for i, value in enumerate(values):
        assert value == f"value{i}"
    
    # 验证统计信息
    stats = cache_service.get_statistics()
    assert stats["sets"] == 10
    assert stats["hits"] == 10


@pytest.mark.asyncio
async def test_cache_error_handling(cache_service):
    """测试错误处理"""
    # 关闭连接
    await cache_service.close()
    
    # 尝试操作应该抛出异常
    with pytest.raises(RuntimeError, match="Redis client not connected"):
        await cache_service.get("test:key")
    
    with pytest.raises(RuntimeError, match="Redis client not connected"):
        await cache_service.set("test:key", "value")
    
    with pytest.raises(RuntimeError, match="Redis client not connected"):
        await cache_service.delete("test:key")
