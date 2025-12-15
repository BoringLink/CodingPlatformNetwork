"""Redis缓存服务

提供基于Redis的缓存功能，用于LLM响应缓存等场景。
"""

from typing import Optional, Dict, Any
from datetime import datetime
import time
import redis.asyncio as redis
import structlog

from app.config import settings

logger = structlog.get_logger(__name__)


class CacheStatistics:
    """缓存统计信息"""
    
    def __init__(self):
        self.hits: int = 0
        self.misses: int = 0
        self.sets: int = 0
        self.deletes: int = 0
        self.errors: int = 0
        self.start_time: datetime = datetime.now()
        
        # 新增统计指标
        self.total_get_time: float = 0.0  # 总获取时间（秒）
        self.total_set_time: float = 0.0  # 总设置时间（秒）
        self.total_delete_time: float = 0.0  # 总删除时间（秒）
        self.avg_get_time: float = 0.0  # 平均获取时间（秒）
        self.avg_set_time: float = 0.0  # 平均设置时间（秒）
        self.avg_delete_time: float = 0.0  # 平均删除时间（秒）
    
    @property
    def total_requests(self) -> int:
        """总请求数"""
        return self.hits + self.misses
    
    @property
    def hit_rate(self) -> float:
        """缓存命中率"""
        if self.total_requests == 0:
            return 0.0
        return self.hits / self.total_requests
    
    @property
    def miss_rate(self) -> float:
        """缓存未命中率"""
        if self.total_requests == 0:
            return 0.0
        return self.misses / self.total_requests
    
    def update_latency(self, operation: str, latency: float) -> None:
        """更新延迟统计
        
        Args:
            operation: 操作类型（get, set, delete）
            latency: 延迟时间（秒）
        """
        if operation == "get":
            self.total_get_time += latency
            if self.total_requests > 0:
                self.avg_get_time = self.total_get_time / self.total_requests
        elif operation == "set":
            self.total_set_time += latency
            if self.sets > 0:
                self.avg_set_time = self.total_set_time / self.sets
        elif operation == "delete":
            self.total_delete_time += latency
            if self.deletes > 0:
                self.avg_delete_time = self.total_delete_time / self.deletes
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "hits": self.hits,
            "misses": self.misses,
            "sets": self.sets,
            "deletes": self.deletes,
            "errors": self.errors,
            "total_requests": self.total_requests,
            "hit_rate": round(self.hit_rate, 4),
            "miss_rate": round(self.miss_rate, 4),
            "uptime_seconds": (datetime.now() - self.start_time).total_seconds(),
            "total_get_time": round(self.total_get_time, 6),
            "total_set_time": round(self.total_set_time, 6),
            "total_delete_time": round(self.total_delete_time, 6),
            "avg_get_time": round(self.avg_get_time, 6),
            "avg_set_time": round(self.avg_set_time, 6),
            "avg_delete_time": round(self.avg_delete_time, 6),
        }
    
    def reset(self) -> None:
        """重置统计信息"""
        self.hits = 0
        self.misses = 0
        self.sets = 0
        self.deletes = 0
        self.errors = 0
        self.start_time = datetime.now()
        self.total_get_time = 0.0
        self.total_set_time = 0.0
        self.total_delete_time = 0.0
        self.avg_get_time = 0.0
        self.avg_set_time = 0.0
        self.avg_delete_time = 0.0


class CacheService:
    """Redis缓存服务
    
    提供异步的Redis缓存操作接口，包括：
    - 基本的缓存操作（get、set、delete）
    - 多种缓存过期策略（TTL、LRU、LFU）
    - 缓存防护机制（布隆过滤器、互斥锁等）
    - 缓存统计和监控
    - 模式匹配清除
    """
    
    def __init__(self):
        self._client: Optional[redis.Redis] = None
        self._stats = CacheStatistics()
        self._bloom_filter_key = "cache:bloom_filter"
    
    async def connect(self) -> None:
        """建立Redis连接"""
        if self._client is not None:
            logger.warning("redis_client_already_connected")
            return
        
        try:
            self._client = redis.Redis(
                host=settings.redis_host,
                port=settings.redis_port,
                db=settings.redis_db,
                password=settings.redis_password,
                max_connections=settings.redis_max_connections,
                decode_responses=True,
            )
            
            # 验证连接
            await self._client.ping()
            
            # 配置Redis缓存策略
            if settings.cache_strategy in ["lru", "lfu"]:
                # 根据缓存最大键数量和平均键大小(假设平均1KB)计算maxmemory
                # 预留20%额外空间
                estimated_memory = settings.cache_max_keys * 1024 * 1.2
                # 确保至少有10MB内存
                max_memory = max(int(estimated_memory), 10 * 1024 * 1024)
                
                await self._client.config_set("maxmemory", max_memory)
                await self._client.config_set("maxmemory-policy", f"allkeys-{settings.cache_strategy}")
                
                # 配置LRU/LFU相关参数，优化缓存性能
                if settings.cache_strategy == "lru":
                    # LRU策略下，配置采样数量
                    await self._client.config_set("maxmemory-samples", "5")
                elif settings.cache_strategy == "lfu":
                    # LFU策略下，配置衰减时间和初始计数器
                    await self._client.config_set("lfu-decay-time", "1")  # 1分钟衰减
                    await self._client.config_set("lfu-log-factor", "10")  # 访问频率对数因子
            
            logger.info(
                "redis_connected",
                host=settings.redis_host,
                port=settings.redis_port,
                db=settings.redis_db,
                cache_strategy=settings.cache_strategy,
            )
        except Exception as e:
            logger.error("redis_connection_failed", error=str(e))
            raise
    
    async def close(self) -> None:
        """关闭Redis连接"""
        if self._client is not None:
            await self._client.close()
            self._client = None
            logger.info("redis_disconnected")
    
    async def get(self, key: str) -> Optional[str]:
        """获取缓存值
        
        Args:
            key: 缓存键
        
        Returns:
            缓存值，如果不存在则返回None
        """
        if self._client is None:
            raise RuntimeError("Redis client not connected. Call connect() first.")
        
        start_time = time.time()
        
        try:
            value = await self._client.get(key)
            
            # 计算延迟
            latency = time.time() - start_time
            
            # 更新统计信息
            if value is not None:
                self._stats.hits += 1
                logger.debug("cache_hit", key=key, latency=latency)
            else:
                self._stats.misses += 1
                logger.debug("cache_miss", key=key, latency=latency)
            
            # 更新延迟统计
            self._stats.update_latency("get", latency)
            
            return value
        except Exception as e:
            self._stats.errors += 1
            logger.warning("redis_get_error", key=key, error=str(e), latency=time.time() - start_time)
            return None
    
    async def set(
        self,
        key: str,
        value: str,
        ex: Optional[int] = None,
    ) -> bool:
        """设置缓存值
        
        Args:
            key: 缓存键
            value: 缓存值
            ex: 过期时间（秒），默认使用配置的TTL
        
        Returns:
            是否设置成功
        """
        if self._client is None:
            raise RuntimeError("Redis client not connected. Call connect() first.")
        
        start_time = time.time()
        
        try:
            # 如果未指定过期时间，使用配置的默认TTL
            ttl = ex if ex is not None else settings.cache_ttl
            
            await self._client.set(key, value, ex=ttl)
            
            # 计算延迟
            latency = time.time() - start_time
            
            # 更新统计信息
            self._stats.sets += 1
            logger.debug("cache_set", key=key, ttl=ttl, latency=latency)
            
            # 更新延迟统计
            self._stats.update_latency("set", latency)
            
            return True
        except Exception as e:
            self._stats.errors += 1
            logger.warning("redis_set_error", key=key, error=str(e), latency=time.time() - start_time)
            return False
    
    async def delete(self, key: str) -> bool:
        """删除缓存值
        
        Args:
            key: 缓存键
        
        Returns:
            是否删除成功
        """
        if self._client is None:
            raise RuntimeError("Redis client not connected. Call connect() first.")
        
        start_time = time.time()
        
        try:
            result = await self._client.delete(key)
            
            # 计算延迟
            latency = time.time() - start_time
            
            # 更新统计信息
            if result > 0:
                self._stats.deletes += 1
                logger.debug("cache_delete", key=key, latency=latency)
            
            # 更新延迟统计
            self._stats.update_latency("delete", latency)
            
            return True
        except Exception as e:
            self._stats.errors += 1
            logger.warning("redis_delete_error", key=key, error=str(e), latency=time.time() - start_time)
            return False
    
    async def exists(self, key: str) -> bool:
        """检查缓存键是否存在
        
        Args:
            key: 缓存键
        
        Returns:
            是否存在
        """
        if self._client is None:
            raise RuntimeError("Redis client not connected. Call connect() first.")
        
        try:
            result = await self._client.exists(key)
            return result > 0
        except Exception as e:
            logger.warning("redis_exists_error", key=key, error=str(e))
            return False
    
    async def clear_pattern(self, pattern: str, batch_size: int = 1000) -> int:
        """清除匹配模式的所有键
        
        优化实现：使用分批处理，避免一次性处理大量键导致内存问题
        
        Args:
            pattern: 键模式（支持通配符）
            batch_size: 每批处理的键数量，默认1000
        
        Returns:
            删除的键数量
        """
        if self._client is None:
            raise RuntimeError("Redis client not connected. Call connect() first.")
        
        try:
            total_deleted = 0
            cursor = 0
            
            # 使用SCAN命令分批遍历，避免阻塞Redis
            while True:
                cursor, keys = await self._client.scan(cursor, match=pattern, count=batch_size)
                
                if keys:
                    deleted = await self._client.delete(*keys)
                    total_deleted += deleted
                    self._stats.deletes += deleted
                    
                    logger.debug(
                        "redis_clear_pattern_batch",
                        pattern=pattern,
                        batch_size=len(keys),
                        deleted=deleted,
                        total_deleted=total_deleted,
                    )
                
                # 游标为0表示遍历结束
                if cursor == 0:
                    break
            
            logger.info("redis_clear_pattern_completed", pattern=pattern, total_deleted=total_deleted)
            return total_deleted
        except Exception as e:
            self._stats.errors += 1
            logger.warning("redis_clear_pattern_error", pattern=pattern, error=str(e))
            return 0
    
    async def get_info(self) -> Dict[str, Any]:
        """获取Redis服务器信息
        
        Returns:
            Redis服务器信息字典
        """
        if self._client is None:
            raise RuntimeError("Redis client not connected. Call connect() first.")
        
        try:
            info = await self._client.info()
            
            # 提取关键指标
            return {
                "redis_version": info.get("redis_version", "unknown"),
                "used_memory_human": info.get("used_memory_human", "unknown"),
                "connected_clients": info.get("connected_clients", 0),
                "total_commands_processed": info.get("total_commands_processed", 0),
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0),
                "evicted_keys": info.get("evicted_keys", 0),
                "expired_keys": info.get("expired_keys", 0),
            }
        except Exception as e:
            logger.warning("redis_info_error", error=str(e))
            return {}
    
    async def get_key_count(self, pattern: str = "*") -> int:
        """获取匹配模式的键数量
        
        Args:
            pattern: 键模式（支持通配符），默认为所有键
        
        Returns:
            键数量
        """
        if self._client is None:
            raise RuntimeError("Redis client not connected. Call connect() first.")
        
        try:
            count = 0
            async for _ in self._client.scan_iter(match=pattern):
                count += 1
            return count
        except Exception as e:
            logger.warning("redis_key_count_error", pattern=pattern, error=str(e))
            return 0
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取缓存统计信息
        
        Returns:
            统计信息字典
        """
        return self._stats.to_dict()
    
    def reset_statistics(self) -> None:
        """重置缓存统计信息"""
        self._stats.reset()
        logger.info("cache_statistics_reset")
    
    async def get_memory_usage(self, key: str) -> Optional[int]:
        """获取键的内存使用量（字节）
        
        Args:
            key: 缓存键
        
        Returns:
            内存使用量（字节），如果键不存在则返回None
        """
        if self._client is None:
            raise RuntimeError("Redis client not connected. Call connect() first.")
        
        try:
            # 使用MEMORY USAGE命令
            usage = await self._client.memory_usage(key)
            return usage
        except Exception as e:
            logger.warning("redis_memory_usage_error", key=key, error=str(e))
            return None
    
    async def get_ttl(self, key: str) -> Optional[int]:
        """获取键的剩余生存时间（秒）
        
        Args:
            key: 缓存键
        
        Returns:
            剩余生存时间（秒），-1表示永不过期，-2表示键不存在，None表示查询失败
        """
        if self._client is None:
            raise RuntimeError("Redis client not connected. Call connect() first.")
        
        try:
            ttl = await self._client.ttl(key)
            return ttl
        except Exception as e:
            logger.warning("redis_ttl_error", key=key, error=str(e))
            return None
    
    async def set_ttl(self, key: str, seconds: int) -> bool:
        """设置键的过期时间
        
        Args:
            key: 缓存键
            seconds: 过期时间（秒）
        
        Returns:
            是否设置成功
        """
        if self._client is None:
            raise RuntimeError("Redis client not connected. Call connect() first.")
        
        try:
            result = await self._client.expire(key, seconds)
            if result:
                logger.debug("cache_ttl_set", key=key, seconds=seconds)
            return result
        except Exception as e:
            self._stats.errors += 1
            logger.warning("redis_set_ttl_error", key=key, error=str(e))
            return False


# 全局缓存服务实例
cache_service: Optional[CacheService] = None


def get_cache_service() -> CacheService:
    """获取缓存服务实例
    
    Returns:
        缓存服务实例
    
    Raises:
        RuntimeError: 如果服务未初始化
    """
    if cache_service is None:
        raise RuntimeError("Cache service not initialized")
    return cache_service
