"""图查询服务集成测试"""

import pytest
from datetime import datetime, timedelta
import structlog

from app.database import init_database, close_database, neo4j_connection

logger = structlog.get_logger()
from app.services.graph_service import graph_service
from app.services.query_service import (
    query_service,
    NodeFilter,
    RelationshipFilter,
    GraphFilter,
)
from app.services.llm_service import get_llm_service
from app.models.nodes import NodeType
from app.models.relationships import RelationshipType


@pytest.fixture(scope="function")
async def setup_database():
    """设置测试数据库"""
    await init_database()
    # 清理测试数据（在测试前清理）
    async with neo4j_connection.get_session() as session:
        await session.run("MATCH (n) DETACH DELETE n")
    yield
    # 清理测试数据（在测试后清理）
    async with neo4j_connection.get_session() as session:
        await session.run("MATCH (n) DETACH DELETE n")


@pytest.fixture
async def sample_graph(setup_database):
    """创建示例图谱数据"""
    # 创建学生节点
    student1 = await graph_service.create_node(
        NodeType.STUDENT,
        {
            "student_id": "S001",
            "name": "张三",
            "grade": "3",
        }
    )
    
    student2 = await graph_service.create_node(
        NodeType.STUDENT,
        {
            "student_id": "S002",
            "name": "李四",
            "grade": "4",
        }
    )
    
    # 创建教师节点
    teacher = await graph_service.create_node(
        NodeType.TEACHER,
        {
            "teacher_id": "T001",
            "name": "王老师",
            "subject": "数学",
        }
    )
    
    # 创建课程节点
    course = await graph_service.create_node(
        NodeType.COURSE,
        {
            "course_id": "C001",
            "name": "高等数学",
            "description": "大学数学基础课程",
            "difficulty": "intermediate",
        }
    )
    
    # 创建知识点节点
    kp1 = await graph_service.create_node(
        NodeType.KNOWLEDGE_POINT,
        {
            "knowledge_point_id": "KP001",
            "name": "微积分",
            "description": "微积分基础",
            "category": "数学",
        }
    )
    
    kp2 = await graph_service.create_node(
        NodeType.KNOWLEDGE_POINT,
        {
            "knowledge_point_id": "KP002",
            "name": "线性代数",
            "description": "线性代数基础",
            "category": "数学",
        }
    )
    
    # 创建错误类型节点
    error_type = await graph_service.create_node(
        NodeType.ERROR_TYPE,
        {
            "error_type_id": "E001",
            "name": "计算错误",
            "description": "基本计算错误",
            "severity": "medium",
        }
    )
    
    # 创建关系
    # 学生学习课程
    learns_rel = await graph_service.create_relationship(
        from_node_id=student1.id,
        to_node_id=course.id,
        relationship_type=RelationshipType.LEARNS,
        properties={
            "enrollment_date": datetime.utcnow(),
            "progress": 50.0,
        }
    )
    
    # 课程包含知识点
    contains_rel1 = await graph_service.create_relationship(
        from_node_id=course.id,
        to_node_id=kp1.id,
        relationship_type=RelationshipType.CONTAINS,
        properties={
            "order": 1,
            "importance": "core",
        }
    )
    
    contains_rel2 = await graph_service.create_relationship(
        from_node_id=course.id,
        to_node_id=kp2.id,
        relationship_type=RelationshipType.CONTAINS,
        properties={
            "order": 2,
            "importance": "supplementary",
        }
    )
    
    # 学生互动
    chat_rel = await graph_service.create_relationship(
        from_node_id=student1.id,
        to_node_id=student2.id,
        relationship_type=RelationshipType.CHAT_WITH,
        properties={
            "message_count": 10,
            "last_interaction_date": datetime.utcnow(),
        }
    )
    
    # 教师教学
    teaches_rel = await graph_service.create_relationship(
        from_node_id=teacher.id,
        to_node_id=student1.id,
        relationship_type=RelationshipType.TEACHES,
        properties={
            "interaction_count": 5,
            "last_interaction_date": datetime.utcnow(),
        }
    )
    
    # 学生错误
    error_rel = await graph_service.create_relationship(
        from_node_id=student1.id,
        to_node_id=error_type.id,
        relationship_type=RelationshipType.HAS_ERROR,
        properties={
            "occurrence_count": 3,
            "first_occurrence": datetime.utcnow() - timedelta(days=7),
            "last_occurrence": datetime.utcnow(),
            "course_id": "C001",
            "resolved": False,
        }
    )
    
    # 错误关联知识点
    relates_rel = await graph_service.create_relationship(
        from_node_id=error_type.id,
        to_node_id=kp1.id,
        relationship_type=RelationshipType.RELATES_TO,
        properties={
            "strength": 0.8,
            "confidence": 0.9,
        }
    )
    
    return {
        "student1": student1,
        "student2": student2,
        "teacher": teacher,
        "course": course,
        "kp1": kp1,
        "kp2": kp2,
        "error_type": error_type,
        "learns_rel": learns_rel,
        "contains_rel1": contains_rel1,
        "contains_rel2": contains_rel2,
        "chat_rel": chat_rel,
        "teaches_rel": teaches_rel,
        "error_rel": error_rel,
        "relates_rel": relates_rel,
    }


@pytest.mark.asyncio
async def test_query_nodes_by_type(sample_graph):
    """测试按类型查询节点"""
    # 查询所有学生节点
    filter = NodeFilter(types=[NodeType.STUDENT])
    nodes = await query_service.query_nodes(filter)
    
    assert len(nodes) == 2
    assert all(node.type == NodeType.STUDENT for node in nodes)


@pytest.mark.asyncio
async def test_query_nodes_by_properties(sample_graph):
    """测试按属性查询节点"""
    # 查询特定学生
    filter = NodeFilter(
        types=[NodeType.STUDENT],
        properties={"student_id": "S001"}
    )
    nodes = await query_service.query_nodes(filter)
    
    assert len(nodes) == 1
    assert nodes[0].properties["student_id"] == "S001"
    assert nodes[0].properties["name"] == "张三"


@pytest.mark.asyncio
async def test_query_nodes_with_pagination(sample_graph):
    """测试分页查询节点"""
    # 查询第一页
    filter = NodeFilter(types=[NodeType.STUDENT], limit=1, offset=0)
    nodes_page1 = await query_service.query_nodes(filter)
    
    assert len(nodes_page1) == 1
    
    # 查询第二页
    filter = NodeFilter(types=[NodeType.STUDENT], limit=1, offset=1)
    nodes_page2 = await query_service.query_nodes(filter)
    
    assert len(nodes_page2) == 1
    assert nodes_page1[0].id != nodes_page2[0].id


@pytest.mark.asyncio
async def test_query_nodes_by_date_range(sample_graph):
    """测试按日期范围查询节点"""
    # 查询最近创建的节点
    now = datetime.utcnow()
    yesterday = now - timedelta(days=1)
    
    filter = NodeFilter(
        date_range={"start": yesterday, "end": now}
    )
    nodes = await query_service.query_nodes(filter)
    
    # 应该返回所有节点（因为都是刚创建的）
    assert len(nodes) >= 7


@pytest.mark.asyncio
async def test_query_relationships_by_type(sample_graph):
    """测试按类型查询关系"""
    # 查询所有 CONTAINS 关系
    filter = RelationshipFilter(types=[RelationshipType.CONTAINS])
    relationships = await query_service.query_relationships(filter)
    
    assert len(relationships) == 2
    assert all(rel.type == RelationshipType.CONTAINS for rel in relationships)


@pytest.mark.asyncio
async def test_query_relationships_by_node(sample_graph):
    """测试按节点查询关系"""
    student1 = sample_graph["student1"]
    
    # 查询从学生1出发的所有关系
    filter = RelationshipFilter(from_node_id=student1.id)
    relationships = await query_service.query_relationships(filter)
    
    assert len(relationships) >= 3  # LEARNS, CHAT_WITH, HAS_ERROR
    assert all(rel.from_node_id == student1.id for rel in relationships)


@pytest.mark.asyncio
async def test_query_relationships_by_weight(sample_graph):
    """测试按权重查询关系"""
    # 查询权重大于等于 5 的关系
    filter = RelationshipFilter(min_weight=5.0)
    relationships = await query_service.query_relationships(filter)
    
    assert len(relationships) >= 1
    assert all(rel.weight >= 5.0 for rel in relationships if rel.weight is not None)


@pytest.mark.asyncio
async def test_query_subgraph(sample_graph):
    """测试查询子图"""
    student1 = sample_graph["student1"]
    
    # 查询深度为 2 的子图
    subgraph = await query_service.query_subgraph(
        root_node_id=student1.id,
        depth=2,
    )
    
    assert subgraph.metadata["node_count"] >= 4  # 至少包含学生、课程、知识点等
    assert subgraph.metadata["relationship_count"] >= 3
    assert len(subgraph.nodes) == subgraph.metadata["node_count"]
    assert len(subgraph.relationships) == subgraph.metadata["relationship_count"]


@pytest.mark.asyncio
async def test_query_subgraph_with_filter(sample_graph):
    """测试带过滤器的子图查询"""
    student1 = sample_graph["student1"]
    
    # 只查询学生和课程节点
    filter = GraphFilter(
        node_types=[NodeType.STUDENT, NodeType.COURSE],
        relationship_types=[RelationshipType.LEARNS],
    )
    
    subgraph = await query_service.query_subgraph(
        root_node_id=student1.id,
        depth=2,
        filter=filter,
    )
    
    # 应该只包含学生和课程节点
    assert all(
        node.type in [NodeType.STUDENT, NodeType.COURSE]
        for node in subgraph.nodes
    )
    
    # 应该只包含 LEARNS 关系
    assert all(
        rel.type == RelationshipType.LEARNS
        for rel in subgraph.relationships
    )


@pytest.mark.asyncio
async def test_find_path(sample_graph):
    """测试路径查询"""
    student1 = sample_graph["student1"]
    course = sample_graph["course"]
    
    # 查找学生到课程的直接路径（应该只有一条）
    paths = await query_service.find_path(
        from_node_id=student1.id,
        to_node_id=course.id,
        max_depth=1,
    )
    
    assert len(paths) >= 1
    
    # 验证路径
    path = paths[0]
    assert path.nodes[0].id == student1.id
    assert path.nodes[-1].id == course.id
    assert path.length == 1  # 直接关系


@pytest.mark.asyncio
async def test_find_path_no_connection(sample_graph):
    """测试查询不存在的路径"""
    student1 = sample_graph["student1"]
    student2 = sample_graph["student2"]
    
    # 创建一个孤立的节点
    isolated_node = await graph_service.create_node(
        NodeType.STUDENT,
        {
            "student_id": "S999",
            "name": "孤立学生",
        }
    )
    
    # 查找学生1到孤立节点的路径（应该找不到）
    paths = await query_service.find_path(
        from_node_id=student1.id,
        to_node_id=isolated_node.id,
        max_depth=5,
    )
    
    assert len(paths) == 0


@pytest.mark.asyncio
async def test_query_nodes_empty_result(setup_database):
    """测试查询空结果"""
    # 查询不存在的节点类型组合
    filter = NodeFilter(
        types=[NodeType.STUDENT],
        properties={"student_id": "NONEXISTENT"}
    )
    nodes = await query_service.query_nodes(filter)
    
    assert len(nodes) == 0


@pytest.mark.asyncio
async def test_query_relationships_empty_result(setup_database):
    """测试查询空关系结果"""
    # 查询不存在的关系
    filter = RelationshipFilter(
        types=[RelationshipType.CHAT_WITH],
        from_node_id="NONEXISTENT",
    )
    relationships = await query_service.query_relationships(filter)
    
    assert len(relationships) == 0


@pytest.mark.asyncio
async def test_query_subgraph_invalid_root(setup_database):
    """测试查询不存在的根节点"""
    with pytest.raises(ValueError, match="Root node not found"):
        await query_service.query_subgraph(
            root_node_id="NONEXISTENT",
            depth=2,
        )


@pytest.mark.asyncio
async def test_find_path_invalid_depth(sample_graph):
    """测试无效的路径深度"""
    student1 = sample_graph["student1"]
    kp1 = sample_graph["kp1"]
    
    with pytest.raises(ValueError, match="Max depth must be at least 1"):
        await query_service.find_path(
            from_node_id=student1.id,
            to_node_id=kp1.id,
            max_depth=0,
        )


@pytest.mark.asyncio
async def test_subgraph_enhancement_with_llm(sample_graph):
    """测试使用LLM增强子图数据"""
    student1 = sample_graph["student1"]
    
    # 查询子图，验证是否调用了LLM增强
    subgraph = await query_service.query_subgraph(
        root_node_id=student1.id,
        depth=2,
    )
    
    # 验证子图不为空
    assert len(subgraph.nodes) > 0
    assert len(subgraph.relationships) > 0
    
    # 这个测试主要验证子图查询功能是否正常，以及LLM增强逻辑是否能正确处理
    # LLM服务未初始化的情况（应该跳过增强而不是抛出异常）
    logger.info("subgraph_enhancement_test_complete", node_count=len(subgraph.nodes), relationship_count=len(subgraph.relationships))
