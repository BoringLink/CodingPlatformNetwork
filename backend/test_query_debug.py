#!/usr/bin/env python3
"""测试脚本：调试节点查询逻辑"""

import asyncio
import logging
from typing import List

from app.models.nodes import NodeType
from app.services.query_service import QueryService, NodeFilter
from app.database import init_database, close_database, neo4j_connection

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_direct_query():
    """直接查询Neo4j数据库中的所有节点"""
    logger.info("执行直接查询...")
    async with neo4j_connection.get_session() as session:
        # 直接查询所有节点，包括标签和属性
        query = "MATCH (n) RETURN n, labels(n) AS labels LIMIT 100"
        result = await session.run(query)
        records = await result.data()

    logger.info(f"直接查询到 {len(records)} 个节点")

    for i, record in enumerate(records[:5]):  # 只显示前5个
        node = record["n"]
        labels = record["labels"]
        properties = dict(node)
        logger.info(f"节点 {i+1}:")
        logger.info(f"  标签: {labels}")
        logger.info(f"  属性: {properties}")

    return records


async def test_service_query():
    """使用QueryService查询节点"""
    logger.info("\n执行服务查询...")
    query_service = QueryService()

    # 创建一个空的过滤器，应该返回所有节点
    filter = NodeFilter(limit=100, offset=0)

    # 执行查询
    nodes = await query_service.query_nodes(filter=filter)

    logger.info(f"服务查询到 {len(nodes)} 个节点")
    for i, node in enumerate(nodes[:5]):  # 只显示前5个
        logger.info(f"节点 {i+1}:")
        logger.info(f"  ID: {node.id}")
        logger.info(f"  类型: {node.type}")
        logger.info(f"  属性: {node.properties}")

    return nodes


async def test_node_type_validation():
    """测试节点类型验证逻辑"""
    logger.info("\n测试节点类型验证...")

    # 直接查询数据库获取节点数据，然后手动执行类型验证逻辑
    async with neo4j_connection.get_session() as session:
        query = "MATCH (n) RETURN n, labels(n) AS labels LIMIT 100"
        result = await session.run(query)
        records = await result.data()

    logger.info(f"开始验证 {len(records)} 个节点的类型...")

    valid_nodes = []
    skipped_nodes = []

    for record in records:
        neo4j_node = record["n"]
        node_data = dict(neo4j_node)
        labels = record.get("labels", [])

        # 手动执行类型验证逻辑
        node_type_value = None
        if labels:
            # 从标签中找到有效的 NodeType
            for label in labels:
                if label in NodeType._value2member_map_:
                    node_type_value = label
                    break
        if not node_type_value:
            # 从节点属性中获取类型
            node_type_value = node_data.get("type")

        # 检查是否有效
        if not node_type_value or node_type_value not in NodeType._value2member_map_:
            skipped_nodes.append(
                {
                    "labels": labels,
                    "type_from_property": node_data.get("type"),
                    "properties": node_data,
                }
            )
        else:
            valid_nodes.append(
                {
                    "labels": labels,
                    "valid_type": node_type_value,
                    "properties": node_data,
                }
            )

    logger.info(f"有效节点数: {len(valid_nodes)}")
    logger.info(f"被跳过的节点数: {len(skipped_nodes)}")

    if skipped_nodes:
        logger.info("\n被跳过的节点详情:")
        for i, node in enumerate(skipped_nodes[:3]):  # 只显示前3个
            logger.info(f"节点 {i+1}:")
            logger.info(f"  标签: {node['labels']}")
            logger.info(f"  属性中的类型: {node['type_from_property']}")
            logger.info(f"  属性: {node['properties']}")

    return valid_nodes, skipped_nodes


async def main():
    """主函数"""
    logger.info("=== 开始调试节点查询逻辑 ===")

    try:
        # 初始化数据库连接
        await init_database()
        logger.info("数据库连接成功")

        # 测试1：直接查询
        direct_records = await test_direct_query()

        # 测试2：服务查询
        service_nodes = await test_service_query()

        # 测试3：验证节点类型逻辑
        valid_nodes, skipped_nodes = await test_node_type_validation()

        logger.info("\n=== 调试完成 ===")
        logger.info(f"直接查询节点数: {len(direct_records)}")
        logger.info(f"服务查询节点数: {len(service_nodes)}")
        logger.info(f"类型验证通过节点数: {len(valid_nodes)}")
        logger.info(f"类型验证跳过节点数: {len(skipped_nodes)}")

        if len(direct_records) > 0 and len(service_nodes) == 0:
            logger.warning("发现问题：数据库中有节点，但服务查询返回空结果！")
            logger.warning("可能的原因：节点类型验证失败")

    except Exception as e:
        logger.error(f"测试过程中发生错误: {str(e)}")
        import traceback

        traceback.print_exc()
    finally:
        # 关闭数据库连接
        await close_database()
        logger.info("数据库连接已关闭")


if __name__ == "__main__":
    asyncio.run(main())
