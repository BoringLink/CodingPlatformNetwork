"""为数据库中的所有节点添加UUID格式的id属性"""

import asyncio
import logging
import uuid

from app.database import init_database, close_database, neo4j_connection

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def add_uuid_to_all_nodes():
    """为所有节点添加UUID格式的id属性"""
    logger.info("开始为所有节点添加UUID格式的id...")

    # 初始化数据库连接
    await init_database()
    logger.info("数据库连接成功")

    try:
        async with neo4j_connection.get_session() as session:
            # 统计当前没有id的节点数量
            count_query = "MATCH (n) WHERE n.id IS NULL RETURN count(n) AS count"
            count_result = await session.run(count_query)
            count_record = await count_result.single()
            nodes_without_id = count_record["count"] if count_record else 0

            logger.info(f"发现 {nodes_without_id} 个节点没有id属性")

            if nodes_without_id == 0:
                logger.info("所有节点都已经有id属性，无需处理")
                return

            total_processed = 0
            batch_size = 1000

            while True:
                # 获取当前批次的没有id的节点
                query = "MATCH (n) WHERE n.id IS NULL RETURN id(n) AS node_id, labels(n) AS labels LIMIT $batch_size"
                result = await session.run(query, batch_size=batch_size)
                records = await result.data()

                if not records:
                    break

                batch_count = len(records)
                logger.info(
                    f"开始处理第 {total_processed // batch_size + 1} 批，共 {batch_count} 个节点"
                )

                # 为每个节点添加UUID格式的id
                for record in records:
                    node_internal_id = record["node_id"]
                    labels = record["labels"]

                    # 生成UUID作为id
                    new_id = str(uuid.uuid4())

                    # 更新节点
                    update_query = "MATCH (n) WHERE id(n) = $node_id SET n.id = $new_id RETURN labels(n) AS labels"
                    await session.run(
                        update_query, node_id=node_internal_id, new_id=new_id
                    )

                    logger.info(
                        f"为节点 {node_internal_id} 添加id: {new_id}, 标签: {labels}"
                    )

                total_processed += batch_count
                logger.info(f"已成功处理 {total_processed} 个节点")

                # 检查是否还有剩余节点
                count_result = await session.run(count_query)
                count_record = await count_result.single()
                remaining_nodes = count_record["count"] if count_record else 0

                logger.info(f"剩余 {remaining_nodes} 个节点需要处理")

            logger.info(
                f"所有节点处理完成，共为 {total_processed} 个节点添加了UUID格式的id"
            )
            logger.info("所有节点都已添加id属性")

    except Exception as e:
        logger.error(f"处理过程中发生错误: {str(e)}")
        import traceback

        traceback.print_exc()
    finally:
        # 关闭数据库连接
        await close_database()
        logger.info("数据库连接已关闭")


if __name__ == "__main__":
    asyncio.run(add_uuid_to_all_nodes())
