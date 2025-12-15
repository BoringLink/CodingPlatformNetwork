#!/usr/bin/env python3
"""
检查数据库中是否存在节点数据的脚本
"""

import asyncio
from app.database import neo4j_connection
from app.services.query_service import query_service

async def check_database():
    """检查数据库中是否存在节点数据"""
    print("=" * 60)
    print("检查数据库中是否存在节点数据")
    print("=" * 60)
    
    try:
        # 使用查询服务获取所有节点
        from app.services.query_service import NodeFilter
        nodes = await query_service.query_nodes(NodeFilter())
        print(f"\n数据库中共有 {len(nodes)} 个节点")
        
        if nodes:
            # 按类型统计节点数量
            node_types = {}
            for node in nodes:
                node_type = node.type.value
                node_types[node_type] = node_types.get(node_type, 0) + 1
            
            print("\n节点类型分布:")
            for node_type, count in node_types.items():
                print(f"  - {node_type}: {count} 个节点")
        else:
            print("\n数据库中没有任何节点数据")
            print("需要添加模拟数据")
    
    except Exception as e:
        print(f"\n查询数据库时出错: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("检查完成")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(check_database())