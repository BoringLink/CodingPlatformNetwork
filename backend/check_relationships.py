#!/usr/bin/env python3
"""
检查数据库中的关系数据
"""

import asyncio
import structlog
from app.database import neo4j_connection
from app.models.relationships import RelationshipType

logger = structlog.get_logger()


async def check_relationships():
    """检查数据库中的关系数据"""
    print("\n" + "=" * 60)
    print("检查数据库中是否存在关系数据")
    print("=" * 60)

    try:
        # 确保连接已建立
        if not hasattr(neo4j_connection, "_driver") or neo4j_connection._driver is None:
            await neo4j_connection.connect()

        # 查询所有关系
        async with neo4j_connection.get_session() as session:
            # 查询关系总数
            count_query = "MATCH ()-[r]-() RETURN COUNT(r) as rel_count"
            count_result = await session.run(count_query)
            count_record = await count_result.single()
            total_rels = count_record["rel_count"] if count_record else 0

            print(f"数据库中共有 {total_rels} 个关系")

            if total_rels > 0:
                # 查询关系类型分布
                type_query = "MATCH ()-[r]-() RETURN type(r) as rel_type, COUNT(r) as count ORDER BY count DESC"
                type_result = await session.run(type_query)
                type_records = await type_result.data()

                print("\n关系类型分布:")
                for record in type_records:
                    rel_type = record["rel_type"]
                    count = record["count"]
                    print(f"  - {rel_type}: {count} 个关系")

                # 查询部分关系详情
                sample_query = "MATCH (a)-[r]->(b) RETURN a.id as from_id, type(r) as rel_type, b.id as to_id LIMIT 10"
                sample_result = await session.run(sample_query)
                sample_records = await sample_result.data()

                print("\n部分关系详情:")
                for i, record in enumerate(sample_records):
                    print(
                        f"  {i+1}. {record['from_id']} -[{record['rel_type']}]-> {record['to_id']}"
                    )

    except Exception as e:
        logger.error("error_checking_relationships", error=str(e))
        print(f"检查关系数据时出错: {e}")
    finally:
        # 不需要关闭连接，由应用管理
        pass


if __name__ == "__main__":
    asyncio.run(check_relationships())
