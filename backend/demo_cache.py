"""Redis缓存功能演示脚本

此脚本演示Redis缓存服务的核心功能，包括：
1. 连接管理
2. 基本操作（set、get、delete）
3. 过期策略
4. 统计监控

运行前请确保Redis服务正在运行：
docker-compose up -d redis
"""

import asyncio
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.cache_service import CacheService
from app.config import settings


async def demo_basic_operations():
    """演示基本缓存操作"""
    print("\n=== 1. 基本缓存操作演示 ===\n")
    
    cache = CacheService()
    
    try:
        # 连接Redis
        print("连接Redis...")
        await cache.connect()
        print(f"✓ 成功连接到 {settings.redis_host}:{settings.redis_port}")
        
        # 设置缓存
        print("\n设置缓存...")
        await cache.set("demo:user:1", "Alice")
        await cache.set("demo:user:2", "Bob")
        await cache.set("demo:user:3", "Charlie")
        print("✓ 已设置3个缓存键")
        
        # 获取缓存
        print("\n获取缓存...")
        user1 = await cache.get("demo:user:1")
        user2 = await cache.get("demo:user:2")
        print(f"✓ demo:user:1 = {user1}")
        print(f"✓ demo:user:2 = {user2}")
        
        # 检查存在性
        print("\n检查键存在性...")
        exists = await cache.exists("demo:user:1")
        not_exists = await cache.exists("demo:user:999")
        print(f"✓ demo:user:1 存在: {exists}")
        print(f"✓ demo:user:999 存在: {not_exists}")
        
        # 删除缓存
        print("\n删除缓存...")
        await cache.delete("demo:user:3")
        exists_after_delete = await cache.exists("demo:user:3")
        print(f"✓ 删除后 demo:user:3 存在: {exists_after_delete}")
        
    finally:
        await cache.close()
        print("\n✓ 已关闭Redis连接")


async def demo_expiration():
    """演示缓存过期策略"""
    print("\n=== 2. 缓存过期策略演示 ===\n")
    
    cache = CacheService()
    
    try:
        await cache.connect()
        
        # 设置带过期时间的缓存
        print("设置3秒过期的缓存...")
        await cache.set("demo:temp:key", "temporary_value", ex=3)
        
        # 检查TTL
        ttl = await cache.get_ttl("demo:temp:key")
        print(f"✓ 当前TTL: {ttl}秒")
        
        # 立即获取
        value = await cache.get("demo:temp:key")
        print(f"✓ 立即获取: {value}")
        
        # 等待过期
        print("\n等待3秒让缓存过期...")
        await asyncio.sleep(3.5)
        
        # 再次获取
        value_after_expiry = await cache.get("demo:temp:key")
        print(f"✓ 过期后获取: {value_after_expiry}")
        
        # 演示默认TTL
        print(f"\n设置使用默认TTL的缓存（{settings.cache_ttl}秒）...")
        await cache.set("demo:default:key", "default_ttl_value")
        ttl = await cache.get_ttl("demo:default:key")
        print(f"✓ 默认TTL: {ttl}秒")
        
        # 动态修改TTL
        print("\n动态修改TTL为10秒...")
        await cache.set_ttl("demo:default:key", 10)
        new_ttl = await cache.get_ttl("demo:default:key")
        print(f"✓ 新TTL: {new_ttl}秒")
        
    finally:
        await cache.close()


async def demo_pattern_operations():
    """演示模式匹配操作"""
    print("\n=== 3. 模式匹配操作演示 ===\n")
    
    cache = CacheService()
    
    try:
        await cache.connect()
        
        # 设置多个键
        print("设置多个缓存键...")
        for i in range(5):
            await cache.set(f"demo:pattern:key{i}", f"value{i}")
        await cache.set("demo:other:key", "other_value")
        print("✓ 已设置6个缓存键")
        
        # 统计键数量
        pattern_count = await cache.get_key_count("demo:pattern:*")
        total_count = await cache.get_key_count("demo:*")
        print(f"\n✓ demo:pattern:* 匹配 {pattern_count} 个键")
        print(f"✓ demo:* 匹配 {total_count} 个键")
        
        # 批量删除
        print("\n批量删除 demo:pattern:* 键...")
        deleted = await cache.clear_pattern("demo:pattern:*")
        print(f"✓ 已删除 {deleted} 个键")
        
        # 验证删除
        remaining = await cache.get_key_count("demo:pattern:*")
        other_exists = await cache.exists("demo:other:key")
        print(f"✓ demo:pattern:* 剩余 {remaining} 个键")
        print(f"✓ demo:other:key 仍存在: {other_exists}")
        
    finally:
        # 清理所有demo键
        await cache.clear_pattern("demo:*")
        await cache.close()


async def demo_statistics():
    """演示缓存统计功能"""
    print("\n=== 4. 缓存统计功能演示 ===\n")
    
    cache = CacheService()
    
    try:
        await cache.connect()
        
        # 重置统计
        cache.reset_statistics()
        print("已重置统计信息\n")
        
        # 执行一系列操作
        print("执行缓存操作...")
        await cache.set("demo:stats:1", "value1")
        await cache.set("demo:stats:2", "value2")
        await cache.set("demo:stats:3", "value3")
        
        await cache.get("demo:stats:1")  # hit
        await cache.get("demo:stats:1")  # hit
        await cache.get("demo:stats:2")  # hit
        await cache.get("demo:stats:999")  # miss
        await cache.get("demo:stats:888")  # miss
        
        await cache.delete("demo:stats:3")
        
        # 获取统计信息
        stats = cache.get_statistics()
        print("\n缓存统计信息:")
        print(f"  设置次数: {stats['sets']}")
        print(f"  命中次数: {stats['hits']}")
        print(f"  未命中次数: {stats['misses']}")
        print(f"  删除次数: {stats['deletes']}")
        print(f"  总请求数: {stats['total_requests']}")
        print(f"  命中率: {stats['hit_rate']:.2%}")
        print(f"  未命中率: {stats['miss_rate']:.2%}")
        print(f"  运行时间: {stats['uptime_seconds']:.2f}秒")
        
    finally:
        await cache.clear_pattern("demo:*")
        await cache.close()


async def demo_monitoring():
    """演示监控功能"""
    print("\n=== 5. 监控功能演示 ===\n")
    
    cache = CacheService()
    
    try:
        await cache.connect()
        
        # 获取Redis服务器信息
        print("Redis服务器信息:")
        info = await cache.get_info()
        print(f"  版本: {info.get('redis_version', 'N/A')}")
        print(f"  内存使用: {info.get('used_memory_human', 'N/A')}")
        print(f"  连接客户端: {info.get('connected_clients', 'N/A')}")
        print(f"  处理命令数: {info.get('total_commands_processed', 'N/A')}")
        print(f"  键空间命中: {info.get('keyspace_hits', 'N/A')}")
        print(f"  键空间未命中: {info.get('keyspace_misses', 'N/A')}")
        
        # 设置测试键并查询内存使用
        print("\n内存使用分析:")
        await cache.set("demo:memory:test", "x" * 1000)  # 1KB数据
        memory = await cache.get_memory_usage("demo:memory:test")
        if memory:
            print(f"  demo:memory:test 占用内存: {memory} 字节")
        
    finally:
        await cache.clear_pattern("demo:*")
        await cache.close()


async def demo_llm_cache_simulation():
    """演示LLM缓存场景"""
    print("\n=== 6. LLM缓存场景演示 ===\n")
    
    cache = CacheService()
    
    try:
        await cache.connect()
        cache.reset_statistics()
        
        # 模拟LLM响应缓存
        import hashlib
        import json
        
        def generate_cache_key(prefix: str, content: str) -> str:
            """生成缓存键（模拟LLM服务的逻辑）"""
            content_hash = hashlib.sha256(content.encode()).hexdigest()
            return f"{prefix}:{content_hash}"
        
        # 第一次"调用"（缓存未命中）
        print("第一次分析互动内容...")
        content1 = "学生A和学生B讨论数学问题"
        cache_key1 = generate_cache_key("interaction_analysis", content1)
        
        cached = await cache.get(cache_key1)
        if cached is None:
            print("  ✗ 缓存未命中，需要调用LLM API")
            # 模拟LLM响应
            llm_response = {
                "sentiment": "positive",
                "topics": ["数学", "讨论", "学习"],
                "confidence": 0.85
            }
            await cache.set(cache_key1, json.dumps(llm_response))
            print(f"  ✓ 已缓存LLM响应")
        
        # 第二次"调用"相同内容（缓存命中）
        print("\n第二次分析相同内容...")
        cached = await cache.get(cache_key1)
        if cached:
            print("  ✓ 缓存命中，无需调用LLM API")
            response = json.loads(cached)
            print(f"  响应: {response}")
        
        # 第三次"调用"不同内容（缓存未命中）
        print("\n分析不同内容...")
        content2 = "学生C询问老师关于作业的问题"
        cache_key2 = generate_cache_key("interaction_analysis", content2)
        
        cached = await cache.get(cache_key2)
        if cached is None:
            print("  ✗ 缓存未命中，需要调用LLM API")
            llm_response = {
                "sentiment": "neutral",
                "topics": ["作业", "提问", "师生互动"],
                "confidence": 0.90
            }
            await cache.set(cache_key2, json.dumps(llm_response))
            print(f"  ✓ 已缓存LLM响应")
        
        # 显示统计
        print("\nLLM缓存统计:")
        stats = cache.get_statistics()
        print(f"  总请求: {stats['total_requests']}")
        print(f"  命中: {stats['hits']}")
        print(f"  未命中: {stats['misses']}")
        print(f"  命中率: {stats['hit_rate']:.2%}")
        print(f"  节省的API调用: {stats['hits']} 次")
        
    finally:
        await cache.clear_pattern("interaction_analysis:*")
        await cache.close()


async def main():
    """主函数"""
    print("=" * 60)
    print("Redis缓存功能演示")
    print("=" * 60)
    
    try:
        await demo_basic_operations()
        await demo_expiration()
        await demo_pattern_operations()
        await demo_statistics()
        await demo_monitoring()
        await demo_llm_cache_simulation()
        
        print("\n" + "=" * 60)
        print("✓ 所有演示完成！")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ 错误: {e}")
        print("\n请确保Redis服务正在运行:")
        print("  docker-compose up -d redis")
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
