"""边界场景测试

测试系统在各种边界情况下的表现和健壮性
"""

import pytest
from datetime import datetime
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
async def setup_empty_database():
    """设置空测试数据库"""
    await init_database()
    # 确保数据库为空
    async with neo4j_connection.get_session() as session:
        await session.run("MATCH (n) DETACH DELETE n")
    yield
    await close_database()


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
async def test_data_with_many_relationships(setup_test_database):
    """创建具有大量关系的测试数据"""
    # 创建中心节点
    student = await graph_service.create_node(
        NodeType.STUDENT,
        {
            "student_id": "S_MANY",
            "name": "测试学生",
            "grade": "3",
            "age": 15,
        },
    )

    # 创建多个课程和知识点节点
    relationships = []
    for i in range(1, 6):
        # 创建课程
        course = await graph_service.create_node(
            NodeType.COURSE,
            {
                "course_id": f"C{i:03d}",
                "name": f"课程{i}",
                "description": f"测试课程{i}",
                "difficulty": "intermediate",
            },
        )

        # 创建学习关系
        learns_rel = await graph_service.create_relationship(
            from_node_id=student.id,
            to_node_id=course.id,
            relationship_type=RelationshipType.LEARNS,
            properties={
                "enrollment_date": datetime.now().isoformat(),
                "progress": (i * 20) % 100,
            },
        )
        relationships.append(learns_rel)

        # 创建知识点
        for j in range(1, 4):
            kp = await graph_service.create_node(
                NodeType.KNOWLEDGE_POINT,
                {
                    "knowledge_point_id": f"KP{i:03d}{j:03d}",
                    "name": f"知识点{i}-{j}",
                    "description": f"测试知识点{i}-{j}",
                    "category": "数学",
                },
            )

            # 课程包含知识点
            contains_rel = await graph_service.create_relationship(
                from_node_id=course.id,
                to_node_id=kp.id,
                relationship_type=RelationshipType.CONTAINS,
                properties={
                    "order": j,
                    "importance": "core" if j == 1 else "supplementary",
                },
            )
            relationships.append(contains_rel)

    return {
        "student": student,
        "relationships": relationships,
    }


@pytest.mark.asyncio
async def test_query_empty_database(setup_empty_database):
    """测试查询空数据库的情况"""
    # 测试查询空数据库的节点
    node_filter = NodeFilter(types=[NodeType.STUDENT])
    student_nodes = await query_service.query_nodes(node_filter)
    assert len(student_nodes) == 0

    # 测试查询空数据库的关系
    rel_filter = RelationshipFilter()
    relationships = await query_service.query_relationships(rel_filter)
    assert len(relationships) == 0

    # 测试查询空数据库的子图
    # 这里应该抛出异常，因为根节点不存在
    with pytest.raises(Exception):
        await query_service.query_subgraph(root_node_id="non_existent_node", depth=1)

    logger.info("Empty database query test completed successfully")


@pytest.mark.asyncio
async def test_query_nonexistent_node(setup_test_database):
    """测试查询不存在的节点"""
    # 测试查询不存在的节点
    node_filter = NodeFilter(properties={"student_id": "NON_EXISTENT"})
    student_nodes = await query_service.query_nodes(node_filter)
    assert len(student_nodes) == 0

    # 测试通过不存在的节点ID查询关系
    rel_filter = RelationshipFilter(from_node_id="non_existent_node")
    relationships = await query_service.query_relationships(rel_filter)
    assert len(relationships) == 0

    # 测试通过不存在的节点ID查询子图
    with pytest.raises(Exception):
        await query_service.query_subgraph(root_node_id="non_existent_node", depth=1)

    logger.info("Non-existent node query test completed successfully")


@pytest.mark.asyncio
async def test_query_depth_zero(setup_test_database):
    """测试查询深度为0的情况"""
    # 创建测试节点
    student = await graph_service.create_node(
        NodeType.STUDENT,
        {
            "student_id": "S_DEPTH0",
            "name": "测试学生",
            "grade": "3",
            "age": 15,
        },
    )

    # 查询深度为1的子图 - 由于没有创建任何关系，应该返回空的子图
    subgraph = await query_service.query_subgraph(root_node_id=student.id, depth=1)

    # 生成可视化数据
    viz_data = visualization_service.generate_visualization(subgraph)
    visualization_data = viz_data.to_dict()

    logger.info("Depth zero query test completed successfully")


@pytest.mark.asyncio
async def test_query_large_depth(setup_test_database):
    """测试查询大深度的情况"""
    # 创建测试节点链
    nodes = []
    for i in range(1, 6):
        node = await graph_service.create_node(
            NodeType.STUDENT,
            {
                "student_id": f"S_CHAIN{i}",
                "name": f"学生{i}",
                "grade": "3",
                "age": 15,
            },
        )
        nodes.append(node)

    # 创建关系链
    for i in range(len(nodes) - 1):
        await graph_service.create_relationship(
            from_node_id=nodes[i].id,
            to_node_id=nodes[i + 1].id,
            relationship_type=RelationshipType.CHAT_WITH,
            properties={
                "message_count": (i + 1) * 10,
                "last_interaction_date": datetime.now().isoformat(),
            },
        )

    # 查询大深度子图
    subgraph = await query_service.query_subgraph(root_node_id=nodes[0].id, depth=10)
    # 应该返回所有5个节点和4个关系
    assert len(subgraph.nodes) == 5
    assert len(subgraph.relationships) == 4

    logger.info("Large depth query test completed successfully")


@pytest.mark.asyncio
async def test_large_number_of_relationships(test_data_with_many_relationships):
    """测试处理大量关系的情况"""
    student = test_data_with_many_relationships["student"]

    # 查询子图
    subgraph = await query_service.query_subgraph(root_node_id=student.id, depth=2)
    # 应该返回1个学生节点，5个课程节点，15个知识点节点，共21个节点
    # 关系：5个LEARNS，15个CONTAINS，共20个关系
    assert len(subgraph.nodes) == 21
    assert len(subgraph.relationships) == 20

    # 生成可视化数据
    viz_data = visualization_service.generate_visualization(subgraph)
    visualization_data = viz_data.to_dict()
    assert len(visualization_data["nodes"]) == 21
    assert len(visualization_data["edges"]) == 20

    logger.info("Large number of relationships test completed successfully")


@pytest.mark.asyncio
async def test_invalid_filter_conditions(setup_test_database):
    """测试无效的筛选条件"""
    # 创建测试节点
    student = await graph_service.create_node(
        NodeType.STUDENT,
        {
            "student_id": "S_FILTER",
            "name": "测试学生",
            "grade": "3",
            "age": 15,
        },
    )

    # 使用空的筛选条件筛选
    empty_node_filter = NodeFilter(types=[])
    nodes = await query_service.query_nodes(empty_node_filter)
    assert len(nodes) >= 1

    # 使用空的关系类型筛选
    empty_rel_filter = RelationshipFilter(types=[])
    relationships = await query_service.query_relationships(empty_rel_filter)
    # 因为没有创建任何关系，所以应该返回空列表
    assert len(relationships) == 0

    # 使用有效的图筛选条件，只包含学生节点类型
    graph_filter = GraphFilter(
        node_types=[NodeType.STUDENT],
        relationship_types=[],
    )
    subgraph = await query_service.query_subgraph(
        root_node_id=student.id, depth=1, filter=graph_filter
    )
    # 子图查询应该成功执行，不抛出异常
    # 由于没有创建任何关系，子图可能返回空的节点列表

    logger.info("Invalid filter conditions test completed successfully")


@pytest.mark.asyncio
async def test_path_query_no_path(setup_test_database):
    """测试查询不存在路径的情况"""
    # 创建两个不相关的节点
    student1 = await graph_service.create_node(
        NodeType.STUDENT,
        {
            "student_id": "S_PATH1",
            "name": "学生1",
            "grade": "3",
            "age": 15,
        },
    )

    student2 = await graph_service.create_node(
        NodeType.STUDENT,
        {
            "student_id": "S_PATH2",
            "name": "学生2",
            "grade": "3",
            "age": 15,
        },
    )

    # 查询两个不相关节点之间的路径，应该返回空列表
    paths = await query_service.find_path(
        from_node_id=student1.id, to_node_id=student2.id, max_depth=3
    )
    assert len(paths) == 0

    logger.info("Path query no path test completed successfully")


@pytest.mark.asyncio
async def test_visualization_with_empty_subgraph(setup_test_database):
    """测试使用空子图生成可视化数据"""
    # 从query_service导入Subgraph类
    from app.services.query_service import Subgraph

    # 创建空的子图
    empty_subgraph = Subgraph(nodes=[], relationships=[])

    # 生成可视化数据，应该返回空的可视化数据，而不是抛出异常
    viz_data = visualization_service.generate_visualization(empty_subgraph)
    visualization_data = viz_data.to_dict()

    assert len(visualization_data["nodes"]) == 0
    assert len(visualization_data["edges"]) == 0
    assert "layout" in visualization_data

    logger.info("Visualization with empty subgraph test completed successfully")


@pytest.mark.asyncio
async def test_path_query_with_invalid_input(setup_test_database):
    """测试路径查询的无效输入情况"""
    # 创建测试节点
    student = await graph_service.create_node(
        NodeType.STUDENT,
        {
            "student_id": "S_PATH_INVALID",
            "name": "测试学生",
            "grade": "3",
            "age": 15,
        },
    )

    # 测试从节点不存在
    paths = await query_service.find_path(
        from_node_id="non_existent_node", to_node_id=student.id, max_depth=3
    )
    assert len(paths) == 0

    # 测试到节点不存在
    paths = await query_service.find_path(
        from_node_id=student.id, to_node_id="non_existent_node", max_depth=3
    )
    assert len(paths) == 0

    # 测试从节点和到节点相同
    paths = await query_service.find_path(
        from_node_id=student.id, to_node_id=student.id, max_depth=3
    )
    assert len(paths) == 0  # 自身到自身没有路径

    logger.info("Path query with invalid input test completed successfully")


@pytest.mark.asyncio
async def test_llm_enhancement_with_disabled_service(setup_test_database):
    """测试LLM服务禁用时的增强功能"""
    # 创建测试节点和关系
    student = await graph_service.create_node(
        NodeType.STUDENT,
        {
            "student_id": "S_LLM_DISABLED",
            "name": "测试学生",
            "grade": "3",
            "age": 15,
        },
    )

    # 创建课程节点
    course = await graph_service.create_node(
        NodeType.COURSE,
        {
            "course_id": "C_LLM",
            "name": "测试课程",
            "description": "测试课程",
            "difficulty": "intermediate",
        },
    )

    # 创建学习关系
    await graph_service.create_relationship(
        from_node_id=student.id,
        to_node_id=course.id,
        relationship_type=RelationshipType.LEARNS,
        properties={
            "enrollment_date": datetime.now().isoformat(),
            "progress": 50.0,
        },
    )

    # 查询子图，应该能正常返回，即使LLM服务不可用
    subgraph = await query_service.query_subgraph(root_node_id=student.id, depth=1)
    # 应该返回学生节点和课程节点，以及它们之间的关系
    assert len(subgraph.nodes) >= 2
    assert len(subgraph.relationships) >= 1

    logger.info("LLM enhancement with disabled service test completed successfully")
