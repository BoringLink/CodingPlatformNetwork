"""增量更新和事务支持测试"""

import pytest
from datetime import datetime

from app.database import init_database, close_database, neo4j_connection
from app.services.graph_service import (
    graph_service,
    ConflictResolutionStrategy,
    CreateNodeOperation,
    UpdateNodeOperation,
    CreateRelationshipOperation,
    UpdateRelationshipOperation,
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


# ==================== 增量更新测试 ====================

@pytest.mark.asyncio
async def test_upsert_node_creates_new_node(setup_database):
    """测试 upsert 节点：节点不存在时创建新节点"""
    properties = {
        "student_id": "S001",
        "name": "张三",
        "grade": "3",
    }
    
    node = await graph_service.upsert_node(
        node_type=NodeType.STUDENT,
        unique_field="student_id",
        unique_value="S001",
        properties=properties,
    )
    
    assert node.id is not None
    assert node.type == NodeType.STUDENT
    assert node.properties["student_id"] == "S001"
    assert node.properties["name"] == "张三"


@pytest.mark.asyncio
async def test_upsert_node_updates_existing_with_timestamp_priority(setup_database):
    """测试 upsert 节点：节点存在时使用时间戳优先策略更新"""
    # 创建初始节点
    initial_properties = {
        "student_id": "S002",
        "name": "李四",
        "grade": "2",
    }
    initial_node = await graph_service.create_node(NodeType.STUDENT, initial_properties)
    
    # 等待一小段时间确保时间戳不同
    import asyncio
    await asyncio.sleep(0.1)
    
    # 使用 upsert 更新节点（带有更新时间戳）
    updated_properties = {
        "student_id": "S002",
        "name": "李四",
        "grade": "3",
        "updated_at": datetime.utcnow().isoformat(),
    }
    
    updated_node = await graph_service.upsert_node(
        node_type=NodeType.STUDENT,
        unique_field="student_id",
        unique_value="S002",
        properties=updated_properties,
        conflict_strategy=ConflictResolutionStrategy.TIMESTAMP_PRIORITY,
    )
    
    assert updated_node.id == initial_node.id
    assert updated_node.properties["grade"] == "3"


@pytest.mark.asyncio
async def test_upsert_node_keeps_existing_with_keep_existing_strategy(setup_database):
    """测试 upsert 节点：使用保留现有数据策略"""
    # 创建初始节点
    initial_properties = {
        "student_id": "S003",
        "name": "王五",
        "grade": "1",
    }
    initial_node = await graph_service.create_node(NodeType.STUDENT, initial_properties)
    
    # 尝试 upsert 但保留现有数据
    new_properties = {
        "student_id": "S003",
        "name": "王五",
        "grade": "5",
    }
    
    result_node = await graph_service.upsert_node(
        node_type=NodeType.STUDENT,
        unique_field="student_id",
        unique_value="S003",
        properties=new_properties,
        conflict_strategy=ConflictResolutionStrategy.KEEP_EXISTING,
    )
    
    assert result_node.id == initial_node.id
    assert result_node.properties["grade"] == "1"  # 保持原有值


@pytest.mark.asyncio
async def test_upsert_node_merges_properties(setup_database):
    """测试 upsert 节点：使用合并属性策略"""
    # 创建初始节点
    initial_properties = {
        "student_id": "S004",
        "name": "赵六",
        "grade": "2",
    }
    initial_node = await graph_service.create_node(NodeType.STUDENT, initial_properties)
    
    # 使用合并策略 upsert
    new_properties = {
        "student_id": "S004",
        "grade": "3",
        "metadata": {"updated": True},
    }
    
    merged_node = await graph_service.upsert_node(
        node_type=NodeType.STUDENT,
        unique_field="student_id",
        unique_value="S004",
        properties=new_properties,
        conflict_strategy=ConflictResolutionStrategy.MERGE_PROPERTIES,
    )
    
    assert merged_node.id == initial_node.id
    assert merged_node.properties["name"] == "赵六"  # 保留原有属性
    assert merged_node.properties["grade"] == "3"  # 更新新属性
    assert merged_node.properties["metadata"]["updated"] is True  # 添加新属性


@pytest.mark.asyncio
async def test_upsert_relationship_creates_new_relationship(setup_database):
    """测试 upsert 关系：关系不存在时创建新关系"""
    # 创建两个学生节点
    student1 = await graph_service.create_node(
        NodeType.STUDENT,
        {"student_id": "S101", "name": "学生A"}
    )
    student2 = await graph_service.create_node(
        NodeType.STUDENT,
        {"student_id": "S102", "name": "学生B"}
    )
    
    # Upsert 关系
    relationship = await graph_service.upsert_relationship(
        from_node_id=student1.id,
        to_node_id=student2.id,
        relationship_type=RelationshipType.CHAT_WITH,
        properties={
            "message_count": 5,
            "last_interaction_date": datetime(2024, 1, 15),
        },
    )
    
    assert relationship.id is not None
    assert relationship.type == RelationshipType.CHAT_WITH
    assert relationship.properties["message_count"] == 5


@pytest.mark.asyncio
async def test_upsert_relationship_updates_existing(setup_database):
    """测试 upsert 关系：关系存在时更新"""
    # 创建两个学生节点
    student1 = await graph_service.create_node(
        NodeType.STUDENT,
        {"student_id": "S103", "name": "学生C"}
    )
    student2 = await graph_service.create_node(
        NodeType.STUDENT,
        {"student_id": "S104", "name": "学生D"}
    )
    
    # 创建初始关系
    initial_rel = await graph_service.create_relationship(
        student1.id,
        student2.id,
        RelationshipType.CHAT_WITH,
        {
            "message_count": 5,
            "last_interaction_date": datetime(2024, 1, 15),
        }
    )
    
    # Upsert 更新关系
    updated_rel = await graph_service.upsert_relationship(
        from_node_id=student1.id,
        to_node_id=student2.id,
        relationship_type=RelationshipType.CHAT_WITH,
        properties={
            "message_count": 10,
            "last_interaction_date": datetime(2024, 2, 1),
        },
    )
    
    assert updated_rel.id == initial_rel.id
    assert updated_rel.properties["message_count"] == 10


@pytest.mark.asyncio
async def test_upsert_relationship_keeps_existing(setup_database):
    """测试 upsert 关系：使用保留现有数据策略"""
    # 创建两个学生节点
    student1 = await graph_service.create_node(
        NodeType.STUDENT,
        {"student_id": "S105", "name": "学生E"}
    )
    student2 = await graph_service.create_node(
        NodeType.STUDENT,
        {"student_id": "S106", "name": "学生F"}
    )
    
    # 创建初始关系
    initial_rel = await graph_service.create_relationship(
        student1.id,
        student2.id,
        RelationshipType.CHAT_WITH,
        {
            "message_count": 5,
            "last_interaction_date": datetime(2024, 1, 15),
        }
    )
    
    # Upsert 但保留现有数据
    result_rel = await graph_service.upsert_relationship(
        from_node_id=student1.id,
        to_node_id=student2.id,
        relationship_type=RelationshipType.CHAT_WITH,
        properties={
            "message_count": 100,
            "last_interaction_date": datetime(2024, 2, 1),
        },
        conflict_strategy=ConflictResolutionStrategy.KEEP_EXISTING,
    )
    
    assert result_rel.id == initial_rel.id
    assert result_rel.properties["message_count"] == 5  # 保持原有值


@pytest.mark.asyncio
async def test_upsert_relationship_merges_properties(setup_database):
    """测试 upsert 关系：使用合并属性策略"""
    # 创建两个学生节点
    student1 = await graph_service.create_node(
        NodeType.STUDENT,
        {"student_id": "S107", "name": "学生G"}
    )
    student2 = await graph_service.create_node(
        NodeType.STUDENT,
        {"student_id": "S108", "name": "学生H"}
    )
    
    # 创建初始关系
    initial_rel = await graph_service.create_relationship(
        student1.id,
        student2.id,
        RelationshipType.CHAT_WITH,
        {
            "message_count": 5,
            "last_interaction_date": datetime(2024, 1, 15),
            "topics": ["数学"],
        }
    )
    
    # Upsert 合并属性
    merged_rel = await graph_service.upsert_relationship(
        from_node_id=student1.id,
        to_node_id=student2.id,
        relationship_type=RelationshipType.CHAT_WITH,
        properties={
            "message_count": 10,
            "new_field": "新字段",
        },
        conflict_strategy=ConflictResolutionStrategy.MERGE_PROPERTIES,
    )
    
    assert merged_rel.id == initial_rel.id
    assert merged_rel.properties["message_count"] == 10  # 更新
    assert merged_rel.properties["topics"] == ["数学"]  # 保留
    assert merged_rel.properties["new_field"] == "新字段"  # 添加


# ==================== 批量操作和事务测试 ====================

@pytest.mark.asyncio
async def test_execute_batch_with_transaction_success(setup_database):
    """测试批量操作：所有操作成功时提交事务"""
    operations = [
        CreateNodeOperation(
            node_type=NodeType.STUDENT,
            properties={"student_id": "S201", "name": "批量学生1"},
        ),
        CreateNodeOperation(
            node_type=NodeType.STUDENT,
            properties={"student_id": "S202", "name": "批量学生2"},
        ),
        CreateNodeOperation(
            node_type=NodeType.TEACHER,
            properties={"teacher_id": "T201", "name": "批量教师1"},
        ),
    ]
    
    result = await graph_service.execute_batch(operations, use_transaction=True)
    
    assert result.success is True
    assert result.operations_count == 3
    assert result.successful_operations == 3
    assert result.failed_operations == 0
    assert len(result.results) == 3
    assert len(result.errors) == 0
    
    # 验证节点已创建
    async with neo4j_connection.get_session() as session:
        result_query = await session.run("MATCH (n) RETURN count(n) as count")
        record = await result_query.single()
        assert record["count"] == 3


@pytest.mark.asyncio
async def test_execute_batch_with_transaction_rollback_on_failure(setup_database):
    """测试批量操作：任何操作失败时回滚所有操作"""
    operations = [
        CreateNodeOperation(
            node_type=NodeType.STUDENT,
            properties={"student_id": "S203", "name": "批量学生3"},
        ),
        CreateNodeOperation(
            node_type=NodeType.STUDENT,
            properties={"student_id": "S204", "name": "批量学生4"},
        ),
        CreateNodeOperation(
            node_type=NodeType.STUDENT,
            properties={"invalid_field": "这会导致验证失败"},  # 缺少必需字段
        ),
    ]
    
    with pytest.raises(RuntimeError) as exc_info:
        await graph_service.execute_batch(operations, use_transaction=True)
    
    assert "rolled back" in str(exc_info.value).lower()
    
    # 验证所有操作都被回滚，没有节点被创建
    async with neo4j_connection.get_session() as session:
        result_query = await session.run("MATCH (n) RETURN count(n) as count")
        record = await result_query.single()
        assert record["count"] == 0


@pytest.mark.asyncio
async def test_execute_batch_without_transaction(setup_database):
    """测试批量操作：不使用事务时部分成功"""
    operations = [
        CreateNodeOperation(
            node_type=NodeType.STUDENT,
            properties={"student_id": "S205", "name": "批量学生5"},
        ),
        CreateNodeOperation(
            node_type=NodeType.STUDENT,
            properties={"student_id": "S206", "name": "批量学生6"},
        ),
        CreateNodeOperation(
            node_type=NodeType.STUDENT,
            properties={"invalid_field": "这会导致验证失败"},  # 缺少必需字段
        ),
        CreateNodeOperation(
            node_type=NodeType.STUDENT,
            properties={"student_id": "S207", "name": "批量学生7"},
        ),
    ]
    
    result = await graph_service.execute_batch(operations, use_transaction=False)
    
    assert result.success is False  # 有失败操作
    assert result.operations_count == 4
    assert result.successful_operations == 3  # 3个成功
    assert result.failed_operations == 1  # 1个失败
    assert len(result.errors) == 1
    
    # 验证成功的节点已创建
    async with neo4j_connection.get_session() as session:
        result_query = await session.run("MATCH (n:Student) RETURN count(n) as count")
        record = await result_query.single()
        assert record["count"] == 3


@pytest.mark.asyncio
async def test_execute_batch_with_mixed_operations(setup_database):
    """测试批量操作：混合节点和关系操作"""
    # 先创建一些节点用于后续关系创建
    student1 = await graph_service.create_node(
        NodeType.STUDENT,
        {"student_id": "S208", "name": "学生X"}
    )
    student2 = await graph_service.create_node(
        NodeType.STUDENT,
        {"student_id": "S209", "name": "学生Y"}
    )
    
    operations = [
        CreateNodeOperation(
            node_type=NodeType.TEACHER,
            properties={"teacher_id": "T202", "name": "教师X"},
        ),
        CreateRelationshipOperation(
            from_node_id=student1.id,
            to_node_id=student2.id,
            relationship_type=RelationshipType.CHAT_WITH,
            properties={
                "message_count": 5,
                "last_interaction_date": datetime(2024, 1, 15),
            },
        ),
        UpdateNodeOperation(
            node_id=student1.id,
            properties={"grade": "3"},
        ),
    ]
    
    result = await graph_service.execute_batch(operations, use_transaction=True)
    
    assert result.success is True
    assert result.operations_count == 3
    assert result.successful_operations == 3
    assert result.failed_operations == 0
    
    # 验证操作结果
    async with neo4j_connection.get_session() as session:
        # 验证教师节点已创建
        teacher_query = await session.run(
            "MATCH (t:Teacher {teacher_id: 'T202'}) RETURN t"
        )
        teacher_record = await teacher_query.single()
        assert teacher_record is not None
        
        # 验证关系已创建
        rel_query = await session.run(
            """
            MATCH (s1:Student {student_id: 'S208'})-[r:CHAT_WITH]->(s2:Student {student_id: 'S209'})
            RETURN r
            """
        )
        rel_record = await rel_query.single()
        assert rel_record is not None
        
        # 验证节点已更新
        student_query = await session.run(
            "MATCH (s:Student {student_id: 'S208'}) RETURN s.grade as grade"
        )
        student_record = await student_query.single()
        assert student_record["grade"] == "3"


@pytest.mark.asyncio
async def test_execute_batch_empty_operations(setup_database):
    """测试批量操作：空操作列表"""
    result = await graph_service.execute_batch([], use_transaction=True)
    
    assert result.success is True
    assert result.operations_count == 0
    assert result.successful_operations == 0
    assert result.failed_operations == 0
    assert len(result.results) == 0
    assert len(result.errors) == 0


@pytest.mark.asyncio
async def test_execute_batch_update_operations(setup_database):
    """测试批量操作：批量更新节点"""
    # 创建一些节点
    student1 = await graph_service.create_node(
        NodeType.STUDENT,
        {"student_id": "S210", "name": "学生批量更新1", "grade": "1"}
    )
    student2 = await graph_service.create_node(
        NodeType.STUDENT,
        {"student_id": "S211", "name": "学生批量更新2", "grade": "1"}
    )
    student3 = await graph_service.create_node(
        NodeType.STUDENT,
        {"student_id": "S212", "name": "学生批量更新3", "grade": "1"}
    )
    
    # 批量更新
    operations = [
        UpdateNodeOperation(
            node_id=student1.id,
            properties={"grade": "2"},
        ),
        UpdateNodeOperation(
            node_id=student2.id,
            properties={"grade": "2"},
        ),
        UpdateNodeOperation(
            node_id=student3.id,
            properties={"grade": "2"},
        ),
    ]
    
    result = await graph_service.execute_batch(operations, use_transaction=True)
    
    assert result.success is True
    assert result.successful_operations == 3
    
    # 验证所有节点都已更新
    async with neo4j_connection.get_session() as session:
        query = await session.run(
            """
            MATCH (s:Student)
            WHERE s.student_id IN ['S210', 'S211', 'S212']
            RETURN s.grade as grade
            """
        )
        records = await query.data()
        assert len(records) == 3
        assert all(record["grade"] == "2" for record in records)


@pytest.mark.asyncio
async def test_execute_batch_relationship_operations(setup_database):
    """测试批量操作：批量创建和更新关系"""
    # 创建节点
    student1 = await graph_service.create_node(
        NodeType.STUDENT,
        {"student_id": "S213", "name": "学生关系1"}
    )
    student2 = await graph_service.create_node(
        NodeType.STUDENT,
        {"student_id": "S214", "name": "学生关系2"}
    )
    student3 = await graph_service.create_node(
        NodeType.STUDENT,
        {"student_id": "S215", "name": "学生关系3"}
    )
    
    # 批量创建关系
    operations = [
        CreateRelationshipOperation(
            from_node_id=student1.id,
            to_node_id=student2.id,
            relationship_type=RelationshipType.CHAT_WITH,
            properties={
                "message_count": 5,
                "last_interaction_date": datetime(2024, 1, 15),
            },
        ),
        CreateRelationshipOperation(
            from_node_id=student2.id,
            to_node_id=student3.id,
            relationship_type=RelationshipType.CHAT_WITH,
            properties={
                "message_count": 3,
                "last_interaction_date": datetime(2024, 1, 20),
            },
        ),
        CreateRelationshipOperation(
            from_node_id=student1.id,
            to_node_id=student3.id,
            relationship_type=RelationshipType.LIKES,
            properties={
                "like_count": 2,
                "last_like_date": datetime(2024, 1, 25),
            },
        ),
    ]
    
    result = await graph_service.execute_batch(operations, use_transaction=True)
    
    assert result.success is True
    assert result.successful_operations == 3
    
    # 验证关系已创建
    async with neo4j_connection.get_session() as session:
        query = await session.run(
            "MATCH ()-[r]->() RETURN count(r) as count"
        )
        record = await query.single()
        assert record["count"] == 3


@pytest.mark.asyncio
async def test_batch_operations_atomicity(setup_database):
    """测试批量操作的原子性：验证事务要么全部成功要么全部失败"""
    # 创建一个学生节点用于后续操作
    student = await graph_service.create_node(
        NodeType.STUDENT,
        {"student_id": "S216", "name": "原子性测试学生"}
    )
    
    # 创建一个会失败的批量操作
    operations = [
        CreateNodeOperation(
            node_type=NodeType.TEACHER,
            properties={"teacher_id": "T203", "name": "教师原子性1"},
        ),
        CreateNodeOperation(
            node_type=NodeType.TEACHER,
            properties={"teacher_id": "T204", "name": "教师原子性2"},
        ),
        UpdateNodeOperation(
            node_id="nonexistent-node-id",  # 这会失败
            properties={"grade": "5"},
        ),
        CreateNodeOperation(
            node_type=NodeType.TEACHER,
            properties={"teacher_id": "T205", "name": "教师原子性3"},
        ),
    ]
    
    # 记录操作前的节点数量
    async with neo4j_connection.get_session() as session:
        before_query = await session.run("MATCH (n) RETURN count(n) as count")
        before_record = await before_query.single()
        count_before = before_record["count"]
    
    # 执行批量操作（应该失败并回滚）
    with pytest.raises(RuntimeError):
        await graph_service.execute_batch(operations, use_transaction=True)
    
    # 验证节点数量没有变化（所有操作都被回滚）
    async with neo4j_connection.get_session() as session:
        after_query = await session.run("MATCH (n) RETURN count(n) as count")
        after_record = await after_query.single()
        count_after = after_record["count"]
    
    assert count_after == count_before  # 原子性：没有部分提交
