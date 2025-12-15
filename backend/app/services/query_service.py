"""图查询服务

提供节点、关系、子图以及路径查询能力，供可视化和业务接口使用。
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional
import structlog

from app.database import neo4j_connection
from app.models.nodes import Node, NodeType
from app.models.relationships import Relationship, RelationshipType

logger = structlog.get_logger()


class NodeFilter:
    """节点查询过滤器"""

    def __init__(
        self,
        types: Optional[List[NodeType]] = None,
        properties: Optional[Dict[str, Any]] = None,
        date_range: Optional[Dict[str, Any]] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ):
        self.types = types
        self.properties = properties or {}
        self.date_range = date_range
        self.limit = limit
        self.offset = offset or 0


class RelationshipFilter:
    """关系查询过滤器"""

    def __init__(
        self,
        types: Optional[List[RelationshipType]] = None,
        from_node_id: Optional[str] = None,
        to_node_id: Optional[str] = None,
        properties: Optional[Dict[str, Any]] = None,
        min_weight: Optional[float] = None,
        max_weight: Optional[float] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ):
        self.types = types
        self.from_node_id = from_node_id
        self.to_node_id = to_node_id
        self.properties = properties or {}
        self.min_weight = min_weight
        self.max_weight = max_weight
        self.limit = limit
        self.offset = offset or 0


class GraphFilter:
    """子图过滤条件"""

    def __init__(
        self,
        node_types: Optional[List[NodeType]] = None,
        relationship_types: Optional[List[RelationshipType]] = None,
        date_range: Optional[Dict[str, Any]] = None,
    ):
        self.node_types = node_types
        self.relationship_types = relationship_types
        self.date_range = date_range

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, GraphFilter):
            return False
        return (
            self.node_types == other.node_types
            and self.relationship_types == other.relationship_types
            and self.date_range == other.date_range
        )


class Subgraph:
    """子图数据结构"""

    def __init__(
        self,
        nodes: List[Node],
        relationships: List[Relationship],
        metadata: Optional[Dict[str, Any]] = None,
    ):
        self.nodes = nodes
        self.relationships = relationships
        self.metadata = metadata or {
            "node_count": len(nodes),
            "relationship_count": len(relationships),
        }

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Subgraph):
            return False
        return (
            self.nodes == other.nodes
            and self.relationships == other.relationships
            and self.metadata == other.metadata
        )

    def to_dict(self) -> Dict[str, Any]:
        """将子图转换为字典格式"""
        return {
            "nodes": [node.to_dict() for node in self.nodes],
            "relationships": [rel.to_dict() for rel in self.relationships],
            "metadata": self.metadata,
        }


class Path:
    """路径结果"""

    def __init__(
        self,
        nodes: List[Node],
        relationships: List[Relationship],
        length: int,
    ):
        self.nodes = nodes
        self.relationships = relationships
        self.length = length


class QueryService:
    """查询服务"""

    async def query_nodes(self, filter: NodeFilter) -> List[Node]:
        """按过滤条件查询节点"""

        query = "MATCH (n)"
        where_clauses: List[str] = []
        params: Dict[str, Any] = {}

        if filter.types:
            params["types"] = [t.value for t in filter.types]
            where_clauses.append("ANY(label IN labels(n) WHERE label IN $types)")

        for idx, (key, value) in enumerate(filter.properties.items()):
            param_name = f"prop_{idx}"
            where_clauses.append(f"n.{key} = ${param_name}")
            params[param_name] = value

        if where_clauses:
            query += " WHERE " + " AND ".join(where_clauses)

        query += " RETURN n, labels(n) AS labels"

        if filter.limit is not None:
            query += " SKIP $offset LIMIT $limit"
            params["offset"] = filter.offset
            params["limit"] = filter.limit

        async with neo4j_connection.get_session() as session:
            result = await session.run(query, **params)
            records = await result.data()

        nodes: List[Node] = []
        for record in records:
            neo4j_node = record["n"]
            node_data = dict(neo4j_node)
            node_id = node_data.pop("id", None)
            created_at_raw = node_data.pop("created_at", None)
            updated_at_raw = node_data.pop("updated_at", None)
            labels = record.get("labels") or list(getattr(neo4j_node, "labels", []))

            # 处理节点类型，确保只使用有效的 NodeType
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

            # 如果找不到有效的 NodeType，跳过该节点
            if (
                not node_type_value
                or node_type_value not in NodeType._value2member_map_
            ):
                logger.warning(
                    "skipping_node_with_invalid_type",
                    node_id=node_id,
                    labels=labels,
                    type=node_type_value,
                )
                continue

            node_type = NodeType(node_type_value)

            created_at = (
                datetime.fromisoformat(created_at_raw)
                if isinstance(created_at_raw, str)
                else created_at_raw or datetime.utcnow()
            )
            updated_at = (
                datetime.fromisoformat(updated_at_raw)
                if isinstance(updated_at_raw, str)
                else updated_at_raw or datetime.utcnow()
            )

            if filter.date_range:
                start = (
                    filter.date_range.get("start")
                    if isinstance(filter.date_range, dict)
                    else None
                )
                end = (
                    filter.date_range.get("end")
                    if isinstance(filter.date_range, dict)
                    else None
                )
                if start and created_at < start:
                    continue
                if end and created_at > end:
                    continue

            nodes.append(
                Node(
                    id=node_id,
                    type=node_type,
                    properties=node_data,
                    created_at=created_at,
                    updated_at=updated_at,
                )
            )

        logger.info("query_nodes_completed", count=len(nodes))
        return nodes

    async def query_relationships(
        self, filter: RelationshipFilter
    ) -> List[Relationship]:
        """按过滤条件查询关系"""

        query = "MATCH (from)-[r]->(to)"
        where_clauses: List[str] = []
        params: Dict[str, Any] = {}

        if filter.types:
            params["types"] = [t.value for t in filter.types]
            where_clauses.append("type(r) IN $types")

        if filter.from_node_id:
            params["from_node_id"] = filter.from_node_id
            where_clauses.append("from.id = $from_node_id")

        if filter.to_node_id:
            params["to_node_id"] = filter.to_node_id
            where_clauses.append("to.id = $to_node_id")

        for idx, (key, value) in enumerate(filter.properties.items()):
            param_name = f"rprop_{idx}"
            where_clauses.append(f"r.{key} = ${param_name}")
            params[param_name] = value

        if where_clauses:
            query += " WHERE " + " AND ".join(where_clauses)

        query += " RETURN r {.* , id:id(r), type:type(r), from_id:from.id, to_id:to.id} AS rel"

        if filter.limit is not None:
            query += " SKIP $offset LIMIT $limit"
            params["offset"] = filter.offset
            params["limit"] = filter.limit

        async with neo4j_connection.get_session() as session:
            result = await session.run(query, **params)
            records = await result.data()

        relationships: List[Relationship] = []
        for record in records:
            rel_data = dict(record["rel"])
            rel_id_raw = rel_data.pop("id", None)
            rel_type_value = rel_data.pop("type", None)
            from_id = rel_data.pop("from_id", None)
            to_id = rel_data.pop("to_id", None)
            rel_type = RelationshipType(rel_type_value)
            rel_id = str(rel_id_raw) if rel_id_raw is not None else None

            weight = rel_data.get("weight")

            if filter.min_weight is not None and (
                weight is None or weight < filter.min_weight
            ):
                continue
            if (
                filter.max_weight is not None
                and weight is not None
                and weight > filter.max_weight
            ):
                continue

            relationships.append(
                Relationship(
                    id=rel_id,
                    type=rel_type,
                    from_node_id=from_id,
                    to_node_id=to_id,
                    properties=rel_data,
                    weight=weight,
                )
            )

        logger.info("query_relationships_completed", count=len(relationships))
        return relationships

    async def query_subgraph(
        self,
        root_node_id: str,
        depth: int,
        filter: Optional[GraphFilter] = None,
        limit: Optional[int] = None,
    ) -> Subgraph:
        """查询指定深度的子图"""

        if depth < 1:
            raise ValueError("Depth must be at least 1")

        # 先检查根节点是否存在
        async with neo4j_connection.get_session() as session:
            exists_result = await session.run(
                "MATCH (n {id: $root_id}) RETURN count(n) as cnt",
                root_id=root_node_id,
            )
            exists_record = await exists_result.single()
            if not exists_record or exists_record["cnt"] == 0:
                # 如果根节点不存在，返回空的子图
                return Subgraph(
                    nodes=[],
                    relationships=[],
                    metadata={"node_count": 0, "relationship_count": 0},
                )

            # 构建基础查询
            query = (
                f"MATCH p=(root {{id: $root_id}})-[r*..{depth}]-(n) "
                "RETURN "
                "[node IN nodes(p) | node {.* , id: node.id, labels: labels(node)}] AS nodes, "
                "[rel IN relationships(p) | rel {.* , id: id(rel), type: type(rel), from_id: startNode(rel).id, to_id: endNode(rel).id}] AS rels "
            )
            
            # 条件性添加 LIMIT 子句
            if limit is not None:
                query += " LIMIT $limit"
            
            # 准备参数
            params = {
                "root_id": root_node_id
            }
            if limit is not None:
                params["limit"] = limit
            
            result = await session.run(
                query,
                **params
            )
            records = await result.data()

        node_map: Dict[str, Node] = {}
        rel_map: Dict[str, Relationship] = {}

        # 1. 处理子图查询结果
        for record in records:
            for neo_node in record.get("nodes", []):
                node = self._convert_node(neo_node)
                if self._node_passes_filter(node, filter):
                    node_map[node.id] = node

            for neo_rel in record.get("rels", []):
                rel = self._convert_relationship(neo_rel)
                if self._relationship_passes_filter(rel, filter):
                    rel_map[rel.id] = rel

        # 2. 添加所有符合筛选条件的节点（包括孤立节点）
        all_nodes_filter = NodeFilter(
            types=filter.node_types if filter else None,
            limit=None,  # 不限制数量，确保获取所有符合条件的节点
        )
        all_matching_nodes = await self.query_nodes(all_nodes_filter)

        # 合并所有符合条件的节点
        for node in all_matching_nodes:
            if self._node_passes_filter(node, filter):
                node_map[node.id] = node

        # 3. 如果有节点过滤，确保关系两端都在节点集合中
        if filter and filter.node_types:
            rel_map = {
                rel_id: rel
                for rel_id, rel in rel_map.items()
                if rel.from_node_id in node_map and rel.to_node_id in node_map
            }

        nodes = list(node_map.values())
        relationships = list(rel_map.values())

        subgraph = Subgraph(
            nodes=nodes,
            relationships=relationships,
            metadata={
                "node_count": len(nodes),
                "relationship_count": len(relationships),
            },
        )

        # LLM 增强：可选，失败时忽略
        await self._maybe_enhance_with_llm(subgraph)

        logger.info(
            "query_subgraph_completed",
            node_count=len(nodes),
            relationship_count=len(relationships),
            include_isolated_nodes=True,
        )
        return subgraph

    async def find_path(
        self,
        from_node_id: str,
        to_node_id: str,
        max_depth: int,
        limit: int = 5,
        relationship_types: Optional[List[RelationshipType]] = None,
    ) -> List[Path]:
        """查找两节点之间的路径"""

        if max_depth < 1:
            raise ValueError("Max depth must be at least 1")

        where_rel = ""
        params: Dict[str, Any] = {
            "from_id": from_node_id,
            "to_id": to_node_id,
            "limit": limit,
        }

        if relationship_types:
            params["rel_types"] = [rt.value for rt in relationship_types]
            where_rel = (
                " WHERE ALL(rt IN relationships(p) WHERE type(rt) IN $rel_types)"
            )

        query = (
            f"MATCH p=(from {{id: $from_id}})-[*..{max_depth}]-(to {{id: $to_id}})"
            f"{where_rel} "
            "RETURN "
            "[node IN nodes(p) | node {.* , id: node.id, labels: labels(node)}] AS nodes, "
            "[rel IN relationships(p) | rel {.* , id: id(rel), type: type(rel), from_id: startNode(rel).id, to_id: endNode(rel).id}] AS rels, "
            "length(p) AS len "
            "ORDER BY len ASC "
            "LIMIT $limit"
        )

        async with neo4j_connection.get_session() as session:
            result = await session.run(query, **params)
            records = await result.data()

        paths: List[Path] = []
        for record in records:
            nodes = [self._convert_node(n) for n in record.get("nodes", [])]
            relationships = [
                self._convert_relationship(r) for r in record.get("rels", [])
            ]
            paths.append(
                Path(
                    nodes=nodes,
                    relationships=relationships,
                    length=record.get("len", len(relationships)),
                )
            )

        logger.info("find_path_completed", path_count=len(paths))
        return paths

    def _convert_node(self, neo_node: Any) -> Node:
        node_data = dict(neo_node)
        node_id = node_data.pop("id", None)
        created_at_raw = node_data.pop("created_at", None)
        updated_at_raw = node_data.pop("updated_at", None)
        labels = list(getattr(neo_node, "labels", []))
        node_type_value = None

        if labels:
            node_type_value = next(
                (lbl for lbl in labels if lbl in NodeType._value2member_map_),
                labels[0],
            )
        if not node_type_value:
            node_type_value = node_data.get("type")

        if not node_type_value:
            logger.warning(
                "node_type_missing",
                node_id=node_id,
                labels=labels,
                properties=list(node_data.keys()),
            )
            node_type_value = NodeType.STUDENT.value

        node_type = NodeType(node_type_value)

        created_at = (
            datetime.fromisoformat(created_at_raw)
            if isinstance(created_at_raw, str)
            else created_at_raw or datetime.utcnow()
        )
        updated_at = (
            datetime.fromisoformat(updated_at_raw)
            if isinstance(updated_at_raw, str)
            else updated_at_raw or datetime.utcnow()
        )

        return Node(
            id=node_id,
            type=node_type,
            properties=node_data,
            created_at=created_at,
            updated_at=updated_at,
        )

    def _convert_relationship(self, rel: Any) -> Relationship:
        # Prefer dictionary payloads produced by Cypher projections
        if isinstance(rel, dict):
            rel_type_raw = rel.get("type") or rel.get("label")
            if rel_type_raw is None:
                raise ValueError("Relationship missing type/label")

            from_id = rel.get("from_id") or rel.get("start") or rel.get("source")
            to_id = rel.get("to_id") or rel.get("end") or rel.get("target")
            if from_id is None or to_id is None:
                raise ValueError("Relationship missing endpoints")

            rel_id_raw = rel.get("id") or rel.get("element_id")
            props = {
                k: v
                for k, v in rel.items()
                if k
                not in {
                    "id",
                    "element_id",
                    "type",
                    "label",
                    "from_id",
                    "to_id",
                    "start",
                    "end",
                    "source",
                    "target",
                }
            }

            rel_type = (
                rel_type_raw
                if isinstance(rel_type_raw, RelationshipType)
                else RelationshipType(rel_type_raw)
            )
            rel_id = str(rel_id_raw) if rel_id_raw is not None else None
            return Relationship(
                id=rel_id,
                type=rel_type,
                from_node_id=from_id,
                to_node_id=to_id,
                properties=props or None,
                weight=props.get("weight") if props else None,
            )

        # Fallback for raw Neo4j relationship objects (when no projection applied)
        if neo4j.Relationship is not None and isinstance(rel, neo4j.Relationship):  # type: ignore[attr-defined]
            rel_data = dict(rel)
            rel_id_raw = getattr(rel, "id", None)
            rel_type = RelationshipType(getattr(rel, "type"))
            from_id = rel.start_node.get("id")  # type: ignore[attr-defined]
            to_id = rel.end_node.get("id")  # type: ignore[attr-defined]
            if from_id is None or to_id is None:
                raise ValueError("Relationship missing endpoints")

            rel_id = str(rel_id_raw) if rel_id_raw is not None else None
            return Relationship(
                id=rel_id,
                type=rel_type,
                from_node_id=from_id,
                to_node_id=to_id,
                properties=rel_data or None,
                weight=rel_data.get("weight"),
            )

        raise ValueError(f"Unsupported relationship type: {type(rel)}")

    def _node_passes_filter(self, node: Node, filter: Optional[GraphFilter]) -> bool:
        if filter is None:
            return True
        # 如果node_types是列表（包括空列表），则仅返回列表中包含的节点
        if filter.node_types is not None:
            if node.type not in filter.node_types:
                return False
        if filter.date_range:
            start = (
                filter.date_range.get("start")
                if isinstance(filter.date_range, dict)
                else None
            )
            end = (
                filter.date_range.get("end")
                if isinstance(filter.date_range, dict)
                else None
            )
            if start and node.created_at < start:
                return False
            if end and node.created_at > end:
                return False
        return True

    def _relationship_passes_filter(
        self, rel: Relationship, filter: Optional[GraphFilter]
    ) -> bool:
        if filter is None:
            return True
        # 如果relationship_types是列表（包括空列表），则仅返回列表中包含的关系
        if filter.relationship_types is not None:
            if rel.type not in filter.relationship_types:
                return False
        return True

    async def query_node_details(self, node_id: str) -> Optional[Dict[str, Any]]:
        """查询节点详情，包括关联关系"""

        # 构建查询，获取节点及其直接关联关系
        query = """
        MATCH (n {id: $node_id})-[r]-(related)
        RETURN 
            n {.* , id: n.id, labels: labels(n)} AS node,
            collect({
                relationship: r {.* , id: id(r), type: type(r), from_id: n.id, to_id: related.id},
                related_node: related {.* , id: related.id, labels: labels(related)}
            }) AS connections
        """

        async with neo4j_connection.get_session() as session:
            result = await session.run(query, node_id=node_id)
            record = await result.single()

        if not record:
            return None

        neo_node = record["node"]
        connections = record["connections"]

        # 转换节点
        node = self._convert_node(neo_node)

        # 转换关联关系和相关节点
        relationships = []
        related_nodes = []

        for conn in connections:
            # 转换关系
            rel = self._convert_relationship(conn["relationship"])
            relationships.append(rel)

            # 转换相关节点
            related_node = self._convert_node(conn["related_node"])
            related_nodes.append(related_node)

        # 去重相关节点
        unique_related_nodes = {rn.id: rn for rn in related_nodes}.values()

        return {
            "node": node,
            "relationships": relationships,
            "related_nodes": list(unique_related_nodes),
        }

    async def _maybe_enhance_with_llm(self, subgraph: Subgraph) -> None:
        """尝试使用 LLM 对子图进行增强，失败时静默跳过"""

        try:
            from app.services.llm_service import get_llm_service

            llm = get_llm_service()
            if not llm:
                return

            if hasattr(llm, "enhance_subgraph"):
                try:
                    await llm.enhance_subgraph(subgraph)
                except Exception as e:  # noqa: BLE001
                    logger.warning("llm_subgraph_enhancement_failed", error=str(e))
        except Exception:
            # 如果 llm 服务不可用，直接跳过
            return


# 全局实例
query_service = QueryService()


def get_query_service() -> QueryService:
    """获取查询服务实例"""

    return query_service
