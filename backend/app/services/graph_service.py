"""图谱管理服务"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Literal
from uuid import uuid4
from enum import Enum
import structlog

from app.database import neo4j_connection
from app.models.nodes import (
    Node,
    NodeType,
    StudentNodeProperties,
    TeacherNodeProperties,
    CourseNodeProperties,
    KnowledgePointNodeProperties,
    ErrorTypeNodeProperties,
)
from app.models.relationships import Relationship, RelationshipType

logger = structlog.get_logger()


class ConflictResolutionStrategy(str, Enum):
    """冲突解决策略"""
    TIMESTAMP_PRIORITY = "timestamp_priority"  # 时间戳优先（保留最新数据）
    KEEP_EXISTING = "keep_existing"  # 保留现有数据
    MERGE_PROPERTIES = "merge_properties"  # 合并属性


class GraphOperation:
    """图操作基类"""
    pass


class CreateNodeOperation(GraphOperation):
    """创建节点操作"""
    def __init__(self, node_type: NodeType, properties: Dict[str, Any]):
        self.node_type = node_type
        self.properties = properties


class UpdateNodeOperation(GraphOperation):
    """更新节点操作"""
    def __init__(self, node_id: str, properties: Dict[str, Any]):
        self.node_id = node_id
        self.properties = properties


class CreateRelationshipOperation(GraphOperation):
    """创建关系操作"""
    def __init__(
        self,
        from_node_id: str,
        to_node_id: str,
        relationship_type: RelationshipType,
        properties: Optional[Dict[str, Any]] = None,
    ):
        self.from_node_id = from_node_id
        self.to_node_id = to_node_id
        self.relationship_type = relationship_type
        self.properties = properties or {}


class UpdateRelationshipOperation(GraphOperation):
    """更新关系操作"""
    def __init__(self, relationship_id: str, properties: Dict[str, Any]):
        self.relationship_id = relationship_id
        self.properties = properties


class BatchResult:
    """批量操作结果"""
    def __init__(
        self,
        success: bool,
        operations_count: int,
        successful_operations: int,
        failed_operations: int,
        results: List[Any],
        errors: List[str],
    ):
        self.success = success
        self.operations_count = operations_count
        self.successful_operations = successful_operations
        self.failed_operations = failed_operations
        self.results = results
        self.errors = errors


class GraphManagementService:
    """图谱管理服务
    
    负责管理图数据库中的节点和关系
    """
    
    # 节点类型到属性模型的映射
    NODE_PROPERTY_MODELS = {
        NodeType.STUDENT: StudentNodeProperties,
        NodeType.TEACHER: TeacherNodeProperties,
        NodeType.COURSE: CourseNodeProperties,
        NodeType.KNOWLEDGE_POINT: KnowledgePointNodeProperties,
        NodeType.ERROR_TYPE: ErrorTypeNodeProperties,
    }
    
    def _flatten_dict(self, d: Dict[str, Any], parent_key: str = '', sep: str = '_') -> Dict[str, Any]:
        """将嵌套字典扁平化为单层字典
        
        Args:
            d: 嵌套字典
            parent_key: 父键
            sep: 分隔符
            
        Returns:
            扁平字典
        """
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self._flatten_dict(v, new_key, sep=sep).items())
            elif isinstance(v, list):
                # 将列表转换为字符串或保持原样，根据Neo4j支持的类型
                items.append((new_key, v))
            else:
                items.append((new_key, v))
        return dict(items)
    
    async def create_node(
        self,
        node_type: NodeType,
        properties: Dict[str, Any],
    ) -> Node:
        """创建节点
        
        Args:
            node_type: 节点类型
            properties: 节点属性
            
        Returns:
            创建的节点
            
        Raises:
            ValueError: 如果属性验证失败
            RuntimeError: 如果数据库操作失败
        """
        # 验证属性
        property_model = self.NODE_PROPERTY_MODELS.get(node_type)
        if property_model is None:
            raise ValueError(f"Unknown node type: {node_type}")
        
        try:
            validated_properties = property_model(**properties)
        except Exception as e:
            logger.error(
                "node_property_validation_failed",
                node_type=node_type,
                error=str(e),
            )
            raise ValueError(f"Property validation failed: {e}")
        
        # 生成节点 ID
        node_id = str(uuid4())
        
        # 添加时间戳
        now = datetime.utcnow()
        properties_dict = validated_properties.model_dump()
        
        # 将嵌套字典扁平化为单层字典，以兼容Neo4j
        flattened_properties = self._flatten_dict(properties_dict)
        
        # 将类型写入属性，防止后续查询缺失标签时无法识别节点类型
        flattened_properties["type"] = node_type.value
        flattened_properties["created_at"] = now.isoformat()
        flattened_properties["updated_at"] = now.isoformat()
        
        # 检查唯一性
        unique_field = self._get_unique_field(node_type)
        if unique_field and unique_field in flattened_properties:
            existing_node = await self._find_node_by_unique_field(
                node_type,
                unique_field,
                flattened_properties[unique_field],
            )
            if existing_node:
                logger.warning(
                    "node_already_exists",
                    node_type=node_type,
                    unique_field=unique_field,
                    value=flattened_properties[unique_field],
                )
                return existing_node
        
        # 创建节点
        query = f"""
        CREATE (n:{node_type.value} $properties)
        SET n.id = $node_id
        RETURN n
        """
        
        try:
            async with neo4j_connection.get_session() as session:
                result = await session.run(
                    query,
                    properties=flattened_properties,
                    node_id=node_id,
                )
                record = await result.single()
                
                if record is None:
                    raise RuntimeError("Failed to create node")
                
                node_data = dict(record["n"])
                
                logger.info(
                    "node_created",
                    node_id=node_id,
                    node_type=node_type,
                )
                
                return Node(
                    id=node_id,
                    type=node_type,
                    properties=node_data,
                    created_at=now,
                    updated_at=now,
                )
        except Exception as e:
            logger.error(
                "node_creation_failed",
                node_type=node_type,
                error=str(e),
            )
            raise RuntimeError(f"Failed to create node: {e}")
    
    async def _find_node_by_unique_field(
        self,
        node_type: NodeType,
        field_name: str,
        field_value: Any,
    ) -> Optional[Node]:
        """根据唯一字段查找节点
        
        Args:
            node_type: 节点类型
            field_name: 字段名
            field_value: 字段值
            
        Returns:
            找到的节点，如果不存在则返回 None
        """
        query = f"""
        MATCH (n:{node_type.value})
        WHERE n.{field_name} = $field_value
        RETURN n
        """
        
        try:
            async with neo4j_connection.get_session() as session:
                result = await session.run(query, field_value=field_value)
                record = await result.single()
                
                if record is None:
                    return None
                
                node_data = dict(record["n"])
                node_id = node_data.pop("id", None)
                
                if node_id is None:
                    return None
                
                created_at = node_data.pop("created_at", None)
                updated_at = node_data.pop("updated_at", None)
                
                return Node(
                    id=node_id,
                    type=node_type,
                    properties=node_data,
                    created_at=datetime.fromisoformat(created_at) if created_at else datetime.utcnow(),
                    updated_at=datetime.fromisoformat(updated_at) if updated_at else datetime.utcnow(),
                )
        except Exception as e:
            logger.error(
                "node_lookup_failed",
                node_type=node_type,
                field_name=field_name,
                error=str(e),
            )
            return None
    
    def _get_unique_field(self, node_type: NodeType) -> Optional[str]:
        """获取节点类型的唯一字段名
        
        Args:
            node_type: 节点类型
            
        Returns:
            唯一字段名，如果没有则返回 None
        """
        unique_fields = {
            NodeType.STUDENT: "student_id",
            NodeType.TEACHER: "teacher_id",
            NodeType.COURSE: "course_id",
            NodeType.KNOWLEDGE_POINT: "knowledge_point_id",
            NodeType.ERROR_TYPE: "error_type_id",
        }
        return unique_fields.get(node_type)
    
    async def merge_nodes(self, node_ids: List[str]) -> Node:
        """合并重复节点
        
        将多个节点合并为一个节点，保留所有属性和关系
        
        Args:
            node_ids: 要合并的节点 ID 列表
            
        Returns:
            合并后的节点
            
        Raises:
            ValueError: 如果节点列表为空或节点类型不一致
            RuntimeError: 如果数据库操作失败
        """
        if not node_ids or len(node_ids) < 2:
            raise ValueError("At least 2 nodes are required for merging")
        
        # 获取所有节点
        nodes = []
        async with neo4j_connection.get_session() as session:
            for node_id in node_ids:
                query = """
                MATCH (n)
                WHERE n.id = $node_id
                RETURN n, labels(n) as labels
                """
                result = await session.run(query, node_id=node_id)
                record = await result.single()
                
                if record is None:
                    logger.warning("node_not_found", node_id=node_id)
                    continue
                
                nodes.append({
                    "data": dict(record["n"]),
                    "labels": record["labels"],
                    "id": node_id,
                })
        
        if len(nodes) < 2:
            raise ValueError("Not enough valid nodes found for merging")
        
        # 检查节点类型是否一致
        first_labels = set(nodes[0]["labels"])
        for node in nodes[1:]:
            if set(node["labels"]) != first_labels:
                raise ValueError("Cannot merge nodes of different types")
        
        # 确定主节点（保留第一个）
        primary_node = nodes[0]
        secondary_node_ids = [n["id"] for n in nodes[1:]]
        
        # 合并属性（后面的节点属性覆盖前面的）
        merged_properties = {}
        for node in nodes:
            merged_properties.update(node["data"])
        
        # 更新时间戳
        merged_properties["updated_at"] = datetime.utcnow().isoformat()
        
        try:
            async with neo4j_connection.get_session() as session:
                # 在事务中执行合并操作
                async with await session.begin_transaction() as tx:
                    # 更新主节点属性
                    update_query = """
                    MATCH (n)
                    WHERE n.id = $node_id
                    SET n = $properties
                    RETURN n
                    """
                    await tx.run(
                        update_query,
                        node_id=primary_node["id"],
                        properties=merged_properties,
                    )
                    
                    # 将所有指向次要节点的关系重定向到主节点
                    for secondary_id in secondary_node_ids:
                        redirect_incoming_query = """
                        MATCH (other)-[r]->(secondary)
                        WHERE secondary.id = $secondary_id
                        MATCH (primary)
                        WHERE primary.id = $primary_id
                        CREATE (other)-[r2:TYPE(r)]->(primary)
                        SET r2 = properties(r)
                        DELETE r
                        """
                        await tx.run(
                            redirect_incoming_query,
                            secondary_id=secondary_id,
                            primary_id=primary_node["id"],
                        )
                        
                        redirect_outgoing_query = """
                        MATCH (secondary)-[r]->(other)
                        WHERE secondary.id = $secondary_id
                        MATCH (primary)
                        WHERE primary.id = $primary_id
                        CREATE (primary)-[r2:TYPE(r)]->(other)
                        SET r2 = properties(r)
                        DELETE r
                        """
                        await tx.run(
                            redirect_outgoing_query,
                            secondary_id=secondary_id,
                            primary_id=primary_node["id"],
                        )
                    
                    # 删除次要节点
                    delete_query = """
                    MATCH (n)
                    WHERE n.id IN $node_ids
                    DELETE n
                    """
                    await tx.run(delete_query, node_ids=secondary_node_ids)
                    
                    await tx.commit()
                
                logger.info(
                    "nodes_merged",
                    primary_node_id=primary_node["id"],
                    merged_node_ids=secondary_node_ids,
                )
                
                # 获取合并后的节点
                node_type_str = list(first_labels)[0]
                node_type = NodeType(node_type_str)
                
                created_at = merged_properties.pop("created_at", None)
                updated_at = merged_properties.pop("updated_at", None)
                node_id = merged_properties.pop("id", primary_node["id"])
                
                return Node(
                    id=node_id,
                    type=node_type,
                    properties=merged_properties,
                    created_at=datetime.fromisoformat(created_at) if created_at else datetime.utcnow(),
                    updated_at=datetime.fromisoformat(updated_at) if updated_at else datetime.utcnow(),
                )
        except Exception as e:
            logger.error(
                "node_merge_failed",
                node_ids=node_ids,
                error=str(e),
            )
            raise RuntimeError(f"Failed to merge nodes: {e}")
    
    async def update_node(
        self,
        node_id: str,
        properties: Dict[str, Any],
    ) -> Node:
        """更新节点属性
        
        Args:
            node_id: 节点 ID
            properties: 要更新的属性
            
        Returns:
            更新后的节点
            
        Raises:
            ValueError: 如果节点不存在
            RuntimeError: 如果数据库操作失败
        """
        # 添加更新时间戳
        properties["updated_at"] = datetime.utcnow().isoformat()
        
        query = """
        MATCH (n)
        WHERE n.id = $node_id
        SET n += $properties
        RETURN n, labels(n) as labels
        """
        
        try:
            async with neo4j_connection.get_session() as session:
                result = await session.run(
                    query,
                    node_id=node_id,
                    properties=properties,
                )
                record = await result.single()
                
                if record is None:
                    raise ValueError(f"Node not found: {node_id}")
                
                node_data = dict(record["n"])
                node_type_str = record["labels"][0]
                node_type = NodeType(node_type_str)
                
                created_at = node_data.pop("created_at", None)
                updated_at = node_data.pop("updated_at", None)
                node_data.pop("id", None)
                
                logger.info("node_updated", node_id=node_id)
                
                return Node(
                    id=node_id,
                    type=node_type,
                    properties=node_data,
                    created_at=datetime.fromisoformat(created_at) if created_at else datetime.utcnow(),
                    updated_at=datetime.fromisoformat(updated_at) if updated_at else datetime.utcnow(),
                )
        except Exception as e:
            logger.error(
                "node_update_failed",
                node_id=node_id,
                error=str(e),
            )
            raise RuntimeError(f"Failed to update node: {e}")
    
    async def create_relationship(
        self,
        from_node_id: str,
        to_node_id: str,
        relationship_type: RelationshipType,
        properties: Optional[Dict[str, Any]] = None,
    ) -> Relationship:
        """创建关系
        
        支持所有关系类型，包括属性验证和权重计算
        
        Args:
            from_node_id: 起始节点 ID
            to_node_id: 目标节点 ID
            relationship_type: 关系类型
            properties: 关系属性
            
        Returns:
            创建的关系
            
        Raises:
            ValueError: 如果节点不存在或属性验证失败
            RuntimeError: 如果数据库操作失败
        """
        properties = properties or {}
        
        # 验证关系属性
        validated_properties = self._validate_relationship_properties(
            relationship_type,
            properties,
        )
        
        # 计算关系权重
        weight = self._calculate_relationship_weight(
            relationship_type,
            validated_properties,
        )
        
        # 添加权重到属性中（如果计算出了权重）
        if weight is not None:
            validated_properties["weight"] = weight
        
        # 生成关系 ID
        relationship_id = str(uuid4())
        
        # 创建关系
        query = f"""
        MATCH (from), (to)
        WHERE from.id = $from_node_id AND to.id = $to_node_id
        CREATE (from)-[r:{relationship_type.value} $properties]->(to)
        SET r.id = $relationship_id
        RETURN r, from.id as from_id, to.id as to_id
        """
        
        try:
            async with neo4j_connection.get_session() as session:
                result = await session.run(
                    query,
                    from_node_id=from_node_id,
                    to_node_id=to_node_id,
                    properties=validated_properties,
                    relationship_id=relationship_id,
                )
                record = await result.single()
                
                if record is None:
                    raise ValueError("Failed to create relationship. Nodes may not exist.")
                
                rel_data = dict(record["r"])
                rel_data.pop("id", None)
                
                logger.info(
                    "relationship_created",
                    relationship_id=relationship_id,
                    relationship_type=relationship_type,
                    from_node_id=from_node_id,
                    to_node_id=to_node_id,
                    weight=weight,
                )
                
                return Relationship(
                    id=relationship_id,
                    type=relationship_type,
                    from_node_id=from_node_id,
                    to_node_id=to_node_id,
                    properties=rel_data,
                    weight=weight,
                )
        except Exception as e:
            logger.error(
                "relationship_creation_failed",
                relationship_type=relationship_type,
                from_node_id=from_node_id,
                to_node_id=to_node_id,
                error=str(e),
            )
            raise RuntimeError(f"Failed to create relationship: {e}")
    
    def _validate_relationship_properties(
        self,
        relationship_type: RelationshipType,
        properties: Dict[str, Any],
    ) -> Dict[str, Any]:
        """验证关系属性
        
        Args:
            relationship_type: 关系类型
            properties: 关系属性
            
        Returns:
            验证后的属性字典
            
        Raises:
            ValueError: 如果属性验证失败
        """
        from app.models.relationships import (
            ChatWithProperties,
            LikesProperties,
            TeachesProperties,
            LearnsProperties,
            ContainsProperties,
            HasErrorProperties,
            RelatesToProperties,
        )
        
        # 关系类型到属性模型的映射
        property_models = {
            RelationshipType.CHAT_WITH: ChatWithProperties,
            RelationshipType.LIKES: LikesProperties,
            RelationshipType.TEACHES: TeachesProperties,
            RelationshipType.LEARNS: LearnsProperties,
            RelationshipType.CONTAINS: ContainsProperties,
            RelationshipType.HAS_ERROR: HasErrorProperties,
            RelationshipType.RELATES_TO: RelatesToProperties,
        }
        
        property_model = property_models.get(relationship_type)
        if property_model is None:
            # 如果没有特定的属性模型，直接返回属性
            return properties
        
        try:
            # 验证属性
            validated = property_model(**properties)
            return validated.model_dump(exclude_none=True)
        except Exception as e:
            logger.error(
                "relationship_property_validation_failed",
                relationship_type=relationship_type,
                error=str(e),
            )
            raise ValueError(f"Property validation failed for {relationship_type}: {e}")
    
    def _calculate_relationship_weight(
        self,
        relationship_type: RelationshipType,
        properties: Dict[str, Any],
    ) -> Optional[float]:
        """计算关系权重
        
        根据关系类型和属性计算权重值
        
        Args:
            relationship_type: 关系类型
            properties: 关系属性
            
        Returns:
            计算出的权重值，如果不适用则返回 None
        """
        # 不同关系类型的权重计算策略
        if relationship_type == RelationshipType.CHAT_WITH:
            # 聊天互动：基于消息数量
            message_count = properties.get("message_count", 1)
            return float(message_count)
        
        elif relationship_type == RelationshipType.LIKES:
            # 点赞互动：基于点赞数量
            like_count = properties.get("like_count", 1)
            return float(like_count)
        
        elif relationship_type == RelationshipType.TEACHES:
            # 教学互动：基于互动次数
            interaction_count = properties.get("interaction_count", 1)
            return float(interaction_count)
        
        elif relationship_type == RelationshipType.LEARNS:
            # 学习关系：基于学习进度
            progress = properties.get("progress", 0.0)
            return progress
        
        elif relationship_type == RelationshipType.HAS_ERROR:
            # 错误关系：基于发生次数
            occurrence_count = properties.get("occurrence_count", 1)
            return float(occurrence_count)
        
        elif relationship_type == RelationshipType.RELATES_TO:
            # 关联关系：基于关联强度
            strength = properties.get("strength", 0.5)
            return strength
        
        elif relationship_type == RelationshipType.CONTAINS:
            # 包含关系：基于重要性
            importance = properties.get("importance")
            if importance == "core":
                return 1.0
            elif importance == "supplementary":
                return 0.5
            return None
        
        return None
    
    async def update_relationship(
        self,
        relationship_id: str,
        properties: Dict[str, Any],
    ) -> Relationship:
        """更新关系属性
        
        Args:
            relationship_id: 关系 ID
            properties: 要更新的属性
            
        Returns:
            更新后的关系
            
        Raises:
            ValueError: 如果关系不存在
            RuntimeError: 如果数据库操作失败
        """
        query = """
        MATCH ()-[r]->()
        WHERE r.id = $relationship_id
        SET r += $properties
        RETURN r, type(r) as rel_type, startNode(r).id as from_id, endNode(r).id as to_id
        """
        
        try:
            async with neo4j_connection.get_session() as session:
                result = await session.run(
                    query,
                    relationship_id=relationship_id,
                    properties=properties,
                )
                record = await result.single()
                
                if record is None:
                    raise ValueError(f"Relationship not found: {relationship_id}")
                
                rel_data = dict(record["r"])
                rel_data.pop("id", None)
                rel_type = RelationshipType(record["rel_type"])
                from_id = record["from_id"]
                to_id = record["to_id"]
                
                logger.info("relationship_updated", relationship_id=relationship_id)
                
                return Relationship(
                    id=relationship_id,
                    type=rel_type,
                    from_node_id=from_id,
                    to_node_id=to_id,
                    properties=rel_data,
                    weight=rel_data.get("weight"),
                )
        except Exception as e:
            logger.error(
                "relationship_update_failed",
                relationship_id=relationship_id,
                error=str(e),
            )
            raise RuntimeError(f"Failed to update relationship: {e}")
    
    async def increment_relationship_weight(
        self,
        from_node_id: str,
        to_node_id: str,
        relationship_type: RelationshipType,
        increment: float = 1.0,
    ) -> Relationship:
        """增加关系权重
        
        用于处理重复错误等场景，增加现有关系的权重
        
        Args:
            from_node_id: 起始节点 ID
            to_node_id: 目标节点 ID
            relationship_type: 关系类型
            increment: 权重增量
            
        Returns:
            更新后的关系
            
        Raises:
            ValueError: 如果关系不存在
            RuntimeError: 如果数据库操作失败
        """
        query = f"""
        MATCH (from)-[r:{relationship_type.value}]->(to)
        WHERE from.id = $from_node_id AND to.id = $to_node_id
        SET r.weight = COALESCE(r.weight, 0) + $increment
        RETURN r, r.id as rel_id, from.id as from_id, to.id as to_id
        """
        
        try:
            async with neo4j_connection.get_session() as session:
                result = await session.run(
                    query,
                    from_node_id=from_node_id,
                    to_node_id=to_node_id,
                    increment=increment,
                )
                record = await result.single()
                
                if record is None:
                    raise ValueError(
                        f"Relationship not found: {from_node_id} -> {to_node_id} ({relationship_type})"
                    )
                
                rel_data = dict(record["r"])
                rel_id = rel_data.pop("id", None)
                
                logger.info(
                    "relationship_weight_incremented",
                    relationship_id=rel_id,
                    relationship_type=relationship_type,
                    increment=increment,
                    new_weight=rel_data.get("weight"),
                )
                
                return Relationship(
                    id=rel_id,
                    type=relationship_type,
                    from_node_id=from_node_id,
                    to_node_id=to_node_id,
                    properties=rel_data,
                    weight=rel_data.get("weight"),
                )
        except Exception as e:
            logger.error(
                "relationship_weight_increment_failed",
                relationship_type=relationship_type,
                from_node_id=from_node_id,
                to_node_id=to_node_id,
                error=str(e),
            )
            raise RuntimeError(f"Failed to increment relationship weight: {e}")
    
    async def create_student_multi_course_error(
        self,
        student_id: str,
        error_type_id: str,
        course_id: str,
        occurrence_time: datetime,
        knowledge_point_ids: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """创建学生多课程错误记录
        
        为学生在特定课程中的错误创建独立的 HAS_ERROR 关系，
        并关联到相关知识点
        
        Args:
            student_id: 学生节点 ID
            error_type_id: 错误类型节点 ID
            course_id: 课程 ID
            occurrence_time: 错误发生时间
            knowledge_point_ids: 相关知识点节点 ID 列表
            
        Returns:
            包含创建的关系信息的字典
            
        Raises:
            ValueError: 如果节点不存在
            RuntimeError: 如果数据库操作失败
        """
        knowledge_point_ids = knowledge_point_ids or []
        
        # 检查是否已存在相同的错误关系
        check_query = """
        MATCH (s:Student)-[r:HAS_ERROR]->(e:ErrorType)
        WHERE s.student_id = $student_id 
        AND e.error_type_id = $error_type_id 
        AND r.course_id = $course_id
        RETURN r
        """
        
        try:
            async with neo4j_connection.get_session() as session:
                result = await session.run(
                    check_query,
                    student_id=student_id,
                    error_type_id=error_type_id,
                    course_id=course_id,
                )
                existing_record = await result.single()
                
                if existing_record:
                    # 如果已存在，更新发生次数和最后发生时间
                    update_query = """
                    MATCH (s:Student)-[r:HAS_ERROR]->(e:ErrorType)
                    WHERE s.student_id = $student_id 
                    AND e.error_type_id = $error_type_id 
                    AND r.course_id = $course_id
                    SET r.occurrence_count = r.occurrence_count + 1,
                        r.last_occurrence = $occurrence_time,
                        r.weight = r.occurrence_count + 1
                    RETURN r, r.id as rel_id, s.id as from_id, e.id as to_id
                    """
                    
                    result = await session.run(
                        update_query,
                        student_id=student_id,
                        error_type_id=error_type_id,
                        course_id=course_id,
                        occurrence_time=occurrence_time.isoformat(),
                    )
                    record = await result.single()
                    
                    rel_data = dict(record["r"])
                    rel_id = rel_data.pop("id", None)
                    
                    logger.info(
                        "student_error_updated",
                        student_id=student_id,
                        error_type_id=error_type_id,
                        course_id=course_id,
                        occurrence_count=rel_data.get("occurrence_count"),
                    )
                    
                    return {
                        "relationship": Relationship(
                            id=rel_id,
                            type=RelationshipType.HAS_ERROR,
                            from_node_id=record["from_id"],
                            to_node_id=record["to_id"],
                            properties=rel_data,
                            weight=rel_data.get("weight"),
                        ),
                        "is_new": False,
                    }
                
                # 创建新的错误关系
                # 首先获取学生和错误类型节点的内部 ID
                get_nodes_query = """
                MATCH (s:Student {student_id: $student_id})
                MATCH (e:ErrorType {error_type_id: $error_type_id})
                RETURN s.id as student_node_id, e.id as error_node_id
                """
                
                result = await session.run(
                    get_nodes_query,
                    student_id=student_id,
                    error_type_id=error_type_id,
                )
                nodes_record = await result.single()
                
                if not nodes_record:
                    raise ValueError(
                        f"Student or ErrorType not found: {student_id}, {error_type_id}"
                    )
                
                student_node_id = nodes_record["student_node_id"]
                error_node_id = nodes_record["error_node_id"]
                
                # 创建 HAS_ERROR 关系
                error_relationship = await self.create_relationship(
                    from_node_id=student_node_id,
                    to_node_id=error_node_id,
                    relationship_type=RelationshipType.HAS_ERROR,
                    properties={
                        "occurrence_count": 1,
                        "first_occurrence": occurrence_time,
                        "last_occurrence": occurrence_time,
                        "course_id": course_id,
                        "resolved": False,
                    },
                )
                
                # 如果提供了知识点，创建错误类型到知识点的关联
                relates_to_relationships = []
                if knowledge_point_ids:
                    relates_to_relationships = await self.associate_error_with_knowledge_points(
                        error_type_id=error_type_id,
                        knowledge_point_ids=knowledge_point_ids,
                    )
                
                logger.info(
                    "student_multi_course_error_created",
                    student_id=student_id,
                    error_type_id=error_type_id,
                    course_id=course_id,
                    knowledge_points_count=len(knowledge_point_ids),
                )
                
                return {
                    "relationship": error_relationship,
                    "relates_to_relationships": relates_to_relationships,
                    "is_new": True,
                }
        except Exception as e:
            logger.error(
                "student_multi_course_error_creation_failed",
                student_id=student_id,
                error_type_id=error_type_id,
                course_id=course_id,
                error=str(e),
            )
            raise RuntimeError(f"Failed to create student multi-course error: {e}")
    
    async def associate_error_with_knowledge_points(
        self,
        error_type_id: str,
        knowledge_point_ids: List[str],
        strength: float = 0.8,
        confidence: float = 0.9,
    ) -> List[Relationship]:
        """将错误类型关联到多个知识点
        
        创建错误类型节点到所有相关知识点节点的 RELATES_TO 关系
        
        Args:
            error_type_id: 错误类型节点 ID
            knowledge_point_ids: 知识点节点 ID 列表
            strength: 关联强度（0-1）
            confidence: 置信度（0-1）
            
        Returns:
            创建的 RELATES_TO 关系列表
            
        Raises:
            ValueError: 如果节点不存在
            RuntimeError: 如果数据库操作失败
        """
        if not knowledge_point_ids:
            return []
        
        relationships = []
        
        try:
            # 获取错误类型节点的内部 ID
            async with neo4j_connection.get_session() as session:
                get_error_query = """
                MATCH (e:ErrorType {error_type_id: $error_type_id})
                RETURN e.id as error_node_id
                """
                
                result = await session.run(get_error_query, error_type_id=error_type_id)
                error_record = await result.single()
                
                if not error_record:
                    raise ValueError(f"ErrorType not found: {error_type_id}")
                
                error_node_id = error_record["error_node_id"]
                
                # 为每个知识点创建 RELATES_TO 关系
                for kp_id in knowledge_point_ids:
                    # 获取知识点节点的内部 ID
                    get_kp_query = """
                    MATCH (k:KnowledgePoint {knowledge_point_id: $kp_id})
                    RETURN k.id as kp_node_id
                    """
                    
                    result = await session.run(get_kp_query, kp_id=kp_id)
                    kp_record = await result.single()
                    
                    if not kp_record:
                        logger.warning(
                            "knowledge_point_not_found",
                            knowledge_point_id=kp_id,
                        )
                        continue
                    
                    kp_node_id = kp_record["kp_node_id"]
                    
                    # 检查关系是否已存在
                    check_query = """
                    MATCH (e)-[r:RELATES_TO]->(k)
                    WHERE e.id = $error_node_id AND k.id = $kp_node_id
                    RETURN r
                    """
                    
                    result = await session.run(
                        check_query,
                        error_node_id=error_node_id,
                        kp_node_id=kp_node_id,
                    )
                    existing = await result.single()
                    
                    if existing:
                        logger.info(
                            "relates_to_relationship_already_exists",
                            error_type_id=error_type_id,
                            knowledge_point_id=kp_id,
                        )
                        continue
                    
                    # 创建 RELATES_TO 关系
                    relationship = await self.create_relationship(
                        from_node_id=error_node_id,
                        to_node_id=kp_node_id,
                        relationship_type=RelationshipType.RELATES_TO,
                        properties={
                            "strength": strength,
                            "confidence": confidence,
                        },
                    )
                    
                    relationships.append(relationship)
                
                logger.info(
                    "error_knowledge_points_associated",
                    error_type_id=error_type_id,
                    knowledge_points_count=len(relationships),
                )
                
                return relationships
        except Exception as e:
            logger.error(
                "error_knowledge_points_association_failed",
                error_type_id=error_type_id,
                error=str(e),
            )
            raise RuntimeError(f"Failed to associate error with knowledge points: {e}")
    
    async def aggregate_student_errors(
        self,
        student_id: str,
    ) -> Dict[str, Any]:
        """聚合学生的所有错误关系，生成错误分布统计
        
        Args:
            student_id: 学生 ID
            
        Returns:
            包含错误统计信息的字典
            
        Raises:
            ValueError: 如果学生不存在
            RuntimeError: 如果数据库操作失败
        """
        query = """
        MATCH (s:Student {student_id: $student_id})-[r:HAS_ERROR]->(e:ErrorType)
        OPTIONAL MATCH (e)-[:RELATES_TO]->(k:KnowledgePoint)
        WITH s, r, e, collect(DISTINCT k.knowledge_point_id) as knowledge_points
        RETURN 
            e.error_type_id as error_type_id,
            e.name as error_type_name,
            r.course_id as course_id,
            r.occurrence_count as occurrence_count,
            r.first_occurrence as first_occurrence,
            r.last_occurrence as last_occurrence,
            r.resolved as resolved,
            knowledge_points
        ORDER BY r.occurrence_count DESC
        """
        
        try:
            async with neo4j_connection.get_session() as session:
                result = await session.run(query, student_id=student_id)
                records = await result.data()
                
                if not records:
                    logger.warning("no_errors_found_for_student", student_id=student_id)
                    return {
                        "student_id": student_id,
                        "total_errors": 0,
                        "errors_by_course": {},
                        "errors_by_knowledge_point": {},
                        "errors_by_type": {},
                        "error_details": [],
                    }
                
                # 统计数据
                total_errors = 0
                errors_by_course = {}
                errors_by_knowledge_point = {}
                errors_by_type = {}
                error_details = []
                
                for record in records:
                    error_type_id = record["error_type_id"]
                    error_type_name = record["error_type_name"]
                    course_id = record["course_id"]
                    occurrence_count = record["occurrence_count"]
                    knowledge_points = record["knowledge_points"]
                    
                    total_errors += occurrence_count
                    
                    # 按课程统计
                    if course_id not in errors_by_course:
                        errors_by_course[course_id] = {
                            "count": 0,
                            "error_types": [],
                        }
                    errors_by_course[course_id]["count"] += occurrence_count
                    errors_by_course[course_id]["error_types"].append({
                        "error_type_id": error_type_id,
                        "error_type_name": error_type_name,
                        "count": occurrence_count,
                    })
                    
                    # 按知识点统计
                    for kp_id in knowledge_points:
                        if kp_id not in errors_by_knowledge_point:
                            errors_by_knowledge_point[kp_id] = {
                                "count": 0,
                                "error_types": [],
                            }
                        errors_by_knowledge_point[kp_id]["count"] += occurrence_count
                        if error_type_id not in [
                            e["error_type_id"]
                            for e in errors_by_knowledge_point[kp_id]["error_types"]
                        ]:
                            errors_by_knowledge_point[kp_id]["error_types"].append({
                                "error_type_id": error_type_id,
                                "error_type_name": error_type_name,
                            })
                    
                    # 按错误类型统计
                    if error_type_id not in errors_by_type:
                        errors_by_type[error_type_id] = {
                            "name": error_type_name,
                            "count": 0,
                            "courses": [],
                        }
                    errors_by_type[error_type_id]["count"] += occurrence_count
                    errors_by_type[error_type_id]["courses"].append(course_id)
                    
                    # 详细信息
                    error_details.append({
                        "error_type_id": error_type_id,
                        "error_type_name": error_type_name,
                        "course_id": course_id,
                        "occurrence_count": occurrence_count,
                        "first_occurrence": record["first_occurrence"],
                        "last_occurrence": record["last_occurrence"],
                        "resolved": record["resolved"],
                        "knowledge_points": knowledge_points,
                    })
                
                logger.info(
                    "student_errors_aggregated",
                    student_id=student_id,
                    total_errors=total_errors,
                )
                
                return {
                    "student_id": student_id,
                    "total_errors": total_errors,
                    "errors_by_course": errors_by_course,
                    "errors_by_knowledge_point": errors_by_knowledge_point,
                    "errors_by_type": errors_by_type,
                    "error_details": error_details,
                }
        except Exception as e:
            logger.error(
                "student_errors_aggregation_failed",
                student_id=student_id,
                error=str(e),
            )
            raise RuntimeError(f"Failed to aggregate student errors: {e}")
    
    async def find_cross_course_knowledge_point_paths(
        self,
        course_id_1: str,
        course_id_2: str,
        max_depth: int = 3,
    ) -> List[Dict[str, Any]]:
        """查询跨课程的知识点路径
        
        找到通过共同知识点连接两个课程的路径
        
        Args:
            course_id_1: 第一个课程 ID
            course_id_2: 第二个课程 ID
            max_depth: 最大路径深度
            
        Returns:
            路径列表，每个路径包含节点和关系信息
            
        Raises:
            ValueError: 如果课程不存在
            RuntimeError: 如果数据库操作失败
        """
        query = """
        MATCH (c1:Course {course_id: $course_id_1})
        MATCH (c2:Course {course_id: $course_id_2})
        MATCH path = (c1)-[:CONTAINS*1..2]->(k:KnowledgePoint)<-[:CONTAINS*1..2]-(c2)
        WITH path, k, c1, c2
        RETURN 
            k.knowledge_point_id as knowledge_point_id,
            k.name as knowledge_point_name,
            length(path) as path_length,
            [node in nodes(path) | {
                id: CASE 
                    WHEN 'Course' IN labels(node) THEN node.course_id
                    WHEN 'KnowledgePoint' IN labels(node) THEN node.knowledge_point_id
                    ELSE node.id
                END,
                type: labels(node)[0],
                name: node.name
            }] as nodes,
            [rel in relationships(path) | type(rel)] as relationship_types
        ORDER BY path_length
        LIMIT 100
        """
        
        try:
            async with neo4j_connection.get_session() as session:
                result = await session.run(
                    query,
                    course_id_1=course_id_1,
                    course_id_2=course_id_2,
                )
                records = await result.data()
                
                if not records:
                    logger.info(
                        "no_cross_course_paths_found",
                        course_id_1=course_id_1,
                        course_id_2=course_id_2,
                    )
                    return []
                
                paths = []
                for record in records:
                    paths.append({
                        "knowledge_point_id": record["knowledge_point_id"],
                        "knowledge_point_name": record["knowledge_point_name"],
                        "path_length": record["path_length"],
                        "nodes": record["nodes"],
                        "relationship_types": record["relationship_types"],
                    })
                
                logger.info(
                    "cross_course_paths_found",
                    course_id_1=course_id_1,
                    course_id_2=course_id_2,
                    paths_count=len(paths),
                )
                
                return paths
        except Exception as e:
            logger.error(
                "cross_course_path_query_failed",
                course_id_1=course_id_1,
                course_id_2=course_id_2,
                error=str(e),
            )
            raise RuntimeError(f"Failed to find cross-course knowledge point paths: {e}")
    
    async def update_repeated_error_weight(
        self,
        student_id: str,
        error_type_id: str,
        course_id: str,
    ) -> Relationship:
        """更新重复错误的权重
        
        当学生在同一知识点上重复出错时，增加对应 HAS_ERROR 关系的权重值
        
        Args:
            student_id: 学生 ID
            error_type_id: 错误类型 ID
            course_id: 课程 ID
            
        Returns:
            更新后的关系
            
        Raises:
            ValueError: 如果关系不存在
            RuntimeError: 如果数据库操作失败
        """
        query = """
        MATCH (s:Student {student_id: $student_id})-[r:HAS_ERROR]->(e:ErrorType {error_type_id: $error_type_id})
        WHERE r.course_id = $course_id
        SET r.occurrence_count = r.occurrence_count + 1,
            r.last_occurrence = datetime(),
            r.weight = r.occurrence_count + 1
        RETURN r, r.id as rel_id, s.id as from_id, e.id as to_id
        """
        
        try:
            async with neo4j_connection.get_session() as session:
                result = await session.run(
                    query,
                    student_id=student_id,
                    error_type_id=error_type_id,
                    course_id=course_id,
                )
                record = await result.single()
                
                if record is None:
                    raise ValueError(
                        f"Error relationship not found: student={student_id}, "
                        f"error_type={error_type_id}, course={course_id}"
                    )
                
                rel_data = dict(record["r"])
                rel_id = rel_data.pop("id", None)
                
                logger.info(
                    "repeated_error_weight_updated",
                    student_id=student_id,
                    error_type_id=error_type_id,
                    course_id=course_id,
                    new_occurrence_count=rel_data.get("occurrence_count"),
                    new_weight=rel_data.get("weight"),
                )
                
                return Relationship(
                    id=rel_id,
                    type=RelationshipType.HAS_ERROR,
                    from_node_id=record["from_id"],
                    to_node_id=record["to_id"],
                    properties=rel_data,
                    weight=rel_data.get("weight"),
                )
        except Exception as e:
            logger.error(
                "repeated_error_weight_update_failed",
                student_id=student_id,
                error_type_id=error_type_id,
                course_id=course_id,
                error=str(e),
            )
            raise RuntimeError(f"Failed to update repeated error weight: {e}")
    
    async def upsert_node(
        self,
        node_type: NodeType,
        unique_field: str,
        unique_value: Any,
        properties: Dict[str, Any],
        conflict_strategy: ConflictResolutionStrategy = ConflictResolutionStrategy.TIMESTAMP_PRIORITY,
    ) -> Node:
        """增量更新节点（如果不存在则创建，如果存在则更新）
        
        支持冲突解决策略
        
        Args:
            node_type: 节点类型
            unique_field: 唯一字段名
            unique_value: 唯一字段值
            properties: 节点属性
            conflict_strategy: 冲突解决策略
            
        Returns:
            创建或更新后的节点
            
        Raises:
            ValueError: 如果属性验证失败
            RuntimeError: 如果数据库操作失败
        """
        # 查找现有节点
        existing_node = await self._find_node_by_unique_field(
            node_type,
            unique_field,
            unique_value,
        )
        
        if existing_node is None:
            # 节点不存在，创建新节点
            logger.info(
                "upsert_node_creating_new",
                node_type=node_type,
                unique_field=unique_field,
                unique_value=unique_value,
            )
            return await self.create_node(node_type, properties)
        
        # 节点已存在，根据冲突策略处理
        if conflict_strategy == ConflictResolutionStrategy.KEEP_EXISTING:
            logger.info(
                "upsert_node_keeping_existing",
                node_id=existing_node.id,
                node_type=node_type,
            )
            return existing_node
        
        elif conflict_strategy == ConflictResolutionStrategy.TIMESTAMP_PRIORITY:
            # 时间戳优先：比较更新时间
            existing_updated_at = existing_node.updated_at
            new_updated_at = properties.get("updated_at")
            
            if new_updated_at:
                if isinstance(new_updated_at, str):
                    new_updated_at = datetime.fromisoformat(new_updated_at)
                
                if new_updated_at <= existing_updated_at:
                    logger.info(
                        "upsert_node_existing_is_newer",
                        node_id=existing_node.id,
                        existing_updated_at=existing_updated_at,
                        new_updated_at=new_updated_at,
                    )
                    return existing_node
            
            # 新数据更新，更新节点
            logger.info(
                "upsert_node_updating_with_newer_data",
                node_id=existing_node.id,
                node_type=node_type,
            )
            return await self.update_node(existing_node.id, properties)
        
        elif conflict_strategy == ConflictResolutionStrategy.MERGE_PROPERTIES:
            # 合并属性：保留现有属性，只更新新提供的属性
            merged_properties = {**existing_node.properties, **properties}
            merged_properties["updated_at"] = datetime.utcnow().isoformat()
            
            logger.info(
                "upsert_node_merging_properties",
                node_id=existing_node.id,
                node_type=node_type,
            )
            return await self.update_node(existing_node.id, merged_properties)
        
        else:
            raise ValueError(f"Unknown conflict resolution strategy: {conflict_strategy}")
    
    async def upsert_relationship(
        self,
        from_node_id: str,
        to_node_id: str,
        relationship_type: RelationshipType,
        properties: Optional[Dict[str, Any]] = None,
        conflict_strategy: ConflictResolutionStrategy = ConflictResolutionStrategy.TIMESTAMP_PRIORITY,
    ) -> Relationship:
        """增量更新关系（如果不存在则创建，如果存在则更新）
        
        支持冲突解决策略
        
        Args:
            from_node_id: 起始节点 ID
            to_node_id: 目标节点 ID
            relationship_type: 关系类型
            properties: 关系属性
            conflict_strategy: 冲突解决策略
            
        Returns:
            创建或更新后的关系
            
        Raises:
            ValueError: 如果节点不存在或属性验证失败
            RuntimeError: 如果数据库操作失败
        """
        properties = properties or {}
        
        # 查找现有关系
        query = f"""
        MATCH (from)-[r:{relationship_type.value}]->(to)
        WHERE from.id = $from_node_id AND to.id = $to_node_id
        RETURN r, r.id as rel_id
        """
        
        try:
            async with neo4j_connection.get_session() as session:
                result = await session.run(
                    query,
                    from_node_id=from_node_id,
                    to_node_id=to_node_id,
                )
                record = await result.single()
                
                if record is None:
                    # 关系不存在，创建新关系
                    logger.info(
                        "upsert_relationship_creating_new",
                        from_node_id=from_node_id,
                        to_node_id=to_node_id,
                        relationship_type=relationship_type,
                    )
                    return await self.create_relationship(
                        from_node_id,
                        to_node_id,
                        relationship_type,
                        properties,
                    )
                
                # 关系已存在
                rel_id = record["rel_id"]
                existing_rel_data = dict(record["r"])
                
                if conflict_strategy == ConflictResolutionStrategy.KEEP_EXISTING:
                    logger.info(
                        "upsert_relationship_keeping_existing",
                        relationship_id=rel_id,
                        relationship_type=relationship_type,
                    )
                    return Relationship(
                        id=rel_id,
                        type=relationship_type,
                        from_node_id=from_node_id,
                        to_node_id=to_node_id,
                        properties=existing_rel_data,
                        weight=existing_rel_data.get("weight"),
                    )
                
                elif conflict_strategy == ConflictResolutionStrategy.MERGE_PROPERTIES:
                    # 合并属性
                    merged_properties = {**existing_rel_data, **properties}
                    logger.info(
                        "upsert_relationship_merging_properties",
                        relationship_id=rel_id,
                        relationship_type=relationship_type,
                    )
                    return await self.update_relationship(rel_id, merged_properties)
                
                else:  # TIMESTAMP_PRIORITY or default
                    # 直接更新为新属性
                    logger.info(
                        "upsert_relationship_updating",
                        relationship_id=rel_id,
                        relationship_type=relationship_type,
                    )
                    return await self.update_relationship(rel_id, properties)
                
        except Exception as e:
            logger.error(
                "upsert_relationship_failed",
                from_node_id=from_node_id,
                to_node_id=to_node_id,
                relationship_type=relationship_type,
                error=str(e),
            )
            raise RuntimeError(f"Failed to upsert relationship: {e}")
    
    async def execute_batch(
        self,
        operations: List[GraphOperation],
        use_transaction: bool = True,
    ) -> BatchResult:
        """执行批量操作
        
        支持事务机制确保数据一致性。如果任何操作失败，所有操作都会回滚。
        
        Args:
            operations: 图操作列表
            use_transaction: 是否使用事务（默认为 True）
            
        Returns:
            批量操作结果
            
        Raises:
            RuntimeError: 如果批量操作失败
        """
        if not operations:
            return BatchResult(
                success=True,
                operations_count=0,
                successful_operations=0,
                failed_operations=0,
                results=[],
                errors=[],
            )
        
        results = []
        errors = []
        successful_count = 0
        failed_count = 0
        
        try:
            async with neo4j_connection.get_session() as session:
                if use_transaction:
                    # 使用事务执行所有操作
                    async with await session.begin_transaction() as tx:
                        try:
                            for i, operation in enumerate(operations):
                                try:
                                    result = await self._execute_single_operation_in_tx(
                                        tx,
                                        operation,
                                    )
                                    results.append(result)
                                    successful_count += 1
                                except Exception as e:
                                    error_msg = f"Operation {i} failed: {str(e)}"
                                    errors.append(error_msg)
                                    failed_count += 1
                                    logger.error(
                                        "batch_operation_failed",
                                        operation_index=i,
                                        operation_type=type(operation).__name__,
                                        error=str(e),
                                    )
                                    # 事务模式下，任何失败都会导致回滚
                                    raise
                            
                            # 所有操作成功，提交事务
                            await tx.commit()
                            
                            logger.info(
                                "batch_operations_committed",
                                operations_count=len(operations),
                                successful_operations=successful_count,
                            )
                            
                            return BatchResult(
                                success=True,
                                operations_count=len(operations),
                                successful_operations=successful_count,
                                failed_operations=failed_count,
                                results=results,
                                errors=errors,
                            )
                        
                        except Exception as e:
                            # 事务回滚
                            await tx.rollback()
                            logger.error(
                                "batch_operations_rolled_back",
                                operations_count=len(operations),
                                successful_before_failure=successful_count,
                                error=str(e),
                            )
                            raise RuntimeError(
                                f"Batch operation failed and rolled back: {e}"
                            )
                else:
                    # 不使用事务，逐个执行操作
                    for i, operation in enumerate(operations):
                        try:
                            result = await self._execute_single_operation(operation)
                            results.append(result)
                            successful_count += 1
                        except Exception as e:
                            error_msg = f"Operation {i} failed: {str(e)}"
                            errors.append(error_msg)
                            failed_count += 1
                            logger.error(
                                "batch_operation_failed_non_transactional",
                                operation_index=i,
                                operation_type=type(operation).__name__,
                                error=str(e),
                            )
                    
                    logger.info(
                        "batch_operations_completed_non_transactional",
                        operations_count=len(operations),
                        successful_operations=successful_count,
                        failed_operations=failed_count,
                    )
                    
                    return BatchResult(
                        success=failed_count == 0,
                        operations_count=len(operations),
                        successful_operations=successful_count,
                        failed_operations=failed_count,
                        results=results,
                        errors=errors,
                    )
        
        except Exception as e:
            logger.error(
                "batch_execution_failed",
                operations_count=len(operations),
                error=str(e),
            )
            raise RuntimeError(f"Failed to execute batch operations: {e}")
    
    async def _execute_single_operation(
        self,
        operation: GraphOperation,
    ) -> Any:
        """执行单个图操作（非事务模式）
        
        Args:
            operation: 图操作
            
        Returns:
            操作结果
        """
        if isinstance(operation, CreateNodeOperation):
            return await self.create_node(
                operation.node_type,
                operation.properties,
            )
        
        elif isinstance(operation, UpdateNodeOperation):
            return await self.update_node(
                operation.node_id,
                operation.properties,
            )
        
        elif isinstance(operation, CreateRelationshipOperation):
            return await self.create_relationship(
                operation.from_node_id,
                operation.to_node_id,
                operation.relationship_type,
                operation.properties,
            )
        
        elif isinstance(operation, UpdateRelationshipOperation):
            return await self.update_relationship(
                operation.relationship_id,
                operation.properties,
            )
        
        else:
            raise ValueError(f"Unknown operation type: {type(operation)}")
    
    async def _execute_single_operation_in_tx(
        self,
        tx,
        operation: GraphOperation,
    ) -> Any:
        """在事务中执行单个图操作
        
        Args:
            tx: Neo4j 事务对象
            operation: 图操作
            
        Returns:
            操作结果
        """
        if isinstance(operation, CreateNodeOperation):
            # 验证属性
            property_model = self.NODE_PROPERTY_MODELS.get(operation.node_type)
            if property_model is None:
                raise ValueError(f"Unknown node type: {operation.node_type}")
            
            validated_properties = property_model(**operation.properties)
            
            # 生成节点 ID
            node_id = str(uuid4())
            
            # 添加时间戳
            now = datetime.utcnow()
            properties_dict = validated_properties.model_dump()
            properties_dict["created_at"] = now.isoformat()
            properties_dict["updated_at"] = now.isoformat()
            
            # 创建节点
            query = f"""
            CREATE (n:{operation.node_type.value} $properties)
            SET n.id = $node_id
            RETURN n
            """
            
            result = await tx.run(
                query,
                properties=properties_dict,
                node_id=node_id,
            )
            record = await result.single()
            
            if record is None:
                raise RuntimeError("Failed to create node in transaction")
            
            return Node(
                id=node_id,
                type=operation.node_type,
                properties=dict(record["n"]),
                created_at=now,
                updated_at=now,
            )
        
        elif isinstance(operation, UpdateNodeOperation):
            # 添加更新时间戳
            properties = {**operation.properties}
            properties["updated_at"] = datetime.utcnow().isoformat()
            
            query = """
            MATCH (n)
            WHERE n.id = $node_id
            SET n += $properties
            RETURN n, labels(n) as labels
            """
            
            result = await tx.run(
                query,
                node_id=operation.node_id,
                properties=properties,
            )
            record = await result.single()
            
            if record is None:
                raise ValueError(f"Node not found: {operation.node_id}")
            
            node_data = dict(record["n"])
            node_type_str = record["labels"][0]
            node_type = NodeType(node_type_str)
            
            created_at = node_data.pop("created_at", None)
            updated_at = node_data.pop("updated_at", None)
            node_data.pop("id", None)
            
            return Node(
                id=operation.node_id,
                type=node_type,
                properties=node_data,
                created_at=datetime.fromisoformat(created_at) if created_at else datetime.utcnow(),
                updated_at=datetime.fromisoformat(updated_at) if updated_at else datetime.utcnow(),
            )
        
        elif isinstance(operation, CreateRelationshipOperation):
            # 验证关系属性
            validated_properties = self._validate_relationship_properties(
                operation.relationship_type,
                operation.properties,
            )
            
            # 计算关系权重
            weight = self._calculate_relationship_weight(
                operation.relationship_type,
                validated_properties,
            )
            
            if weight is not None:
                validated_properties["weight"] = weight
            
            # 生成关系 ID
            relationship_id = str(uuid4())
            
            # 创建关系
            query = f"""
            MATCH (from), (to)
            WHERE from.id = $from_node_id AND to.id = $to_node_id
            CREATE (from)-[r:{operation.relationship_type.value} $properties]->(to)
            SET r.id = $relationship_id
            RETURN r
            """
            
            result = await tx.run(
                query,
                from_node_id=operation.from_node_id,
                to_node_id=operation.to_node_id,
                properties=validated_properties,
                relationship_id=relationship_id,
            )
            record = await result.single()
            
            if record is None:
                raise ValueError("Failed to create relationship. Nodes may not exist.")
            
            rel_data = dict(record["r"])
            rel_data.pop("id", None)
            
            return Relationship(
                id=relationship_id,
                type=operation.relationship_type,
                from_node_id=operation.from_node_id,
                to_node_id=operation.to_node_id,
                properties=rel_data,
                weight=weight,
            )
        
        elif isinstance(operation, UpdateRelationshipOperation):
            query = """
            MATCH ()-[r]->()
            WHERE r.id = $relationship_id
            SET r += $properties
            RETURN r, type(r) as rel_type, startNode(r).id as from_id, endNode(r).id as to_id
            """
            
            result = await tx.run(
                query,
                relationship_id=operation.relationship_id,
                properties=operation.properties,
            )
            record = await result.single()
            
            if record is None:
                raise ValueError(f"Relationship not found: {operation.relationship_id}")
            
            rel_data = dict(record["r"])
            rel_data.pop("id", None)
            rel_type = RelationshipType(record["rel_type"])
            
            return Relationship(
                id=operation.relationship_id,
                type=rel_type,
                from_node_id=record["from_id"],
                to_node_id=record["to_id"],
                properties=rel_data,
                weight=rel_data.get("weight"),
            )
        
        else:
            raise ValueError(f"Unknown operation type: {type(operation)}")


# 全局服务实例
graph_service = GraphManagementService()
