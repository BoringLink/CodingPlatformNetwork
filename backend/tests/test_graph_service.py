"""图谱服务集成测试"""

import pytest
from datetime import datetime

from app.database import init_database, close_database, neo4j_connection
from app.services.graph_service import graph_service
from app.models.nodes import NodeType


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


@pytest.mark.asyncio
async def test_create_student_node(setup_database):
    """测试创建学生节点"""
    properties = {
        "student_id": "S001",
        "name": "张三",
        "grade": "3",
        "enrollment_date": datetime(2023, 9, 1),
    }
    
    node = await graph_service.create_node(NodeType.STUDENT, properties)
    
    assert node.id is not None
    assert node.type == NodeType.STUDENT
    assert node.properties["student_id"] == "S001"
    assert node.properties["name"] == "张三"
    assert node.properties["grade"] == "3"


@pytest.mark.asyncio
async def test_create_duplicate_node_returns_existing(setup_database):
    """测试创建重复节点返回已存在的节点"""
    properties = {
        "student_id": "S002",
        "name": "李四",
    }
    
    # 第一次创建
    node1 = await graph_service.create_node(NodeType.STUDENT, properties)
    
    # 第二次创建相同的节点
    node2 = await graph_service.create_node(NodeType.STUDENT, properties)
    
    # 应该返回相同的节点
    assert node1.id == node2.id


@pytest.mark.asyncio
async def test_create_teacher_node(setup_database):
    """测试创建教师节点"""
    properties = {
        "teacher_id": "T001",
        "name": "王老师",
        "subject": "数学",
    }
    
    node = await graph_service.create_node(NodeType.TEACHER, properties)
    
    assert node.id is not None
    assert node.type == NodeType.TEACHER
    assert node.properties["teacher_id"] == "T001"
    assert node.properties["name"] == "王老师"


@pytest.mark.asyncio
async def test_create_course_node(setup_database):
    """测试创建课程节点"""
    properties = {
        "course_id": "C001",
        "name": "高等数学",
        "description": "大学数学基础课程",
        "difficulty": "intermediate",
    }
    
    node = await graph_service.create_node(NodeType.COURSE, properties)
    
    assert node.id is not None
    assert node.type == NodeType.COURSE
    assert node.properties["course_id"] == "C001"
    assert node.properties["difficulty"] == "intermediate"


@pytest.mark.asyncio
async def test_create_knowledge_point_node(setup_database):
    """测试创建知识点节点"""
    properties = {
        "knowledge_point_id": "KP001",
        "name": "微积分基础",
        "description": "微积分的基本概念和定理",
        "category": "数学",
    }
    
    node = await graph_service.create_node(NodeType.KNOWLEDGE_POINT, properties)
    
    assert node.id is not None
    assert node.type == NodeType.KNOWLEDGE_POINT
    assert node.properties["knowledge_point_id"] == "KP001"


@pytest.mark.asyncio
async def test_create_error_type_node(setup_database):
    """测试创建错误类型节点"""
    properties = {
        "error_type_id": "E001",
        "name": "概念理解错误",
        "description": "对基本概念理解不正确",
        "severity": "medium",
    }
    
    node = await graph_service.create_node(NodeType.ERROR_TYPE, properties)
    
    assert node.id is not None
    assert node.type == NodeType.ERROR_TYPE
    assert node.properties["error_type_id"] == "E001"
    assert node.properties["severity"] == "medium"


@pytest.mark.asyncio
async def test_merge_nodes(setup_database):
    """测试合并节点"""
    # 创建两个学生节点
    properties1 = {
        "student_id": "S003",
        "name": "赵六",
        "grade": "2",
    }
    node1 = await graph_service.create_node(NodeType.STUDENT, properties1)
    
    # 手动创建第二个节点（绕过唯一性检查）
    async with neo4j_connection.get_session() as session:
        result = await session.run(
            """
            CREATE (n:Student {
                student_id: 'S003_dup',
                name: '赵六',
                grade: '3',
                id: randomUUID()
            })
            RETURN n.id as id
            """
        )
        record = await result.single()
        node2_id = record["id"]
    
    # 合并节点
    merged_node = await graph_service.merge_nodes([node1.id, node2_id])
    
    assert merged_node.id == node1.id
    assert merged_node.properties["name"] == "赵六"
    
    # 验证第二个节点已被删除
    async with neo4j_connection.get_session() as session:
        result = await session.run(
            "MATCH (n) WHERE n.id = $node_id RETURN n",
            node_id=node2_id
        )
        record = await result.single()
        assert record is None


@pytest.mark.asyncio
async def test_update_node(setup_database):
    """测试更新节点"""
    # 创建节点
    properties = {
        "student_id": "S004",
        "name": "孙七",
        "grade": "1",
    }
    node = await graph_service.create_node(NodeType.STUDENT, properties)
    
    # 更新节点
    updated_node = await graph_service.update_node(
        node.id,
        {"grade": "2", "metadata": {"updated": True}}
    )
    
    assert updated_node.id == node.id
    assert updated_node.properties["grade"] == "2"
    assert updated_node.properties["metadata"]["updated"] is True


# ==================== 关系管理测试 ====================

@pytest.mark.asyncio
async def test_create_chat_with_relationship(setup_database):
    """测试创建聊天互动关系"""
    from app.models.relationships import RelationshipType
    
    # 创建两个学生节点
    student1 = await graph_service.create_node(
        NodeType.STUDENT,
        {"student_id": "S101", "name": "学生A"}
    )
    student2 = await graph_service.create_node(
        NodeType.STUDENT,
        {"student_id": "S102", "name": "学生B"}
    )
    
    # 创建聊天关系
    relationship = await graph_service.create_relationship(
        student1.id,
        student2.id,
        RelationshipType.CHAT_WITH,
        {
            "message_count": 5,
            "last_interaction_date": datetime(2024, 1, 15),
            "topics": ["数学", "作业"],
        }
    )
    
    assert relationship.id is not None
    assert relationship.type == RelationshipType.CHAT_WITH
    assert relationship.from_node_id == student1.id
    assert relationship.to_node_id == student2.id
    assert relationship.properties["message_count"] == 5
    assert relationship.weight == 5.0  # 权重基于消息数量


@pytest.mark.asyncio
async def test_create_likes_relationship(setup_database):
    """测试创建点赞互动关系"""
    from app.models.relationships import RelationshipType
    
    # 创建两个学生节点
    student1 = await graph_service.create_node(
        NodeType.STUDENT,
        {"student_id": "S103", "name": "学生C"}
    )
    student2 = await graph_service.create_node(
        NodeType.STUDENT,
        {"student_id": "S104", "name": "学生D"}
    )
    
    # 创建点赞关系
    relationship = await graph_service.create_relationship(
        student1.id,
        student2.id,
        RelationshipType.LIKES,
        {
            "like_count": 3,
            "last_like_date": datetime(2024, 1, 20),
        }
    )
    
    assert relationship.type == RelationshipType.LIKES
    assert relationship.properties["like_count"] == 3
    assert relationship.weight == 3.0  # 权重基于点赞数量


@pytest.mark.asyncio
async def test_create_teaches_relationship(setup_database):
    """测试创建教学互动关系"""
    from app.models.relationships import RelationshipType
    
    # 创建教师和学生节点
    teacher = await graph_service.create_node(
        NodeType.TEACHER,
        {"teacher_id": "T101", "name": "李老师", "subject": "物理"}
    )
    student = await graph_service.create_node(
        NodeType.STUDENT,
        {"student_id": "S105", "name": "学生E"}
    )
    
    # 创建教学关系
    relationship = await graph_service.create_relationship(
        teacher.id,
        student.id,
        RelationshipType.TEACHES,
        {
            "interaction_count": 10,
            "last_interaction_date": datetime(2024, 1, 25),
            "feedback": "学习态度认真",
        }
    )
    
    assert relationship.type == RelationshipType.TEACHES
    assert relationship.properties["interaction_count"] == 10
    assert relationship.properties["feedback"] == "学习态度认真"
    assert relationship.weight == 10.0  # 权重基于互动次数


@pytest.mark.asyncio
async def test_create_learns_relationship(setup_database):
    """测试创建学习关系"""
    from app.models.relationships import RelationshipType
    
    # 创建学生和课程节点
    student = await graph_service.create_node(
        NodeType.STUDENT,
        {"student_id": "S106", "name": "学生F"}
    )
    course = await graph_service.create_node(
        NodeType.COURSE,
        {"course_id": "C101", "name": "线性代数", "difficulty": "intermediate"}
    )
    
    # 创建学习关系
    relationship = await graph_service.create_relationship(
        student.id,
        course.id,
        RelationshipType.LEARNS,
        {
            "enrollment_date": datetime(2024, 1, 1),
            "progress": 65.5,
            "time_spent": 120,
        }
    )
    
    assert relationship.type == RelationshipType.LEARNS
    assert relationship.properties["progress"] == 65.5
    assert relationship.properties["time_spent"] == 120
    assert relationship.weight == 65.5  # 权重基于学习进度


@pytest.mark.asyncio
async def test_create_contains_relationship(setup_database):
    """测试创建包含关系"""
    from app.models.relationships import RelationshipType
    
    # 创建课程和知识点节点
    course = await graph_service.create_node(
        NodeType.COURSE,
        {"course_id": "C102", "name": "概率论"}
    )
    knowledge_point = await graph_service.create_node(
        NodeType.KNOWLEDGE_POINT,
        {
            "knowledge_point_id": "KP101",
            "name": "贝叶斯定理",
            "description": "条件概率的重要定理",
        }
    )
    
    # 创建包含关系
    relationship = await graph_service.create_relationship(
        course.id,
        knowledge_point.id,
        RelationshipType.CONTAINS,
        {
            "order": 1,
            "importance": "core",
        }
    )
    
    assert relationship.type == RelationshipType.CONTAINS
    assert relationship.properties["order"] == 1
    assert relationship.properties["importance"] == "core"
    assert relationship.weight == 1.0  # 核心知识点权重为 1.0


@pytest.mark.asyncio
async def test_create_has_error_relationship(setup_database):
    """测试创建错误关系"""
    from app.models.relationships import RelationshipType
    
    # 创建学生和错误类型节点
    student = await graph_service.create_node(
        NodeType.STUDENT,
        {"student_id": "S107", "name": "学生G"}
    )
    error_type = await graph_service.create_node(
        NodeType.ERROR_TYPE,
        {
            "error_type_id": "E101",
            "name": "计算错误",
            "description": "计算过程中的错误",
            "severity": "medium",
        }
    )
    
    # 创建错误关系
    relationship = await graph_service.create_relationship(
        student.id,
        error_type.id,
        RelationshipType.HAS_ERROR,
        {
            "occurrence_count": 3,
            "first_occurrence": datetime(2024, 1, 10),
            "last_occurrence": datetime(2024, 1, 30),
            "course_id": "C101",
            "resolved": False,
        }
    )
    
    assert relationship.type == RelationshipType.HAS_ERROR
    assert relationship.properties["occurrence_count"] == 3
    assert relationship.properties["course_id"] == "C101"
    assert relationship.properties["resolved"] is False
    assert relationship.weight == 3.0  # 权重基于发生次数


@pytest.mark.asyncio
async def test_create_relates_to_relationship(setup_database):
    """测试创建关联关系"""
    from app.models.relationships import RelationshipType
    
    # 创建错误类型和知识点节点
    error_type = await graph_service.create_node(
        NodeType.ERROR_TYPE,
        {
            "error_type_id": "E102",
            "name": "概念混淆",
            "description": "对概念理解不清",
        }
    )
    knowledge_point = await graph_service.create_node(
        NodeType.KNOWLEDGE_POINT,
        {
            "knowledge_point_id": "KP102",
            "name": "导数定义",
            "description": "导数的基本定义",
        }
    )
    
    # 创建关联关系
    relationship = await graph_service.create_relationship(
        error_type.id,
        knowledge_point.id,
        RelationshipType.RELATES_TO,
        {
            "strength": 0.85,
            "confidence": 0.92,
        }
    )
    
    assert relationship.type == RelationshipType.RELATES_TO
    assert relationship.properties["strength"] == 0.85
    assert relationship.properties["confidence"] == 0.92
    assert relationship.weight == 0.85  # 权重基于关联强度


@pytest.mark.asyncio
async def test_update_relationship(setup_database):
    """测试更新关系属性"""
    from app.models.relationships import RelationshipType
    
    # 创建节点和关系
    student1 = await graph_service.create_node(
        NodeType.STUDENT,
        {"student_id": "S108", "name": "学生H"}
    )
    student2 = await graph_service.create_node(
        NodeType.STUDENT,
        {"student_id": "S109", "name": "学生I"}
    )
    
    relationship = await graph_service.create_relationship(
        student1.id,
        student2.id,
        RelationshipType.CHAT_WITH,
        {
            "message_count": 5,
            "last_interaction_date": datetime(2024, 1, 15),
        }
    )
    
    # 更新关系
    updated_relationship = await graph_service.update_relationship(
        relationship.id,
        {
            "message_count": 10,
            "last_interaction_date": datetime(2024, 2, 1),
        }
    )
    
    assert updated_relationship.id == relationship.id
    assert updated_relationship.properties["message_count"] == 10


@pytest.mark.asyncio
async def test_increment_relationship_weight(setup_database):
    """测试增加关系权重"""
    from app.models.relationships import RelationshipType
    
    # 创建节点和关系
    student = await graph_service.create_node(
        NodeType.STUDENT,
        {"student_id": "S110", "name": "学生J"}
    )
    error_type = await graph_service.create_node(
        NodeType.ERROR_TYPE,
        {
            "error_type_id": "E103",
            "name": "公式应用错误",
            "description": "公式使用不当",
        }
    )
    
    relationship = await graph_service.create_relationship(
        student.id,
        error_type.id,
        RelationshipType.HAS_ERROR,
        {
            "occurrence_count": 2,
            "first_occurrence": datetime(2024, 1, 10),
            "last_occurrence": datetime(2024, 1, 20),
            "course_id": "C101",
            "resolved": False,
        }
    )
    
    # 初始权重应该是 2.0
    assert relationship.weight == 2.0
    
    # 增加权重
    updated_relationship = await graph_service.increment_relationship_weight(
        student.id,
        error_type.id,
        RelationshipType.HAS_ERROR,
        increment=1.0,
    )
    
    # 权重应该增加到 3.0
    assert updated_relationship.weight == 3.0


@pytest.mark.asyncio
async def test_relationship_property_validation_failure(setup_database):
    """测试关系属性验证失败"""
    from app.models.relationships import RelationshipType
    
    # 创建节点
    student1 = await graph_service.create_node(
        NodeType.STUDENT,
        {"student_id": "S111", "name": "学生K"}
    )
    student2 = await graph_service.create_node(
        NodeType.STUDENT,
        {"student_id": "S112", "name": "学生L"}
    )
    
    # 尝试创建带有无效属性的关系
    with pytest.raises(ValueError) as exc_info:
        await graph_service.create_relationship(
            student1.id,
            student2.id,
            RelationshipType.CHAT_WITH,
            {
                "message_count": -5,  # 无效：负数
                "last_interaction_date": datetime(2024, 1, 15),
            }
        )
    
    assert "validation failed" in str(exc_info.value).lower()


@pytest.mark.asyncio
async def test_create_relationship_with_nonexistent_nodes(setup_database):
    """测试创建关系时节点不存在"""
    from app.models.relationships import RelationshipType
    
    # 尝试创建关系，但节点不存在
    with pytest.raises((ValueError, RuntimeError)) as exc_info:
        await graph_service.create_relationship(
            "nonexistent-node-1",
            "nonexistent-node-2",
            RelationshipType.CHAT_WITH,
            {
                "message_count": 5,
                "last_interaction_date": datetime(2024, 1, 15),
            }
        )
    
    assert "not exist" in str(exc_info.value).lower() or "failed" in str(exc_info.value).lower()


# ==================== 多课程多错误处理测试 ====================

@pytest.mark.asyncio
async def test_create_student_multi_course_error(setup_database):
    """测试创建学生多课程错误记录"""
    from app.models.relationships import RelationshipType
    
    # 创建学生、错误类型和知识点节点
    student = await graph_service.create_node(
        NodeType.STUDENT,
        {"student_id": "S201", "name": "学生多课程"}
    )
    error_type = await graph_service.create_node(
        NodeType.ERROR_TYPE,
        {
            "error_type_id": "E201",
            "name": "多课程错误",
            "description": "跨课程的错误类型",
        }
    )
    kp1 = await graph_service.create_node(
        NodeType.KNOWLEDGE_POINT,
        {
            "knowledge_point_id": "KP201",
            "name": "知识点1",
            "description": "测试知识点1",
        }
    )
    kp2 = await graph_service.create_node(
        NodeType.KNOWLEDGE_POINT,
        {
            "knowledge_point_id": "KP202",
            "name": "知识点2",
            "description": "测试知识点2",
        }
    )
    
    # 创建第一个课程的错误记录
    result1 = await graph_service.create_student_multi_course_error(
        student_id="S201",
        error_type_id="E201",
        course_id="C201",
        occurrence_time=datetime(2024, 1, 10),
        knowledge_point_ids=["KP201", "KP202"],
    )
    
    assert result1["is_new"] is True
    assert result1["relationship"].type == RelationshipType.HAS_ERROR
    assert result1["relationship"].properties["course_id"] == "C201"
    assert result1["relationship"].properties["occurrence_count"] == 1
    assert len(result1["relates_to_relationships"]) == 2
    
    # 创建第二个课程的错误记录（同一学生，同一错误类型，不同课程）
    result2 = await graph_service.create_student_multi_course_error(
        student_id="S201",
        error_type_id="E201",
        course_id="C202",
        occurrence_time=datetime(2024, 1, 15),
        knowledge_point_ids=["KP201"],
    )
    
    assert result2["is_new"] is True
    assert result2["relationship"].properties["course_id"] == "C202"
    assert result2["relationship"].properties["occurrence_count"] == 1
    
    # 验证创建了两个独立的 HAS_ERROR 关系
    async with neo4j_connection.get_session() as session:
        result = await session.run(
            """
            MATCH (s:Student {student_id: $student_id})-[r:HAS_ERROR]->(e:ErrorType {error_type_id: $error_type_id})
            RETURN count(r) as count
            """,
            student_id="S201",
            error_type_id="E201",
        )
        record = await result.single()
        assert record["count"] == 2


@pytest.mark.asyncio
async def test_create_student_multi_course_error_repeated(setup_database):
    """测试重复创建同一课程的错误记录会更新而不是创建新记录"""
    # 创建学生和错误类型节点
    student = await graph_service.create_node(
        NodeType.STUDENT,
        {"student_id": "S202", "name": "学生重复错误"}
    )
    error_type = await graph_service.create_node(
        NodeType.ERROR_TYPE,
        {
            "error_type_id": "E202",
            "name": "重复错误",
            "description": "会重复发生的错误",
        }
    )
    
    # 第一次创建错误记录
    result1 = await graph_service.create_student_multi_course_error(
        student_id="S202",
        error_type_id="E202",
        course_id="C203",
        occurrence_time=datetime(2024, 1, 10),
    )
    
    assert result1["is_new"] is True
    assert result1["relationship"].properties["occurrence_count"] == 1
    assert result1["relationship"].weight == 1.0
    
    # 第二次创建相同的错误记录（同一学生、同一错误类型、同一课程）
    result2 = await graph_service.create_student_multi_course_error(
        student_id="S202",
        error_type_id="E202",
        course_id="C203",
        occurrence_time=datetime(2024, 1, 20),
    )
    
    assert result2["is_new"] is False
    assert result2["relationship"].properties["occurrence_count"] == 2
    assert result2["relationship"].weight == 2.0
    
    # 验证只有一个 HAS_ERROR 关系
    async with neo4j_connection.get_session() as session:
        result = await session.run(
            """
            MATCH (s:Student {student_id: $student_id})-[r:HAS_ERROR]->(e:ErrorType {error_type_id: $error_type_id})
            WHERE r.course_id = $course_id
            RETURN count(r) as count
            """,
            student_id="S202",
            error_type_id="E202",
            course_id="C203",
        )
        record = await result.single()
        assert record["count"] == 1


@pytest.mark.asyncio
async def test_associate_error_with_knowledge_points(setup_database):
    """测试将错误类型关联到多个知识点"""
    from app.models.relationships import RelationshipType
    
    # 创建错误类型和知识点节点
    error_type = await graph_service.create_node(
        NodeType.ERROR_TYPE,
        {
            "error_type_id": "E203",
            "name": "多知识点错误",
            "description": "涉及多个知识点的错误",
        }
    )
    kp1 = await graph_service.create_node(
        NodeType.KNOWLEDGE_POINT,
        {
            "knowledge_point_id": "KP203",
            "name": "知识点A",
            "description": "测试知识点A",
        }
    )
    kp2 = await graph_service.create_node(
        NodeType.KNOWLEDGE_POINT,
        {
            "knowledge_point_id": "KP204",
            "name": "知识点B",
            "description": "测试知识点B",
        }
    )
    kp3 = await graph_service.create_node(
        NodeType.KNOWLEDGE_POINT,
        {
            "knowledge_point_id": "KP205",
            "name": "知识点C",
            "description": "测试知识点C",
        }
    )
    
    # 关联错误类型到多个知识点
    relationships = await graph_service.associate_error_with_knowledge_points(
        error_type_id="E203",
        knowledge_point_ids=["KP203", "KP204", "KP205"],
        strength=0.9,
        confidence=0.95,
    )
    
    assert len(relationships) == 3
    for rel in relationships:
        assert rel.type == RelationshipType.RELATES_TO
        assert rel.properties["strength"] == 0.9
        assert rel.properties["confidence"] == 0.95
    
    # 验证关系已创建
    async with neo4j_connection.get_session() as session:
        result = await session.run(
            """
            MATCH (e:ErrorType {error_type_id: $error_type_id})-[r:RELATES_TO]->(k:KnowledgePoint)
            RETURN count(r) as count
            """,
            error_type_id="E203",
        )
        record = await result.single()
        assert record["count"] == 3


@pytest.mark.asyncio
async def test_aggregate_student_errors(setup_database):
    """测试聚合学生的所有错误关系"""
    # 创建学生、错误类型和知识点节点
    student = await graph_service.create_node(
        NodeType.STUDENT,
        {"student_id": "S203", "name": "学生聚合测试"}
    )
    error_type1 = await graph_service.create_node(
        NodeType.ERROR_TYPE,
        {
            "error_type_id": "E204",
            "name": "错误类型1",
            "description": "第一种错误",
        }
    )
    error_type2 = await graph_service.create_node(
        NodeType.ERROR_TYPE,
        {
            "error_type_id": "E205",
            "name": "错误类型2",
            "description": "第二种错误",
        }
    )
    kp1 = await graph_service.create_node(
        NodeType.KNOWLEDGE_POINT,
        {
            "knowledge_point_id": "KP206",
            "name": "知识点X",
            "description": "测试知识点X",
        }
    )
    kp2 = await graph_service.create_node(
        NodeType.KNOWLEDGE_POINT,
        {
            "knowledge_point_id": "KP207",
            "name": "知识点Y",
            "description": "测试知识点Y",
        }
    )
    
    # 创建多个错误记录
    await graph_service.create_student_multi_course_error(
        student_id="S203",
        error_type_id="E204",
        course_id="C204",
        occurrence_time=datetime(2024, 1, 10),
        knowledge_point_ids=["KP206"],
    )
    
    await graph_service.create_student_multi_course_error(
        student_id="S203",
        error_type_id="E204",
        course_id="C205",
        occurrence_time=datetime(2024, 1, 15),
        knowledge_point_ids=["KP206", "KP207"],
    )
    
    await graph_service.create_student_multi_course_error(
        student_id="S203",
        error_type_id="E205",
        course_id="C204",
        occurrence_time=datetime(2024, 1, 20),
        knowledge_point_ids=["KP207"],
    )
    
    # 聚合错误统计
    stats = await graph_service.aggregate_student_errors("S203")
    
    assert stats["student_id"] == "S203"
    assert stats["total_errors"] == 3
    assert len(stats["errors_by_course"]) == 2
    assert "C204" in stats["errors_by_course"]
    assert "C205" in stats["errors_by_course"]
    assert stats["errors_by_course"]["C204"]["count"] == 2
    assert stats["errors_by_course"]["C205"]["count"] == 1
    
    assert len(stats["errors_by_knowledge_point"]) == 2
    assert "KP206" in stats["errors_by_knowledge_point"]
    assert "KP207" in stats["errors_by_knowledge_point"]
    
    assert len(stats["errors_by_type"]) == 2
    assert "E204" in stats["errors_by_type"]
    assert "E205" in stats["errors_by_type"]
    assert stats["errors_by_type"]["E204"]["count"] == 2
    
    assert len(stats["error_details"]) == 3


@pytest.mark.asyncio
async def test_find_cross_course_knowledge_point_paths(setup_database):
    """测试查询跨课程的知识点路径"""
    # 创建课程和知识点节点
    course1 = await graph_service.create_node(
        NodeType.COURSE,
        {"course_id": "C206", "name": "课程A"}
    )
    course2 = await graph_service.create_node(
        NodeType.COURSE,
        {"course_id": "C207", "name": "课程B"}
    )
    kp_shared = await graph_service.create_node(
        NodeType.KNOWLEDGE_POINT,
        {
            "knowledge_point_id": "KP208",
            "name": "共享知识点",
            "description": "两个课程共享的知识点",
        }
    )
    
    # 创建 CONTAINS 关系
    from app.models.relationships import RelationshipType
    await graph_service.create_relationship(
        course1.id,
        kp_shared.id,
        RelationshipType.CONTAINS,
        {"importance": "core"},
    )
    await graph_service.create_relationship(
        course2.id,
        kp_shared.id,
        RelationshipType.CONTAINS,
        {"importance": "core"},
    )
    
    # 查询跨课程路径
    paths = await graph_service.find_cross_course_knowledge_point_paths(
        course_id_1="C206",
        course_id_2="C207",
    )
    
    assert len(paths) > 0
    assert paths[0]["knowledge_point_id"] == "KP208"
    assert paths[0]["knowledge_point_name"] == "共享知识点"
    assert len(paths[0]["nodes"]) >= 3  # 至少包含两个课程和一个知识点


@pytest.mark.asyncio
async def test_update_repeated_error_weight(setup_database):
    """测试更新重复错误的权重"""
    from app.models.relationships import RelationshipType
    
    # 创建学生和错误类型节点
    student = await graph_service.create_node(
        NodeType.STUDENT,
        {"student_id": "S204", "name": "学生权重测试"}
    )
    error_type = await graph_service.create_node(
        NodeType.ERROR_TYPE,
        {
            "error_type_id": "E206",
            "name": "权重测试错误",
            "description": "用于测试权重更新",
        }
    )
    
    # 创建初始错误记录
    await graph_service.create_student_multi_course_error(
        student_id="S204",
        error_type_id="E206",
        course_id="C208",
        occurrence_time=datetime(2024, 1, 10),
    )
    
    # 更新重复错误权重
    updated_rel = await graph_service.update_repeated_error_weight(
        student_id="S204",
        error_type_id="E206",
        course_id="C208",
    )
    
    assert updated_rel.type == RelationshipType.HAS_ERROR
    assert updated_rel.properties["occurrence_count"] == 2
    assert updated_rel.weight == 2.0
    
    # 再次更新
    updated_rel2 = await graph_service.update_repeated_error_weight(
        student_id="S204",
        error_type_id="E206",
        course_id="C208",
    )
    
    assert updated_rel2.properties["occurrence_count"] == 3
    assert updated_rel2.weight == 3.0


@pytest.mark.asyncio
async def test_aggregate_student_errors_no_errors(setup_database):
    """测试聚合没有错误的学生"""
    # 创建一个没有错误的学生
    student = await graph_service.create_node(
        NodeType.STUDENT,
        {"student_id": "S205", "name": "无错误学生"}
    )
    
    # 聚合错误统计
    stats = await graph_service.aggregate_student_errors("S205")
    
    assert stats["student_id"] == "S205"
    assert stats["total_errors"] == 0
    assert len(stats["errors_by_course"]) == 0
    assert len(stats["errors_by_knowledge_point"]) == 0
    assert len(stats["errors_by_type"]) == 0
    assert len(stats["error_details"]) == 0


@pytest.mark.asyncio
async def test_find_cross_course_knowledge_point_paths_no_shared(setup_database):
    """测试查询没有共享知识点的跨课程路径"""
    # 创建两个没有共享知识点的课程
    course1 = await graph_service.create_node(
        NodeType.COURSE,
        {"course_id": "C209", "name": "独立课程A"}
    )
    course2 = await graph_service.create_node(
        NodeType.COURSE,
        {"course_id": "C210", "name": "独立课程B"}
    )
    
    # 查询跨课程路径
    paths = await graph_service.find_cross_course_knowledge_point_paths(
        course_id_1="C209",
        course_id_2="C210",
    )
    
    assert len(paths) == 0
