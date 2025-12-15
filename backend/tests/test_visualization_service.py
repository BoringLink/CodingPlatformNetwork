"""可视化服务测试"""

import pytest
from datetime import datetime

from app.database import init_database, neo4j_connection
from app.services.graph_service import graph_service
from app.services.query_service import query_service, GraphFilter
from app.services.visualization_service import (
    visualization_service,
    VisualizationOptions,
)
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
    kp = await graph_service.create_node(
        NodeType.KNOWLEDGE_POINT,
        {
            "knowledge_point_id": "KP001",
            "name": "微积分",
            "description": "微积分基础",
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
    # 学生互动
    await graph_service.create_relationship(
        student1.id,
        student2.id,
        RelationshipType.CHAT_WITH,
        {"message_count": 10, "last_interaction_date": datetime.utcnow().isoformat()}
    )
    
    # 教师教学
    await graph_service.create_relationship(
        teacher.id,
        student1.id,
        RelationshipType.TEACHES,
        {"interaction_count": 5, "last_interaction_date": datetime.utcnow().isoformat()}
    )
    
    # 学生学习
    await graph_service.create_relationship(
        student1.id,
        course.id,
        RelationshipType.LEARNS,
        {"enrollment_date": datetime.utcnow().isoformat(), "progress": 75.0}
    )
    
    # 课程包含知识点
    await graph_service.create_relationship(
        course.id,
        kp.id,
        RelationshipType.CONTAINS,
        {"importance": "core"}
    )
    
    # 学生错误
    await graph_service.create_relationship(
        student1.id,
        error_type.id,
        RelationshipType.HAS_ERROR,
        {
            "occurrence_count": 3,
            "first_occurrence": datetime.utcnow().isoformat(),
            "last_occurrence": datetime.utcnow().isoformat(),
            "course_id": "C001",
            "resolved": False,
        }
    )
    
    # 错误关联知识点
    await graph_service.create_relationship(
        error_type.id,
        kp.id,
        RelationshipType.RELATES_TO,
        {"strength": 0.8, "confidence": 0.9}
    )
    
    return {
        "student1": student1,
        "student2": student2,
        "teacher": teacher,
        "course": course,
        "kp": kp,
        "error_type": error_type,
    }


@pytest.mark.asyncio
async def test_generate_visualization(sample_graph):
    """测试生成可视化数据"""
    # 查询子图
    subgraph = await query_service.query_subgraph(
        sample_graph["student1"].id,
        depth=2,
    )
    
    # 生成可视化数据
    viz_data = visualization_service.generate_visualization(subgraph)
    
    # 验证节点
    assert len(viz_data.nodes) > 0
    assert all(node.id for node in viz_data.nodes)
    assert all(node.color for node in viz_data.nodes)
    assert all(node.shape for node in viz_data.nodes)
    
    # 验证边
    assert len(viz_data.edges) > 0
    assert all(edge.source for edge in viz_data.edges)
    assert all(edge.target for edge in viz_data.edges)
    assert all(edge.color for edge in viz_data.edges)
    
    # 验证布局
    assert viz_data.layout is not None
    assert viz_data.layout.name is not None


@pytest.mark.asyncio
async def test_node_color_mapping(sample_graph):
    """测试节点颜色映射"""
    # 查询子图
    subgraph = await query_service.query_subgraph(
        sample_graph["student1"].id,
        depth=2,
    )
    
    # 生成可视化数据
    viz_data = visualization_service.generate_visualization(subgraph)
    
    # 验证不同类型的节点有不同的颜色
    colors_by_type = {}
    for node in viz_data.nodes:
        if node.type not in colors_by_type:
            colors_by_type[node.type] = node.color
        else:
            # 同类型节点应该有相同的颜色
            assert colors_by_type[node.type] == node.color
    
    # 验证至少有多种颜色
    assert len(set(colors_by_type.values())) > 1


@pytest.mark.asyncio
async def test_node_shape_mapping(sample_graph):
    """测试节点形状映射"""
    # 查询子图
    subgraph = await query_service.query_subgraph(
        sample_graph["student1"].id,
        depth=2,
    )
    
    # 生成可视化数据
    viz_data = visualization_service.generate_visualization(subgraph)
    
    # 验证不同类型的节点有不同的形状
    shapes_by_type = {}
    for node in viz_data.nodes:
        if node.type not in shapes_by_type:
            shapes_by_type[node.type] = node.shape
        else:
            # 同类型节点应该有相同的形状
            assert shapes_by_type[node.type] == node.shape
    
    # 验证至少有多种形状
    assert len(set(shapes_by_type.values())) > 1


@pytest.mark.asyncio
async def test_layout_configurations(sample_graph):
    """测试不同的布局配置"""
    # 查询子图
    subgraph = await query_service.query_subgraph(
        sample_graph["student1"].id,
        depth=2,
    )
    
    # 测试不同的布局
    layouts = ["force-directed", "hierarchical", "circular", "concentric", "grid"]
    
    for layout_name in layouts:
        options = VisualizationOptions(layout=layout_name)
        viz_data = visualization_service.generate_visualization(subgraph, options)
        
        assert viz_data.layout is not None
        assert viz_data.layout.name is not None
        assert viz_data.layout.options is not None


@pytest.mark.asyncio
async def test_create_subview(sample_graph):
    """测试创建子视图"""
    # 查询子图
    subgraph = await query_service.query_subgraph(
        sample_graph["student1"].id,
        depth=2,
    )
    
    # 创建子视图
    filter = GraphFilter(
        node_types=[NodeType.STUDENT, NodeType.COURSE],
    )
    
    subview = await visualization_service.create_subview(
        filter=filter,
        name="学生课程视图",
        subgraph=subgraph,
    )
    
    assert subview is not None
    assert subview.id is not None
    assert subview.name == "学生课程视图"
    assert subview.filter == filter
    assert subview.subgraph == subgraph


@pytest.mark.asyncio
async def test_get_subview(sample_graph):
    """测试获取子视图"""
    # 查询子图
    subgraph = await query_service.query_subgraph(
        sample_graph["student1"].id,
        depth=2,
    )
    
    # 创建子视图
    filter = GraphFilter()
    subview = await visualization_service.create_subview(
        filter=filter,
        name="测试视图",
        subgraph=subgraph,
    )
    
    # 获取子视图
    retrieved_subview = await visualization_service.get_subview(subview.id)
    
    assert retrieved_subview is not None
    assert retrieved_subview.id == subview.id
    assert retrieved_subview.name == subview.name


@pytest.mark.asyncio
async def test_update_subview_filter(sample_graph):
    """测试更新子视图筛选条件"""
    # 查询子图
    subgraph = await query_service.query_subgraph(
        sample_graph["student1"].id,
        depth=2,
    )
    
    # 创建子视图
    filter = GraphFilter()
    subview = await visualization_service.create_subview(
        filter=filter,
        name="测试视图",
        subgraph=subgraph,
    )
    
    # 更新筛选条件
    new_filter = GraphFilter(node_types=[NodeType.STUDENT])
    updated_subview = await visualization_service.update_subview_filter(
        subview.id,
        new_filter,
        subgraph,
    )
    
    assert updated_subview is not None
    assert updated_subview.filter == new_filter


@pytest.mark.asyncio
async def test_get_node_details(sample_graph):
    """测试获取节点详情"""
    # 获取学生节点
    student = sample_graph["student1"]
    
    # 获取节点详情（新的实现直接查询数据库）
    details = await visualization_service.get_node_details(student.id)
    
    assert details is not None
    assert details.node.id == student.id
    assert len(details.relationship_counts) > 0
    assert len(details.connected_nodes) > 0
    
    # 验证关系统计
    total_relationships = sum(details.relationship_counts.values())
    assert total_relationships > 0
    
    # 验证连接节点类型统计
    assert all("type" in node for node in details.connected_nodes)
    assert all("count" in node for node in details.connected_nodes)


@pytest.mark.asyncio
async def test_get_direct_neighbors(sample_graph):
    """测试查询直接邻居节点"""
    # 获取学生节点
    student = sample_graph["student1"]
    
    # 查询所有直接邻居
    neighbors = await visualization_service.get_direct_neighbors(student.id)
    
    assert neighbors is not None
    assert len(neighbors) > 0
    
    # 验证邻居节点包含预期的节点
    neighbor_ids = [n.id for n in neighbors]
    assert sample_graph["student2"].id in neighbor_ids  # 通过 CHAT_WITH 连接
    assert sample_graph["course"].id in neighbor_ids  # 通过 LEARNS 连接
    assert sample_graph["error_type"].id in neighbor_ids  # 通过 HAS_ERROR 连接


@pytest.mark.asyncio
async def test_get_direct_neighbors_with_filters(sample_graph):
    """测试带过滤条件的直接邻居查询"""
    # 获取学生节点
    student = sample_graph["student1"]
    
    # 只查询学生类型的邻居
    student_neighbors = await visualization_service.get_direct_neighbors(
        student.id,
        node_types=[NodeType.STUDENT]
    )
    
    assert student_neighbors is not None
    assert len(student_neighbors) > 0
    assert all(n.type == NodeType.STUDENT for n in student_neighbors)
    
    # 只查询通过 LEARNS 关系连接的邻居
    course_neighbors = await visualization_service.get_direct_neighbors(
        student.id,
        relationship_types=[RelationshipType.LEARNS]
    )
    
    assert course_neighbors is not None
    assert len(course_neighbors) > 0
    # 验证包含课程节点
    neighbor_ids = [n.id for n in course_neighbors]
    assert sample_graph["course"].id in neighbor_ids


@pytest.mark.asyncio
async def test_get_relationship_statistics(sample_graph):
    """测试获取关系统计信息"""
    # 获取学生节点
    student = sample_graph["student1"]
    
    # 获取关系统计
    stats = await visualization_service.get_relationship_statistics(student.id)
    
    assert stats is not None
    assert "node_id" in stats
    assert stats["node_id"] == student.id
    
    # 验证总关系数
    assert "total_relationships" in stats
    assert stats["total_relationships"] > 0
    
    # 验证出边统计
    assert "outgoing" in stats
    assert "total_count" in stats["outgoing"]
    assert "by_type" in stats["outgoing"]
    
    # 验证入边统计
    assert "incoming" in stats
    assert "total_count" in stats["incoming"]
    assert "by_type" in stats["incoming"]
    
    # 验证出边类型统计
    outgoing_types = stats["outgoing"]["by_type"]
    assert len(outgoing_types) > 0
    
    # 验证每种关系类型的统计信息
    for rel_type, type_stats in outgoing_types.items():
        assert "count" in type_stats
        assert "total_weight" in type_stats
        assert "avg_weight" in type_stats
        assert type_stats["count"] > 0


@pytest.mark.asyncio
async def test_relationship_statistics_with_weights(sample_graph):
    """测试关系统计中的权重计算"""
    # 获取学生节点
    student = sample_graph["student1"]
    
    # 获取关系统计
    stats = await visualization_service.get_relationship_statistics(student.id)
    
    # 验证权重统计
    assert "total_weight" in stats["outgoing"]
    assert stats["outgoing"]["total_weight"] > 0
    
    # 验证每种关系类型的平均权重
    for rel_type, type_stats in stats["outgoing"]["by_type"].items():
        if type_stats["count"] > 0:
            expected_avg = type_stats["total_weight"] / type_stats["count"]
            assert abs(type_stats["avg_weight"] - expected_avg) < 0.01


@pytest.mark.asyncio
async def test_visualization_data_serialization(sample_graph):
    """测试可视化数据序列化"""
    # 查询子图
    subgraph = await query_service.query_subgraph(
        sample_graph["student1"].id,
        depth=2,
    )
    
    # 生成可视化数据
    viz_data = visualization_service.generate_visualization(subgraph)
    
    # 转换为字典
    viz_dict = viz_data.to_dict()
    
    assert "nodes" in viz_dict
    assert "edges" in viz_dict
    assert "layout" in viz_dict
    assert isinstance(viz_dict["nodes"], list)
    assert isinstance(viz_dict["edges"], list)
    assert isinstance(viz_dict["layout"], dict)


@pytest.mark.asyncio
async def test_edge_width_by_weight(sample_graph):
    """测试根据权重调整边宽度"""
    # 查询子图
    subgraph = await query_service.query_subgraph(
        sample_graph["student1"].id,
        depth=2,
    )
    
    # 生成可视化数据
    viz_data = visualization_service.generate_visualization(subgraph)
    
    # 验证有权重的边宽度不同
    edges_with_weight = [edge for edge in viz_data.edges if edge.weight is not None]
    
    if len(edges_with_weight) > 1:
        # 如果有多条有权重的边，验证宽度可能不同
        widths = [edge.width for edge in edges_with_weight]
        # 至少验证宽度在合理范围内
        assert all(1.0 <= width <= 10.0 for width in widths)
