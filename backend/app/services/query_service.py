"""图查询服务

提供节点、关系、子图以及路径查询能力，供可视化和业务接口使用。
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

import structlog
from neo4j.time import DateTime

from app.database import neo4j_connection
from app.models.nodes import Node, NodeType
from app.models.relationships import Relationship, RelationshipType

logger = structlog.get_logger()


class NodeFilter:
    """节点查询过滤器"""

    def __init__(
        self,
        types: list[NodeType] | None = None,
        properties: dict[str, Any] | None = None,
        date_range: dict[str, Any] | None = None,
        school: str | None = None,
        grade: int | None = None,
        class_: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ):
        self.types = types
        self.properties = properties or {}
        self.date_range = date_range
        self.school = school
        self.grade = grade
        self.class_ = class_
        self.limit = limit
        self.offset = offset or 0


class RelationshipFilter:
    """关系查询过滤器"""

    def __init__(
        self,
        types: list[RelationshipType] | None = None,
        from_node_id: str | None = None,
        to_node_id: str | None = None,
        properties: dict[str, Any] | None = None,
        min_weight: float | None = None,
        max_weight: float | None = None,
        limit: int | None = None,
        offset: int | None = None,
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
        node_types: list[NodeType] | None = None,
        relationship_types: list[RelationshipType] | None = None,
        date_range: dict[str, Any] | None = None,
        school: str | None = None,
        grade: int | None = None,
        class_: str | None = None,
    ):
        self.node_types = node_types
        self.relationship_types = relationship_types
        self.date_range = date_range
        self.school = school
        self.grade = grade
        self.class_ = class_

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, GraphFilter):
            return False
        return (
            self.node_types == other.node_types
            and self.relationship_types == other.relationship_types
            and self.date_range == other.date_range
            and self.school == other.school
            and self.grade == other.grade
            and self.class_ == other.class_
        )


class Subgraph:
    """子图数据结构"""

    def __init__(
        self,
        nodes: list[Node],
        relationships: list[Relationship],
        metadata: dict[str, Any] | None = None,
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

    def to_dict(self) -> dict[str, Any]:
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
        nodes: list[Node],
        relationships: list[Relationship],
        length: int,
    ):
        self.nodes = nodes
        self.relationships = relationships
        self.length = length


class QueryService:
    """查询服务"""

    async def query_nodes(self, filter: NodeFilter) -> list[Node]:
        """按过滤条件查询节点"""

        query = "MATCH (n)"
        where_clauses: list[str] = []
        params: dict[str, Any] = {}

        if filter.types:
            params["types"] = [t.value for t in filter.types]
            where_clauses.append("ANY(label IN labels(n) WHERE label IN $types)")

        for idx, (key, value) in enumerate(filter.properties.items()):
            param_name = f"prop_{idx}"
            where_clauses.append(f"n.{key} = ${param_name}")
            params[param_name] = value

        if filter.date_range:
            params["start_date"] = filter.date_range.get("start")
            params["end_date"] = filter.date_range.get("end")
            where_clauses.append("n.created_at >= $start_date AND n.created_at <= $end_date")

        # 学校筛选 (单值)
        if filter.school:
            params["school"] = filter.school
            where_clauses.append("n.basic_info_school = $school")

        # 年级筛选 (单值，但节点属性是数组，使用 IN 匹配)
        if filter.grade is not None:
            params["grade"] = filter.grade
            where_clauses.append("$grade IN n.basic_info_grade")

        # 班级筛选 (单值)
        if filter.class_:
            params["class_"] = filter.class_
            where_clauses.append("n.basic_info_class = $class_")

        if where_clauses:
            query += " WHERE " + " AND ".join(where_clauses)

        query += " RETURN n, labels(n) AS labels"

        # 分页支持
        if filter.limit is not None:
            query += " SKIP $offset LIMIT $limit"
            params["offset"] = filter.offset
            params["limit"] = filter.limit
        else:
            query += " LIMIT 100"  # 默认限制

        async with neo4j_connection.get_session() as session:
            result = await session.run(query, **params)
            records = await result.data()

        nodes: list[Node] = []
        for record in records:
            neo4j_node = record["n"]
            node_data = dict(neo4j_node)
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

            # 确保id不为None，使用neo4j节点的原生id或生成唯一id
            node_id = node_data.pop("id", None)
            if not node_id:
                node_id = str(
                    getattr(neo4j_node, "id", None) or getattr(neo4j_node, "element_id", None)
                )

            # 不再需要处理basic_info字段，已改为扁平化属性

            # 安全地转换为NodeType枚举，避免抛出ValueError
            try:
                node_type = NodeType(node_type_value)
            except ValueError:
                # 如果node_type_value不是有效的NodeType，尝试从字符串中提取有效的类型
                node_type_str = str(node_type_value).lower()

                # 映射常见的类型名称变体到有效的NodeType
                type_mapping = {
                    "teacher": NodeType.TEACHER,
                    "student": NodeType.STUDENT,
                    "knowledge": NodeType.KNOWLEDGE_POINT,
                    "knowledgepoint": NodeType.KNOWLEDGE_POINT,
                }

                # 查找匹配的类型
                for key, value in type_mapping.items():
                    if key in node_type_str:
                        node_type = value
                        break
                else:
                    # 如果没有找到匹配的类型，使用默认类型
                    logger.warning(
                        "invalid_node_type_fallback",
                        node_id=node_id,
                        node_type_value=node_type_value,
                        default_type=NodeType.STUDENT.value,
                    )
                    node_type = NodeType.STUDENT

            created_at = (
                datetime.fromisoformat(created_at_raw)
                if isinstance(created_at_raw, str)
                else (
                    datetime(
                        created_at_raw.year,
                        created_at_raw.month,
                        created_at_raw.day,
                        created_at_raw.hour,
                        created_at_raw.minute,
                        created_at_raw.second,
                        created_at_raw.nanosecond // 1000,
                    )
                    if isinstance(created_at_raw, DateTime)
                    else created_at_raw or datetime.now()
                )
            )
            updated_at = (
                datetime.fromisoformat(updated_at_raw)
                if isinstance(updated_at_raw, str)
                else (
                    datetime(
                        updated_at_raw.year,
                        updated_at_raw.month,
                        updated_at_raw.day,
                        updated_at_raw.hour,
                        updated_at_raw.minute,
                        updated_at_raw.second,
                        updated_at_raw.nanosecond // 1000,
                    )
                    if isinstance(updated_at_raw, DateTime)
                    else updated_at_raw or datetime.now()
                )
            )

            if filter.date_range:
                start = (
                    filter.date_range.get("start") if isinstance(filter.date_range, dict) else None
                )
                end = filter.date_range.get("end") if isinstance(filter.date_range, dict) else None
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

    async def query_relationships(self, filter: RelationshipFilter) -> list[Relationship]:
        """按过滤条件查询关系"""

        query = "MATCH (from)-[r]->(to)"
        where_clauses: list[str] = []
        params: dict[str, Any] = {}

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

        if filter.date_range:
            params["start_date"] = filter.date_range.get("start")
            params["end_date"] = filter.date_range.get("end")
            where_clauses.append("r.created_at >= $start_date AND r.created_at <= $end_date")

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

        relationships: list[Relationship] = []
        for record in records:
            rel_data = dict(record["rel"])
            rel_id_raw = rel_data.pop("id", None)
            rel_type_value = rel_data.pop("type", None)
            from_id = rel_data.pop("from_id", None)
            to_id = rel_data.pop("to_id", None)
            rel_type = RelationshipType(rel_type_value)
            rel_id = str(rel_id_raw) if rel_id_raw is not None else None

            weight = rel_data.get("weight")

            if filter.min_weight is not None and (weight is None or weight < filter.min_weight):
                continue
            if filter.max_weight is not None and weight is not None and weight > filter.max_weight:
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
        filter: GraphFilter | None = None,
        max_nodes: int = 1000,
        max_relationships: int = 5000,
    ) -> Subgraph:
        """查询指定深度的子图

        Args:
            root_node_id: 根节点ID
            depth: 查询深度
            filter: 筛选条件
            max_nodes: 最大节点数量限制
            max_relationships: 最大关系数量限制
        """

        if depth < 1:
            raise ValueError("图深度应该至少为 1")
        if max_nodes <= 0:
            raise ValueError("最大节点数量必须大于0")
        if max_relationships <= 0:
            raise ValueError("最大关系数量必须大于0")

        # 先检查根节点是否存在，通过id属性匹配
        async with neo4j_connection.get_session() as session:
            exists_query = """
                MATCH (n)
                WHERE n.id = $root_id
                RETURN count(n) as cnt
            """
            exists_result = await session.run(
                exists_query,
                root_id=root_node_id,
            )
            exists_record = await exists_result.single()

            # 如果匹配失败，返回空的子图
            if not exists_record or exists_record["cnt"] == 0:
                logger.warning(
                    "root_node_not_found",
                    root_node_id=root_node_id,
                    query=exists_query,
                )
                return Subgraph(
                    nodes=[],
                    relationships=[],
                    metadata={"node_count": 0, "relationship_count": 0},
                )

            params = {
                "root_id": root_node_id,
                "max_nodes": max_nodes,
                "max_relationships": max_relationships,
            }

            # 构建基础查询，通过id属性匹配根节点
            query = f"""
                MATCH (root {{id: $root_id}})
                CALL {{
                  WITH root
                  MATCH p = (root)-[*0..{depth}]-(node)
                  RETURN p LIMIT $max_relationships
                }}
                UNWIND nodes(p) AS n
                WITH DISTINCT n LIMIT $max_nodes
                WITH collect(n) AS all_nodes
                WITH all_nodes, [n IN all_nodes | n {{.*, id: n.id, labels: labels(n)}}] AS nodes
                
                MATCH (a)-[r]-(b)
                WHERE a IN all_nodes AND b IN all_nodes
                WITH r, a, b, nodes
                LIMIT $max_relationships
                
                RETURN 
                  nodes,
                  collect(r {{.*, 
                    id: elementId(r), 
                    type: type(r), 
                    source: a.id, 
                    target: b.id}}) AS rels
            """

            result = await session.run(query, **params)
            records = await result.data()

        node_map: dict[str, Node] = {}
        rel_map: dict[str, Relationship] = {}

        # 1. 处理子图查询结果，限制节点和关系数量
        for record in records:
            # 处理节点
            for neo_node in record.get("nodes", []):
                if len(node_map) >= max_nodes:
                    break

                node = self._convert_node(neo_node)

                # 确保根节点不会被过滤掉，无论它是否满足过滤条件
                # 这是因为根节点是查询的起点，用户明确指定了要查看该节点
                if node.id == root_node_id or self._node_passes_filter(node, filter):
                    node_map[node.id] = node

            # 处理关系
            for neo_rel in record.get("rels", []):
                if len(rel_map) >= max_relationships:
                    break

                rel = self._convert_relationship(neo_rel)
                if self._relationship_passes_filter(rel, filter):
                    # 确保关系两端都在节点集合中
                    if rel.from_node_id in node_map and rel.to_node_id in node_map:
                        rel_map[rel.id] = rel

            if len(node_map) >= max_nodes and len(rel_map) >= max_relationships:
                break

        nodes = list(node_map.values())[:max_nodes]
        relationships = list(rel_map.values())[:max_relationships]

        subgraph = Subgraph(
            nodes=nodes,
            relationships=relationships,
            metadata={
                "node_count": len(nodes),
                "relationship_count": len(relationships),
                "max_nodes": max_nodes,
                "max_relationships": max_relationships,
                "depth": depth,
            },
        )

        logger.info(
            "query_subgraph_completed",
            node_count=len(nodes),
            relationship_count=len(relationships),
            max_nodes=max_nodes,
            max_relationships=max_relationships,
        )
        return subgraph

    async def find_path(
        self,
        from_node_id: str,
        to_node_id: str,
        max_depth: int,
        limit: int = 5,
        relationship_types: list[RelationshipType] | None = None,
    ) -> list[Path]:
        """查找两节点之间的路径"""

        if max_depth < 1:
            raise ValueError("Max depth must be at least 1")

        where_rel = ""
        params: dict[str, Any] = {
            "from_id": from_node_id,
            "to_id": to_node_id,
            "limit": limit,
        }

        if relationship_types:
            params["rel_types"] = [rt.value for rt in relationship_types]
            where_rel = " WHERE ALL(rt IN relationships(p) WHERE type(rt) IN $rel_types)"

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

        paths: list[Path] = []
        for record in records:
            nodes = [self._convert_node(n) for n in record.get("nodes", [])]
            relationships = [self._convert_relationship(r) for r in record.get("rels", [])]
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
        labels = node_data.pop("labels", [])
        node_type_value = None

        # 从labels中提取有效的NodeType
        if labels:
            # 遍历所有labels，找到第一个有效的NodeType
            for label in labels:
                if label in NodeType._value2member_map_:
                    node_type_value = label
                    break

        # 如果labels中没有找到，尝试从节点属性中获取
        if not node_type_value:
            node_type_value = node_data.get("type")

        # 如果仍然没有找到，尝试从node_data中获取类型信息
        if not node_type_value:
            # 检查是否有特定的类型标识属性
            for key in [
                "teacher_id",
                "student_id",
                "course_id",
                "knowledge_point_id",
                "error_type_id",
            ]:
                if key in node_data:
                    # 根据属性名推断节点类型
                    if "teacher" in key:
                        node_type_value = "Teacher"
                    elif "student" in key:
                        node_type_value = "Student"
                    elif "knowledge" in key:
                        node_type_value = "KnowledgePoint"
                    break

        if not node_type_value:
            logger.warning(
                "node_type_missing",
                node_id=node_id,
                labels=labels,
                properties=list(node_data.keys()),
            )
            # 保留原labels作为类型，以便调试
            node_type_value = labels[0] if labels else NodeType.STUDENT.value

        # 确保node_type_value是有效的NodeType
        if node_type_value not in NodeType._value2member_map_:
            logger.warning(
                "invalid_node_type",
                node_id=node_id,
                node_type_value=node_type_value,
                labels=labels,
            )
            # 尝试从labels中获取第一个有效类型，如果没有则使用Student作为默认值
            valid_types = [lbl for lbl in labels if lbl in NodeType._value2member_map_]
            node_type_value = valid_types[0] if valid_types else NodeType.STUDENT.value

        node_type = NodeType(node_type_value)

        # 处理created_at转换，支持neo4j.time.datetime对象
        if hasattr(created_at_raw, "isoformat"):
            # 处理neo4j.time.datetime对象
            created_at = datetime.fromisoformat(created_at_raw.isoformat())
        elif isinstance(created_at_raw, str):
            # 处理字符串格式
            created_at = datetime.fromisoformat(created_at_raw)
        else:
            # 使用默认值
            created_at = datetime.utcnow()

        # 处理updated_at转换，支持neo4j.time.datetime对象
        if hasattr(updated_at_raw, "isoformat"):
            # 处理neo4j.time.datetime对象
            updated_at = datetime.fromisoformat(updated_at_raw.isoformat())
        elif isinstance(updated_at_raw, str):
            # 处理字符串格式
            updated_at = datetime.fromisoformat(updated_at_raw)
        else:
            # 使用默认值
            updated_at = datetime.now()

        # 确保id不为None
        if not node_id:
            # 从neo节点获取原生id并转换为字符串
            node_id = str(getattr(neo_node, "id", None))

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
            # 处理关系类型，确保它始终有值
            rel_type_raw = rel.get("type")
            if not rel_type_raw:
                # 如果关系没有类型，使用默认类型
                rel_type_raw = RelationshipType.RELATES_TO.value

            # 处理关系端点，确保它们始终有值
            from_id = rel.get("source") or rel.get("from_id") or rel.get("start") or "unknown"
            to_id = rel.get("target") or rel.get("to_id") or rel.get("end") or "unknown"

            rel_id_raw = rel.get("id")

            # 过滤掉不需要的属性
            props = {
                k: v
                for k, v in rel.items()
                if k not in {"id", "type", "source", "target", "from_id", "to_id", "start", "end"}
            }

            # 安全地转换为RelationshipType枚举，避免抛出ValueError
            try:
                rel_type = RelationshipType(rel_type_raw)
            except ValueError:
                # 如果rel_type_raw不是有效的RelationshipType，使用RELATES_TO作为默认类型
                # 因为RELATES_TO是最通用的关系类型，适合表示任何未定义的关系
                logger.warning(
                    "invalid_relationship_type",
                    rel_id=rel_id_raw,
                    rel_type=rel_type_raw,
                )
                rel_type = RelationshipType.RELATES_TO

            rel_id = str(rel_id_raw) if rel_id_raw is not None else None

            return Relationship(
                id=rel_id,
                type=rel_type,
                from_node_id=from_id,
                to_node_id=to_id,
                properties=props or None,
                weight=props.get("weight") if props else None,
            )

        raise ValueError(f"Unsupported relationship type: {type(rel)}")

    def _node_passes_filter(self, node: Node, filter: GraphFilter | None) -> bool:
        if filter is None:
            return True
        # 如果node_types是列表（包括空列表），则仅返回列表中包含的节点
        if filter.node_types is not None:
            if node.type not in filter.node_types:
                return False

        # 学校/年级/班级过滤（仅对Student类型节点生效）
        if node.type == NodeType.STUDENT:
            props = node.properties or {}

            # 学校过滤
            if filter.school is not None:
                node_school = props.get("basic_info_school")
                if node_school != filter.school:
                    return False

            # 年级过滤（grade是整数，但节点中存储为数组）
            if filter.grade is not None:
                node_grades = props.get("basic_info_grade", [])
                # 确保node_grades是列表
                if not isinstance(node_grades, list):
                    node_grades = [node_grades] if node_grades else []
                if filter.grade not in node_grades:
                    return False

            # 班级过滤
            if filter.class_ is not None:
                node_class = props.get("basic_info_class")
                if node_class != filter.class_:
                    return False

        if filter.date_range:
            from datetime import datetime

            from dateutil import parser

            def parse_date(date_str):
                """解析各种格式的日期字符串"""
                if not date_str:
                    return None
                if isinstance(date_str, datetime):
                    return date_str
                try:
                    # 尝试解析ISO格式
                    return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
                except ValueError:
                    # 尝试解析其他格式
                    return parser.parse(date_str)

            start = filter.date_range.get("start") if isinstance(filter.date_range, dict) else None
            end = filter.date_range.get("end") if isinstance(filter.date_range, dict) else None

            # 处理字符串日期转换
            if isinstance(start, str):
                start = parse_date(start)
            if isinstance(end, str):
                end = parse_date(end)

            # 确保node.created_at是带时区的datetime对象
            if node.created_at.tzinfo is None:
                # 添加UTC时区信息
                node_created_at_aware = node.created_at.replace(tzinfo=UTC)
            else:
                node_created_at_aware = node.created_at

            # 确保比较的日期也是带时区的
            if start and start.tzinfo is None:
                start = start.replace(tzinfo=UTC)
            if end and end.tzinfo is None:
                end = end.replace(tzinfo=UTC)

            if start and node_created_at_aware < start:
                return False
            if end and node_created_at_aware > end:
                return False
        return True

    def _relationship_passes_filter(self, rel: Relationship, filter: GraphFilter | None) -> bool:
        if filter is None:
            return True
        # 如果relationship_types是列表（包括空列表），则仅返回列表中包含的关系
        if filter.relationship_types is not None:
            if rel.type not in filter.relationship_types:
                return False
        return True

    async def run_cypher_query(
        self, query: str, params: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        """执行Cypher查询并返回结果"""
        async with neo4j_connection.get_session() as session:
            result = await session.run(query, **(params or {}))
            return await result.data()

    async def query_node_details(self, node_id: str) -> dict[str, Any] | None:
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

        # 如果查询具体相关节点
        # RETURN
        #     n {.* , id: n.id, labels: labels(n)} AS node,
        #     collect({
        #         relationship: r {.* , id: id(r), type: type(r), from_id: n.id, to_id: related.id},
        #         related_node: related {.* , id: related.id, labels: labels(related)}
        #     }) AS connections

        result = await self.run_cypher_query(query, {"node_id": node_id})
        if not result:
            return None

        record = result[0]
        neo_node = record["node"]
        connections = record["connections"]

        # 转换节点
        node = self._convert_node(neo_node)

        # 转换关联关系和相关节点
        relationshipTypes = {}
        # related_nodes = []

        for conn in connections:
            # 转换关系
            rel = self._convert_relationship(conn["relationship"])
            relationshipTypes[rel.type] = relationshipTypes.get(rel.type, 0) + 1

            # 转换相关节点
            # related_node = self._convert_node(conn["related_node"])
            # related_nodes.append(related_node)

        # 去重相关节点
        # unique_related_nodes = {
        #     rn.id: {"type": rn.type, "count": 1} for rn in related_nodes
        # }.values()

        return {
            "node": node,
            "relationshipTypeCounts": relationshipTypes,
            # "connectedNodesCounts": list(unique_related_nodes),
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
