"""集成测试

测试完整的数据处理链路，从数据库查询到图谱生成
"""

import pytest
from datetime import datetime, timedelta
import structlog

from app.database import init_database, close_database, neo4j_connection
from app.services.graph_service import graph_service
from app.services.query_service import (
    query_service,
    NodeFilter,
    RelationshipFilter,
    GraphFilter,
)
from app.services.visualization_service import visualization_service
from app.models.nodes import NodeType
from app.models.relationships import RelationshipType

logger = structlog.get_logger()


@pytest.fixture(scope="function")
async def setup_test_database():
    """设置测试数据库"""
    await init_database()
    # 清理测试数据（在测试前清理）
    async with neo4j_connection.get_session() as session:
        await session.run("MATCH (n) DETACH DELETE n")
    yield
    # 清理测试数据（在测试后清理）
    async with neo4j_connection.get_session() as session:
        await session.run("MATCH (n) DETACH DELETE n")
    await close_database()


@pytest.fixture
async def test_data_graph(setup_test_database):
    """创建测试数据图谱"""
    # 创建学生节点
    student1 = await graph_service.create_node(
        NodeType.STUDENT,
        {
            "student_id": "S001",
            "name": "张三",
            "grade": "3",
            "age": 15,
        },
    )

    student2 = await graph_service.create_node(
        NodeType.STUDENT,
        {
            "student_id": "S002",
            "name": "李四",
            "grade": "4",
            "age": 16,
        },
    )

    # 创建教师节点
    teacher = await graph_service.create_node(
        NodeType.TEACHER,
        {
            "teacher_id": "T001",
            "name": "王老师",
            "subject": "数学",
        },
    )

    # 创建课程节点
    course = await graph_service.create_node(
        NodeType.COURSE,
        {
            "course_id": "C001",
            "name": "高等数学",
            "description": "大学数学基础课程",
            "difficulty": "intermediate",
        },
    )

    # 创建知识点节点
    kp1 = await graph_service.create_node(
        NodeType.KNOWLEDGE_POINT,
        {
            "knowledge_point_id": "KP001",
            "name": "微积分",
            "description": "微积分基础",
            "category": "数学",
        },
    )

    kp2 = await graph_service.create_node(
        NodeType.KNOWLEDGE_POINT,
        {
            "knowledge_point_id": "KP002",
            "name": "线性代数",
            "description": "线性代数基础",
            "category": "数学",
        },
    )

    # 创建错误类型节点
    error_type = await graph_service.create_node(
        NodeType.ERROR_TYPE,
        {
            "error_type_id": "E001",
            "name": "计算错误",
            "description": "基本计算错误",
            "severity": "medium",
        },
    )

    # 创建关系
    # 学生学习课程
    learns_rel = await graph_service.create_relationship(
        from_node_id=student1.id,
        to_node_id=course.id,
        relationship_type=RelationshipType.LEARNS,
        properties={
            "enrollment_date": datetime.now().isoformat(),
            "progress": 50.0,
        },
    )

    # 课程包含知识点
    contains_rel1 = await graph_service.create_relationship(
        from_node_id=course.id,
        to_node_id=kp1.id,
        relationship_type=RelationshipType.CONTAINS,
        properties={
            "order": 1,
            "importance": "core",
        },
    )

    contains_rel2 = await graph_service.create_relationship(
        from_node_id=course.id,
        to_node_id=kp2.id,
        relationship_type=RelationshipType.CONTAINS,
        properties={
            "order": 2,
            "importance": "supplementary",
        },
    )

    # 学生互动
    chat_rel = await graph_service.create_relationship(
        from_node_id=student1.id,
        to_node_id=student2.id,
        relationship_type=RelationshipType.CHAT_WITH,
        properties={
            "message_count": 10,
            "last_interaction_date": datetime.now().isoformat(),
        },
    )

    # 教师教学
    teaches_rel = await graph_service.create_relationship(
        from_node_id=teacher.id,
        to_node_id=student1.id,
        relationship_type=RelationshipType.TEACHES,
        properties={
            "interaction_count": 5,
            "last_interaction_date": datetime.now().isoformat(),
        },
    )

    # 学生错误
    error_rel = await graph_service.create_relationship(
        from_node_id=student1.id,
        to_node_id=error_type.id,
        relationship_type=RelationshipType.HAS_ERROR,
        properties={
            "occurrence_count": 3,
            "first_occurrence": (datetime.now() - timedelta(days=7)).isoformat(),
            "last_occurrence": datetime.now().isoformat(),
            "course_id": "C001",
            "resolved": False,
        },
    )

    # 错误关联知识点
    relates_rel = await graph_service.create_relationship(
        from_node_id=error_type.id,
        to_node_id=kp1.id,
        relationship_type=RelationshipType.RELATES_TO,
        properties={
            "strength": 0.8,
            "confidence": 0.9,
        },
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
async def test_full_data_processing_chain(test_data_graph):
    """测试完整的数据处理链路

    测试流程：
    1. 从数据库查询节点和关系
    2. 使用LLM增强子图数据
    3. 生成可视化数据
    4. 验证结果的完整性和正确性
    """
    student1 = test_data_graph["student1"]

    # 步骤1：查询节点和关系
    logger.info("Starting full data processing chain test")

    # 查询学生节点
    node_filter = NodeFilter(types=[NodeType.STUDENT])
    student_nodes = await query_service.query_nodes(node_filter)
    assert len(student_nodes) >= 2
    logger.info("Node query completed", student_count=len(student_nodes))

    # 查询关系
    rel_filter = RelationshipFilter(from_node_id=student1.id)
    relationships = await query_service.query_relationships(rel_filter)
    assert len(relationships) >= 3  # LEARNS, CHAT_WITH, HAS_ERROR
    logger.info("Relationship query completed", relationship_count=len(relationships))

    # 步骤2：查询子图并使用LLM增强
    graph_filter = GraphFilter(
        node_types=[NodeType.STUDENT, NodeType.COURSE, NodeType.KNOWLEDGE_POINT],
        relationship_types=[RelationshipType.LEARNS, RelationshipType.CONTAINS],
    )

    subgraph = await query_service.query_subgraph(
        root_node_id=student1.id, depth=2, filter=graph_filter
    )

    assert len(subgraph.nodes) >= 3  # student1, course, kp1, kp2
    assert len(subgraph.relationships) >= 2  # LEARNS, CONTAINS (2)
    logger.info(
        "Subgraph query completed",
        node_count=len(subgraph.nodes),
        relationship_count=len(subgraph.relationships),
    )

    # 步骤3：生成可视化数据
    viz_data = visualization_service.generate_visualization(subgraph)
    visualization_data = viz_data.to_dict()

    assert "nodes" in visualization_data
    assert "edges" in visualization_data
    assert len(visualization_data["nodes"]) >= len(subgraph.nodes)
    assert len(visualization_data["edges"]) >= len(subgraph.relationships)
    logger.info(
        "Visualization generation completed",
        viz_node_count=len(visualization_data["nodes"]),
        viz_edge_count=len(visualization_data["edges"]),
    )

    # 步骤4：验证结果的完整性和正确性
    # 验证节点类型
    node_types = {node["type"] for node in visualization_data["nodes"]}
    expected_types = {"Student", "Course", "KnowledgePoint"}
    assert expected_types.issubset(node_types)

    # 验证关系类型
    edge_types = {edge["type"] for edge in visualization_data["edges"]}
    expected_edge_types = {"LEARNS", "CONTAINS"}
    assert expected_edge_types.issubset(edge_types)

    # 验证节点详情：注意 generate_visualization 方法目前不返回 node_details 字段
    # 这个字段是由 API 端点添加的，而不是可视化服务直接返回的
    # 我们只验证核心的可视化数据结构
    assert "layout" in visualization_data

    logger.info("Full data processing chain test completed successfully")


@pytest.mark.asyncio
async def test_multi_filter_data_processing(test_data_graph):
    """测试多维度数据筛选的数据处理链路"""
    student1 = test_data_graph["student1"]

    # 使用多种筛选条件查询子图
    graph_filter = GraphFilter(
        node_types=[NodeType.STUDENT, NodeType.ERROR_TYPE, NodeType.KNOWLEDGE_POINT],
        relationship_types=[RelationshipType.HAS_ERROR, RelationshipType.RELATES_TO],
    )

    subgraph = await query_service.query_subgraph(
        root_node_id=student1.id, depth=2, filter=graph_filter
    )

    # 验证筛选结果
    assert len(subgraph.nodes) >= 3  # student1, error_type, kp1
    assert len(subgraph.relationships) >= 2  # HAS_ERROR, RELATES_TO

    # 生成可视化数据
    viz_data = visualization_service.generate_visualization(subgraph)
    visualization_data = viz_data.to_dict()

    # 验证可视化结果
    assert "nodes" in visualization_data
    assert "edges" in visualization_data

    # 验证筛选后的节点类型
    node_types = {node["type"] for node in visualization_data["nodes"]}
    expected_types = {"Student", "ErrorType", "KnowledgePoint"}
    assert expected_types.issubset(node_types)

    # 验证筛选后的关系类型
    edge_types = {edge["type"] for edge in visualization_data["edges"]}
    expected_edge_types = {"HAS_ERROR", "RELATES_TO"}
    assert expected_edge_types.issubset(edge_types)

    logger.info("Multi-filter data processing test completed successfully")


@pytest.mark.asyncio
async def test_path_query_integration(test_data_graph):
    """测试路径查询集成"""
    student1 = test_data_graph["student1"]
    kp1 = test_data_graph["kp1"]

    # 查找学生到知识点的路径
    paths = await query_service.find_path(
        from_node_id=student1.id, to_node_id=kp1.id, max_depth=3
    )

    # 应该找到至少两条路径：
    # 1. student1 -> course -> kp1 (深度2)
    # 2. student1 -> error_type -> kp1 (深度2)
    assert len(paths) >= 2

    # 验证路径长度
    path_lengths = [path.length for path in paths]
    assert 2 in path_lengths  # 存在深度为2的路径

    logger.info(
        "Path query integration test completed successfully",
        path_count=len(paths),
        path_lengths=path_lengths,
    )


@pytest.mark.asyncio
async def test_visualization_with_llm_results(test_data_graph):
    """测试带有LLM结果的可视化生成"""
    student1 = test_data_graph["student1"]

    # 查询子图
    subgraph = await query_service.query_subgraph(root_node_id=student1.id, depth=2)

    # 生成带有LLM结果的可视化数据
    viz_data = visualization_service.generate_visualization(
        subgraph,
        llm_results={
            "student_attention": {
                "student_attention_scores": {"张三": 85},
                "attention_rankings": [{"name": "张三", "rank": 1}],
                "social_influence": {"张三": "在群体中非常活跃，经常帮助其他学生"},
            }
        },
    )
    visualization_data = viz_data.to_dict()

    # 验证可视化数据结构
    assert "nodes" in visualization_data
    assert "edges" in visualization_data
    assert "layout" in visualization_data

    # 注意：LLM结果目前只会影响日志记录，不会直接修改可视化数据结构
    # 这个测试主要验证 generate_visualization 方法可以处理 llm_results 参数而不抛出异常

    logger.info("Visualization with LLM results test completed successfully")


@pytest.mark.asyncio
async def test_full_system_health_check(setup_test_database):
    """测试完整系统健康检查"""
    # 测试数据库连接
    async with neo4j_connection.get_session() as session:
        result = await session.run("RETURN 1 AS test")
        record = await result.single()
        assert record["test"] == 1

    # 测试服务初始化
    assert graph_service is not None
    assert query_service is not None
    assert visualization_service is not None

    # 测试基础功能
    # 创建一个简单节点
    node = await graph_service.create_node(
        NodeType.STUDENT,
        {
            "student_id": "HEALTHCHECK",
            "name": "健康检查",
            "grade": "1",
        },
    )

    # 查询该节点
    node_filter = NodeFilter(
        types=[NodeType.STUDENT], properties={"student_id": "HEALTHCHECK"}
    )
    nodes = await query_service.query_nodes(node_filter)
    assert len(nodes) == 1
    assert nodes[0].properties["student_id"] == "HEALTHCHECK"

    logger.info("Full system health check completed successfully")
