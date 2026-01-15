"""图服务模块"""

import asyncio
from typing import Dict, List, Optional, Tuple, Any, Type, cast, Union
from neo4j import AsyncSession
from pydantic import ValidationError
import structlog

from app.database import neo4j_connection
from app.models.nodes import Node, NodeType, StudentNodeProperties, KnowledgePointNodeProperties
from app.models.relationships import Relationship, RelationshipType
from app.models.visualization import (
    GraphVisualization,
    NodeVisualization,
    EdgeVisualization,
    VisualizationOptions,
)
from app.services.visualization_service import VisualizationService
from app.services.query_service import query_service

logger = structlog.get_logger(__name__)


class GraphService:
    """图服务类，提供图数据库操作相关的服务"""

    def __init__(self):
        """初始化图服务"""
        self.visualization_service = VisualizationService()

    async def create_node(
        self,
        node_type: NodeType,
        properties: Dict[str, Any],
    ) -> Node:
        """创建节点

        创建一个新的节点

        Args:
            node_type: 节点类型
            properties: 节点属性

        Returns:
            创建的节点

        Raises:
            RuntimeError: 如果数据库操作失败
        """
        try:
            async with neo4j_connection.get_session() as session:
                # 生成节点属性映射
                property_keys = []
                property_values = []
                for key, value in properties.items():
                    property_keys.append(f"{key}: ${key}")
                    property_values.append(value)

                # 构建创建节点的 Cypher 查询
                create_query = f"""
                CREATE (n:{node_type.value} {{{', '.join(property_keys)}}})
                RETURN n, id(n) as node_id
                """

                result = await session.run(create_query, **properties)
                record = await result.single()

                if not record:
                    raise RuntimeError(f"Failed to create {node_type} node")

                node = record["n"]
                node_id = record["node_id"]

                # 构建节点对象
                node = Node(
                    id=node_id,
                    type=node_type,
                    properties=dict(node),
                )

                logger.info(
                    "node_created",
                    node_type=node_type,
                    node_id=node_id,
                )

                return node
        except Exception as e:
            logger.error(
                "failed_to_create_node",
                node_type=node_type,
                properties=properties,
                error=str(e),
            )
            raise RuntimeError(f"Failed to create node: {e}")

    async def update_node(
        self,
        node_id: str,
        properties: Dict[str, Any],
    ) -> Node:
        """更新节点

        更新指定 ID 的节点属性

        Args:
            node_id: 节点 ID
            properties: 要更新的属性

        Returns:
            更新后的节点

        Raises:
            RuntimeError: 如果数据库操作失败
        """
        try:
            async with neo4j_connection.get_session() as session:
                # 构建更新节点的 Cypher 查询
                update_query = """
                MATCH (n) WHERE id(n) = $node_id
                SET n += $properties
                RETURN n, id(n) as node_id
                """

                result = await session.run(
                    update_query,
                    node_id=node_id,
                    properties=properties,
                )
                record = await result.single()

                if not record:
                    raise ValueError(f"Node not found: {node_id}")

                node_data = dict(record["n"])
                node = Node(
                    id=record["node_id"],
                    type=NodeType(node_data["labels"][0]),
                    properties=node_data,
                )

                logger.info("node_updated", node_id=node_id, properties=properties)

                return node
        except Exception as e:
            logger.error("failed_to_update_node", node_id=node_id, error=str(e))
            raise RuntimeError(f"Failed to update node: {e}")

    async def get_node(
        self,
        node_id: str,
        node_type: Optional[NodeType] = None,
    ) -> Optional[Node]:
        """获取节点

        根据 ID 获取节点

        Args:
            node_id: 节点 ID
            node_type: 节点类型（可选）

        Returns:
            节点对象，如果不存在则返回 None

        Raises:
            RuntimeError: 如果数据库操作失败
        """
        try:
            async with neo4j_connection.get_session() as session:
                # 构建查询
                if node_type:
                    query = f"""
                    MATCH (n:{node_type.value}) WHERE id(n) = $node_id
                    RETURN n, id(n) as node_id
                    """
                else:
                    query = """
                    MATCH (n) WHERE id(n) = $node_id
                    RETURN n, id(n) as node_id, labels(n) as labels
                    """

                result = await session.run(query, node_id=node_id)
                record = await result.single()

                if not record:
                    logger.info("node_not_found", node_id=node_id, node_type=node_type)
                    return None

                node_data = dict(record["n"])
                node_id = record["node_id"]
                labels = record.get("labels", [])

                # 确定节点类型
                node_type = None
                for label in labels:
                    try:
                        node_type = NodeType(label)
                        break
                    except ValueError:
                        continue

                if not node_type:
                    logger.warning(
                        "unknown_node_type",
                        node_id=node_id,
                        labels=labels,
                    )
                    return None

                node = Node(
                    id=node_id,
                    type=node_type,
                    properties=node_data,
                )

                logger.info("node_retrieved", node_id=node_id, node_type=node_type)

                return node
        except Exception as e:
            logger.error("failed_to_get_node", node_id=node_id, error=str(e))
            raise RuntimeError(f"Failed to get node: {e}")

    async def get_all_nodes(
        self,
        node_type: Optional[NodeType] = None,
        limit: int = 1000,
    ) -> List[Node]:
        """获取所有节点

        Args:
            node_type: 节点类型（可选）
            limit: 返回结果的最大数量

        Returns:
            节点列表

        Raises:
            RuntimeError: 如果数据库操作失败
        """
        try:
            async with neo4j_connection.get_session() as session:
                if node_type:
                    query = f"""
                    MATCH (n:{node_type.value})
                    RETURN n, id(n) as node_id, labels(n) as labels
                    LIMIT $limit
                    """
                else:
                    query = """
                    MATCH (n)
                    RETURN n, id(n) as node_id, labels(n) as labels
                    LIMIT $limit
                    """

                result = await session.run(query, limit=limit)
                records = await result.data()

                nodes = []
                for record in records:
                    node_data = dict(record["n"])
                    node_id = record["node_id"]
                    labels = record["labels"]

                    # 确定节点类型
                    node_type = None
                    for label in labels:
                        try:
                            node_type = NodeType(label)
                            break
                        except ValueError:
                            continue

                    if not node_type:
                        logger.warning(
                            "unknown_node_type",
                            node_id=node_id,
                            labels=labels,
                        )
                        continue

                    node = Node(
                        id=node_id,
                        type=node_type,
                        properties=node_data,
                    )
                    nodes.append(node)

                logger.info("nodes_retrieved", count=len(nodes), node_type=node_type)

                return nodes
        except Exception as e:
            logger.error("failed_to_get_all_nodes", error=str(e), node_type=node_type)
            raise RuntimeError(f"Failed to get all nodes: {e}")

    async def delete_node(self, node_id: str) -> bool:
        """删除节点

        删除指定 ID 的节点

        Args:
            node_id: 节点 ID

        Returns:
            如果删除成功返回 True，否则返回 False

        Raises:
            RuntimeError: 如果数据库操作失败
        """
        try:
            async with neo4j_connection.get_session() as session:
                delete_query = """
                MATCH (n) WHERE id(n) = $node_id
                DETACH DELETE n
                RETURN count(n) as deleted_count
                """

                result = await session.run(delete_query, node_id=node_id)
                record = await result.single()

                deleted = record["deleted_count"] > 0

                if deleted:
                    logger.info("node_deleted", node_id=node_id)
                else:
                    logger.info("node_not_found_for_deletion", node_id=node_id)

                return deleted
        except Exception as e:
            logger.error("failed_to_delete_node", node_id=node_id, error=str(e))
            raise RuntimeError(f"Failed to delete node: {e}")

    async def create_relationship(
        self,
        from_node_id: str,
        to_node_id: str,
        relationship_type: RelationshipType,
        properties: Optional[Dict[str, Any]] = None,
    ) -> Relationship:
        """创建关系

        在两个节点之间创建关系

        Args:
            from_node_id: 起始节点 ID
            to_node_id: 目标节点 ID
            relationship_type: 关系类型
            properties: 关系属性

        Returns:
            创建的关系

        Raises:
            RuntimeError: 如果数据库操作失败
        """
        try:
            async with neo4j_connection.get_session() as session:
                # 构建创建关系的 Cypher 查询
                create_query = f"""
                MATCH (from_node), (to_node)
                WHERE id(from_node) = $from_node_id AND id(to_node) = $to_node_id
                CREATE (from_node)-[r:{relationship_type.value}]->(to_node)
                RETURN r, id(r) as rel_id
                """

                result = await session.run(
                    create_query,
                    from_node_id=from_node_id,
                    to_node_id=to_node_id,
                    **(properties or {}),
                )
                record = await result.single()

                if not record:
                    raise RuntimeError(
                        f"Failed to create relationship between nodes {from_node_id} and {to_node_id}"
                    )

                rel_data = dict(record["r"])
                rel_id = record["rel_id"]

                relationship = Relationship(
                    id=rel_id,
                    type=relationship_type,
                    from_node_id=from_node_id,
                    to_node_id=to_node_id,
                    properties=rel_data,
                )

                logger.info(
                    "relationship_created",
                    from_node_id=from_node_id,
                    to_node_id=to_node_id,
                    relationship_type=relationship_type,
                )

                return relationship
        except Exception as e:
            logger.error(
                "failed_to_create_relationship",
                from_node_id=from_node_id,
                to_node_id=to_node_id,
                relationship_type=relationship_type,
                error=str(e),
            )
            raise RuntimeError(f"Failed to create relationship: {e}")

    async def update_relationship(
        self,
        relationship_id: str,
        properties: Dict[str, Any],
    ) -> Relationship:
        """更新关系

        更新指定 ID 的关系属性

        Args:
            relationship_id: 关系 ID
            properties: 要更新的属性

        Returns:
            更新后的关系

        Raises:
            RuntimeError: 如果数据库操作失败
        """
        try:
            async with neo4j_connection.get_session() as session:
                # 获取关系的起始和目标节点 ID
                get_nodes_query = """
                MATCH ()-[r]-() WHERE id(r) = $rel_id
                RETURN startNode(r) as from_node, endNode(r) as to_node
                """

                result = await session.run(get_nodes_query, rel_id=relationship_id)
                record = await result.single()

                if not record:
                    raise ValueError(f"Relationship not found: {relationship_id}")

                from_node_id = record["from_node"].id
                to_node_id = record["to_node"].id

                # 更新关系属性
                update_query = """
                MATCH ()-[r]-() WHERE id(r) = $rel_id
                SET r += $properties
                RETURN r, id(r) as rel_id
                """

                result = await session.run(
                    update_query,
                    rel_id=relationship_id,
                    properties=properties,
                )
                updated_rel = await result.single()

                if not updated_rel:
                    raise ValueError(f"Relationship not found: {relationship_id}")

                rel_data = dict(updated_rel["r"])
                rel_id = updated_rel["rel_id"]

                relationship = Relationship(
                    id=rel_id,
                    type=RelationshipType(rel_data["type"]),
                    from_node_id=from_node_id,
                    to_node_id=to_node_id,
                    properties=rel_data,
                )

                logger.info(
                    "relationship_updated",
                    relationship_id=relationship_id,
                    properties=properties,
                )

                return relationship
        except Exception as e:
            logger.error(
                "failed_to_update_relationship",
                relationship_id=relationship_id,
                properties=properties,
                error=str(e),
            )
            raise RuntimeError(f"Failed to update relationship: {e}")

    async def delete_relationship(self, relationship_id: str) -> bool:
        """删除关系

        删除指定 ID 的关系

        Args:
            relationship_id: 关系 ID

        Returns:
            如果删除成功返回 True，否则返回 False

        Raises:
            RuntimeError: 如果数据库操作失败
        """
        try:
            async with neo4j_connection.get_session() as session:
                # 删除关系
                delete_query = """
                MATCH ()-[r]-() WHERE id(r) = $rel_id
                DELETE r
                RETURN count(r) as deleted_count
                """

                result = await session.run(delete_query, rel_id=relationship_id)
                record = await result.single()

                deleted = record["deleted_count"] > 0

                if deleted:
                    logger.info("relationship_deleted", relationship_id=relationship_id)
                else:
                    logger.info("relationship_not_found_for_deletion", relationship_id=relationship_id)

                return deleted
        except Exception as e:
            logger.error("failed_to_delete_relationship", relationship_id=relationship_id, error=str(e))
            raise RuntimeError(f"Failed to delete relationship: {e}")

    async def get_relationships(
        self,
        from_node_id: Optional[str] = None,
        to_node_id: Optional[str] = None,
        relationship_type: Optional[RelationshipType] = None,
    ) -> List[Relationship]:
        """获取关系

        获取满足条件的关系列表

        Args:
            from_node_id: 起始节点 ID（可选）
            to_node_id: 目标节点 ID（可选）
            relationship_type: 关系类型（可选）

        Returns:
            关系列表

        Raises:
            RuntimeError: 如果数据库操作失败
        """
        try:
            async with neo4j_connection.get_session() as session:
                # 构建查询条件
                conditions = []
                params = {}

                # 构建 MATCH 子句
                match_parts = ["()"]

                if from_node_id:
                    match_parts.append(f"-[:{{relationship_type.value if relationship_type else ''}}]->()")
                    conditions.append(f"id(start_node) = $from_node_id")
                    params["from_node_id"] = from_node_id

                if to_node_id:
                    match_parts.append(f"<-[:{{relationship_type.value if relationship_type else ''}}]-")
                    conditions.append(f"id(end_node) = $to_node_id")
                    params["to_node_id"] = to_node_id

                match_clause = "MATCH " + "".join(match_parts)

                # 构建 WHERE 子句
                where_clause = f" WHERE {' AND '.join(conditions)}" if conditions else ""

                # 构建完整查询
                query = f"""{match_clause}{where_clause}
                RETURN start_node, r, end_node
                """

                result = await session.run(query, **params)
                records = await result.data()

                relationships = []
                for record in records:
                    rel_data = dict(record["r"])
                    rel_type = RelationshipType(record["r"].type)
                    rel_id = record["rel_id"]

                    relationship = Relationship(
                        id=rel_id,
                        type=rel_type,
                        from_node_id=record["start_node"].id,
                        to_node_id=record["end_node"].id,
                        properties=rel_data,
                    )
                    relationships.append(relationship)

                logger.info(
                    "relationships_retrieved",
                    count=len(relationships),
                    from_node_id=from_node_id,
                    to_node_id=to_node_id,
                    relationship_type=relationship_type,
                )

                return relationships
        except Exception as e:
            logger.error(
                "failed_to_get_relationships",
                from_node_id=from_node_id,
                to_node_id=to_node_id,
                relationship_type=relationship_type,
                error=str(e),
            )
            raise RuntimeError(f"Failed to get relationships: {e}")

    async def visualize_graph(
        self,
        options: VisualizationOptions,
    ) -> GraphVisualization:
        """可视化图数据

        根据提供的选项可视化图数据

        Args:
            options: 可视化选项

        Returns:
            图可视化数据

        Raises:
            RuntimeError: 如果数据库操作失败
        """
        try:
            # 1. 使用visualization options中的参数查询子图
            subgraph = await query_service.query_subgraph(
                root_node_id=options.root_node_id,
                depth=options.depth,
                filter=None,  # 暂时不使用filter，后续可扩展
                max_nodes=1000,
                max_relationships=5000
            )
            
            # 2. 使用visualization_service生成可视化数据
            # 注意：visualization_service.generate_visualization 接收 Subgraph 和 VisualizationOptions
            viz_data = await self.visualization_service.generate_visualization(subgraph)
            
            # 3. 转换为 GraphVisualization 类型
            nodes = [
                NodeVisualization(
                    id=node.id,
                    type=node.type,
                    label=node.label,
                    properties={},
                    size=node.size,
                    color=node.color
                )
                for node in viz_data.nodes
            ]
            
            edges = [
                EdgeVisualization(
                    id=edge.id,
                    type=edge.type,
                    source=edge.source,
                    target=edge.target,
                    label=edge.label,
                    properties={},
                    weight=edge.weight
                )
                for edge in viz_data.edges
            ]
            
            return GraphVisualization(
                nodes=nodes,
                edges=edges
            )
        except Exception as e:
            logger.error("failed_to_visualize_graph", error=str(e))
            raise RuntimeError(f"Failed to visualize graph: {e}")


# 全局图服务实例
graph_service = GraphService()
