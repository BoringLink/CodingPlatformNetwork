"""可视化服务单元测试（不需要数据库）"""

import pytest
from datetime import datetime

from app.services.visualization_service import (
    visualization_service,
    VisualizationOptions,
    VisualNode,
    VisualEdge,
)
from app.services.query_service import Subgraph, GraphFilter
from app.models.nodes import Node, NodeType
from app.models.relationships import Relationship, RelationshipType


def test_node_color_mapping():
    """测试节点类型到颜色的映射"""
    # 验证所有节点类型都有颜色映射
    for node_type in NodeType:
        assert node_type in visualization_service.NODE_COLORS
        color = visualization_service.NODE_COLORS[node_type]
        assert color.startswith("#")
        assert len(color) == 7  # #RRGGBB


def test_node_shape_mapping():
    """测试节点类型到形状的映射"""
    # 验证所有节点类型都有形状映射
    for node_type in NodeType:
        assert node_type in visualization_service.NODE_SHAPES
        shape = visualization_service.NODE_SHAPES[node_type]
        assert shape in ["ellipse", "triangle", "rectangle", "diamond", "hexagon"]


def test_edge_color_mapping():
    """测试关系类型到颜色的映射"""
    # 验证所有关系类型都有颜色映射
    for rel_type in RelationshipType:
        assert rel_type in visualization_service.EDGE_COLORS
        color = visualization_service.EDGE_COLORS[rel_type]
        assert color.startswith("#")
        assert len(color) == 7  # #RRGGBB


def test_unique_node_colors():
    """测试不同节点类型有不同的颜色"""
    colors = list(visualization_service.NODE_COLORS.values())
    # 至少应该有多种不同的颜色
    unique_colors = set(colors)
    assert len(unique_colors) > 1


def test_unique_node_shapes():
    """测试不同节点类型有不同的形状"""
    shapes = list(visualization_service.NODE_SHAPES.values())
    # 至少应该有多种不同的形状
    unique_shapes = set(shapes)
    assert len(unique_shapes) > 1


def test_node_to_visual():
    """测试节点转换为可视化节点"""
    # 创建测试节点
    node = Node(
        id="test-node-1",
        type=NodeType.STUDENT,
        properties={
            "student_id": "S001",
            "name": "张三",
            "grade": "3",
        },
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    
    options = VisualizationOptions(show_labels=True)
    
    # 转换为可视化节点
    visual_node = visualization_service._node_to_visual(node, options)
    
    # 验证
    assert visual_node.id == node.id
    assert visual_node.type == node.type
    assert visual_node.label == "张三"
    assert visual_node.color == visualization_service.NODE_COLORS[NodeType.STUDENT]
    assert visual_node.shape == visualization_service.NODE_SHAPES[NodeType.STUDENT]
    assert visual_node.size > 0


def test_node_to_visual_without_labels():
    """测试不显示标签时的节点转换"""
    node = Node(
        id="test-node-1",
        type=NodeType.STUDENT,
        properties={
            "student_id": "S001",
            "name": "张三",
        },
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    
    options = VisualizationOptions(show_labels=False)
    
    # 转换为可视化节点
    visual_node = visualization_service._node_to_visual(node, options)
    
    # 验证标签为空
    assert visual_node.label == ""


def test_get_node_label():
    """测试获取节点标签"""
    # 测试学生节点
    student = Node(
        id="s1",
        type=NodeType.STUDENT,
        properties={"name": "张三", "student_id": "S001"},
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    assert visualization_service._get_node_label(student) == "张三"
    
    # 测试教师节点
    teacher = Node(
        id="t1",
        type=NodeType.TEACHER,
        properties={"name": "王老师", "teacher_id": "T001"},
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    assert visualization_service._get_node_label(teacher) == "王老师"
    
    # 测试课程节点
    course = Node(
        id="c1",
        type=NodeType.COURSE,
        properties={"name": "高等数学", "course_id": "C001"},
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    assert visualization_service._get_node_label(course) == "高等数学"


def test_relationship_to_visual():
    """测试关系转换为可视化边"""
    # 创建测试关系
    relationship = Relationship(
        id="rel-1",
        type=RelationshipType.LEARNS,
        from_node_id="student-1",
        to_node_id="course-1",
        properties={
            "enrollment_date": datetime.utcnow().isoformat(),
            "progress": 75.0,
        },
        weight=1.5,
    )
    
    options = VisualizationOptions()
    
    # 转换为可视化边
    visual_edge = visualization_service._relationship_to_visual(relationship, options)
    
    # 验证
    assert visual_edge.id == relationship.id
    assert visual_edge.source == relationship.from_node_id
    assert visual_edge.target == relationship.to_node_id
    assert visual_edge.type == relationship.type
    assert visual_edge.color == visualization_service.EDGE_COLORS[RelationshipType.LEARNS]
    assert visual_edge.width > 0
    assert visual_edge.weight == 1.5


def test_calculate_edge_width_with_weight():
    """测试根据权重计算边宽度"""
    # 创建有权重的关系
    rel_light = Relationship(
        id="rel-1",
        type=RelationshipType.HAS_ERROR,
        from_node_id="s1",
        to_node_id="e1",
        properties={},
        weight=1.0,
    )
    
    rel_heavy = Relationship(
        id="rel-2",
        type=RelationshipType.HAS_ERROR,
        from_node_id="s1",
        to_node_id="e2",
        properties={},
        weight=10.0,
    )
    
    options = VisualizationOptions()
    
    width_light = visualization_service._calculate_edge_width(rel_light, options)
    width_heavy = visualization_service._calculate_edge_width(rel_heavy, options)
    
    # 权重大的边应该更宽
    assert width_heavy > width_light
    # 宽度应该在合理范围内
    assert 1.0 <= width_light <= 10.0
    assert 1.0 <= width_heavy <= 10.0


def test_create_layout_config():
    """测试创建布局配置"""
    # 测试力导向布局
    layout = visualization_service._create_layout_config("force-directed")
    assert layout.name == "cose"
    assert "idealEdgeLength" in layout.options
    
    # 测试层次布局
    layout = visualization_service._create_layout_config("hierarchical")
    assert layout.name == "breadthfirst"
    assert "directed" in layout.options
    
    # 测试圆形布局
    layout = visualization_service._create_layout_config("circular")
    assert layout.name == "circle"
    
    # 测试同心圆布局
    layout = visualization_service._create_layout_config("concentric")
    assert layout.name == "concentric"
    
    # 测试网格布局
    layout = visualization_service._create_layout_config("grid")
    assert layout.name == "grid"
    
    # 测试未知布局（应该返回默认的力导向布局）
    layout = visualization_service._create_layout_config("unknown")
    assert layout.name == "cose"


def test_generate_visualization():
    """测试生成可视化数据"""
    # 创建测试子图
    nodes = [
        Node(
            id="s1",
            type=NodeType.STUDENT,
            properties={"name": "张三", "student_id": "S001"},
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        ),
        Node(
            id="c1",
            type=NodeType.COURSE,
            properties={"name": "数学", "course_id": "C001"},
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        ),
    ]
    
    relationships = [
        Relationship(
            id="rel-1",
            type=RelationshipType.LEARNS,
            from_node_id="s1",
            to_node_id="c1",
            properties={"progress": 75.0},
            weight=None,
        ),
    ]
    
    subgraph = Subgraph(nodes=nodes, relationships=relationships)
    
    # 生成可视化数据
    viz_data = visualization_service.generate_visualization(subgraph)
    
    # 验证
    assert len(viz_data.nodes) == 2
    assert len(viz_data.edges) == 1
    assert viz_data.layout is not None
    
    # 验证节点
    assert all(node.id for node in viz_data.nodes)
    assert all(node.color for node in viz_data.nodes)
    assert all(node.shape for node in viz_data.nodes)
    
    # 验证边
    assert all(edge.source for edge in viz_data.edges)
    assert all(edge.target for edge in viz_data.edges)
    assert all(edge.color for edge in viz_data.edges)


def test_visualization_data_to_dict():
    """测试可视化数据序列化"""
    # 创建测试数据
    nodes = [
        Node(
            id="s1",
            type=NodeType.STUDENT,
            properties={"name": "张三"},
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        ),
    ]
    
    relationships = []
    
    subgraph = Subgraph(nodes=nodes, relationships=relationships)
    viz_data = visualization_service.generate_visualization(subgraph)
    
    # 转换为字典
    viz_dict = viz_data.to_dict()
    
    # 验证
    assert "nodes" in viz_dict
    assert "edges" in viz_dict
    assert "layout" in viz_dict
    assert isinstance(viz_dict["nodes"], list)
    assert isinstance(viz_dict["edges"], list)
    assert isinstance(viz_dict["layout"], dict)
    
    # 验证节点数据
    assert len(viz_dict["nodes"]) == 1
    node_dict = viz_dict["nodes"][0]
    assert "id" in node_dict
    assert "label" in node_dict
    assert "type" in node_dict
    assert "color" in node_dict
    assert "size" in node_dict
    assert "shape" in node_dict


@pytest.mark.asyncio
async def test_create_subview():
    """测试创建子视图"""
    # 创建测试子图
    nodes = [
        Node(
            id="s1",
            type=NodeType.STUDENT,
            properties={"name": "张三"},
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        ),
    ]
    
    subgraph = Subgraph(nodes=nodes, relationships=[])
    
    # 创建子视图
    filter = GraphFilter(node_types=[NodeType.STUDENT])
    subview = await visualization_service.create_subview(
        filter=filter,
        name="学生视图",
        subgraph=subgraph,
    )
    
    # 验证
    assert subview is not None
    assert subview.id is not None
    assert subview.name == "学生视图"
    assert subview.filter == filter
    assert subview.subgraph == subgraph
    assert subview.created_at is not None


@pytest.mark.asyncio
async def test_get_subview():
    """测试获取子视图"""
    # 创建子视图
    nodes = [
        Node(
            id="s1",
            type=NodeType.STUDENT,
            properties={"name": "张三"},
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        ),
    ]
    
    subgraph = Subgraph(nodes=nodes, relationships=[])
    filter = GraphFilter()
    
    subview = await visualization_service.create_subview(
        filter=filter,
        name="测试视图",
        subgraph=subgraph,
    )
    
    # 获取子视图
    retrieved = await visualization_service.get_subview(subview.id)
    
    # 验证
    assert retrieved is not None
    assert retrieved.id == subview.id
    assert retrieved.name == subview.name


@pytest.mark.asyncio
async def test_get_nonexistent_subview():
    """测试获取不存在的子视图"""
    result = await visualization_service.get_subview("nonexistent-id")
    assert result is None


@pytest.mark.asyncio
async def test_update_subview_filter():
    """测试更新子视图筛选条件"""
    # 创建子视图
    nodes = [
        Node(
            id="s1",
            type=NodeType.STUDENT,
            properties={"name": "张三"},
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        ),
    ]
    
    subgraph = Subgraph(nodes=nodes, relationships=[])
    filter = GraphFilter()
    
    subview = await visualization_service.create_subview(
        filter=filter,
        name="测试视图",
        subgraph=subgraph,
    )
    
    # 更新筛选条件
    new_filter = GraphFilter(node_types=[NodeType.STUDENT])
    new_subgraph = Subgraph(nodes=nodes[:1], relationships=[])
    
    updated = await visualization_service.update_subview_filter(
        subview.id,
        new_filter,
        new_subgraph,
    )
    
    # 验证
    assert updated is not None
    assert updated.filter == new_filter
    assert updated.subgraph == new_subgraph


@pytest.mark.asyncio
async def test_get_node_details():
    """测试获取节点详情"""
    # 创建测试节点
    node = Node(
        id="s1",
        type=NodeType.STUDENT,
        properties={"name": "张三", "student_id": "S001"},
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    
    # 创建测试关系
    relationships = [
        Relationship(
            id="rel-1",
            type=RelationshipType.LEARNS,
            from_node_id="s1",
            to_node_id="c1",
            properties={},
            weight=None,
        ),
        Relationship(
            id="rel-2",
            type=RelationshipType.LEARNS,
            from_node_id="s1",
            to_node_id="c2",
            properties={},
            weight=None,
        ),
        Relationship(
            id="rel-3",
            type=RelationshipType.HAS_ERROR,
            from_node_id="s1",
            to_node_id="e1",
            properties={},
            weight=2.0,
        ),
    ]
    
    # 获取节点详情
    details = await visualization_service.get_node_details(node, relationships)
    
    # 验证
    assert details is not None
    assert details.node.id == node.id
    assert len(details.relationship_counts) == 2
    assert details.relationship_counts[RelationshipType.LEARNS] == 2
    assert details.relationship_counts[RelationshipType.HAS_ERROR] == 1
    assert len(details.connected_nodes) == 2
