"""数据导入服务测试"""

import pytest
from datetime import datetime

from app.database import init_database, close_database, neo4j_connection
from app.services.data_import_service import (
    data_import_service,
    RawRecord,
    RecordType,
    ValidationResult,
)
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
async def test_validate_student_interaction_valid():
    """测试验证有效的学生互动记录"""
    record = RawRecord(
        type=RecordType.STUDENT_INTERACTION,
        timestamp=datetime.utcnow(),
        data={
            "student_id_from": "S001",
            "student_id_to": "S002",
            "interaction_type": "chat",
            "message_count": 5,
        },
    )
    
    result = data_import_service.validate_record(record)
    
    assert result.is_valid is True
    assert len(result.errors) == 0


@pytest.mark.asyncio
async def test_validate_student_interaction_missing_fields():
    """测试验证缺少必需字段的学生互动记录"""
    record = RawRecord(
        type=RecordType.STUDENT_INTERACTION,
        timestamp=datetime.utcnow(),
        data={
            "student_id_from": "S001",
            # 缺少 student_id_to 和 interaction_type
        },
    )
    
    result = data_import_service.validate_record(record)
    
    assert result.is_valid is False
    assert len(result.errors) > 0
    assert any("student_id_to" in error for error in result.errors)
    assert any("interaction_type" in error for error in result.errors)


@pytest.mark.asyncio
async def test_validate_student_interaction_invalid_type():
    """测试验证无效互动类型的学生互动记录"""
    record = RawRecord(
        type=RecordType.STUDENT_INTERACTION,
        timestamp=datetime.utcnow(),
        data={
            "student_id_from": "S001",
            "student_id_to": "S002",
            "interaction_type": "invalid_type",
        },
    )
    
    result = data_import_service.validate_record(record)
    
    assert result.is_valid is False
    assert any("interaction_type" in error for error in result.errors)


@pytest.mark.asyncio
async def test_validate_course_record_valid():
    """测试验证有效的课程记录"""
    record = RawRecord(
        type=RecordType.COURSE_RECORD,
        timestamp=datetime.utcnow(),
        data={
            "student_id": "S001",
            "course_id": "C001",
            "progress": 50.0,
        },
    )
    
    result = data_import_service.validate_record(record)
    
    assert result.is_valid is True
    assert len(result.errors) == 0


@pytest.mark.asyncio
async def test_validate_course_record_invalid_progress():
    """测试验证无效进度的课程记录"""
    record = RawRecord(
        type=RecordType.COURSE_RECORD,
        timestamp=datetime.utcnow(),
        data={
            "student_id": "S001",
            "course_id": "C001",
            "progress": 150.0,  # 超出范围
        },
    )
    
    result = data_import_service.validate_record(record)
    
    assert result.is_valid is False
    assert any("progress" in error for error in result.errors)


@pytest.mark.asyncio
async def test_validate_error_record_valid():
    """测试验证有效的错误记录"""
    record = RawRecord(
        type=RecordType.ERROR_RECORD,
        timestamp=datetime.utcnow(),
        data={
            "student_id": "S001",
            "course_id": "C001",
            "error_text": "学生在解题时出现了逻辑错误",
        },
    )
    
    result = data_import_service.validate_record(record)
    
    assert result.is_valid is True
    assert len(result.errors) == 0


@pytest.mark.asyncio
async def test_import_batch_single_record(setup_database):
    """测试导入单条记录"""
    records = [
        RawRecord(
            type=RecordType.STUDENT_INTERACTION,
            timestamp=datetime.utcnow(),
            data={
                "student_id_from": "S001",
                "student_name_from": "张三",
                "student_id_to": "S002",
                "student_name_to": "李四",
                "interaction_type": "chat",
                "message_count": 3,
            },
        )
    ]
    
    result = await data_import_service.import_batch(records, batch_size=1000)
    
    assert result.success_count == 1
    assert result.failure_count == 0
    assert len(result.errors) == 0


@pytest.mark.asyncio
async def test_import_batch_multiple_records(setup_database):
    """测试导入多条记录"""
    records = [
        RawRecord(
            type=RecordType.COURSE_RECORD,
            timestamp=datetime.utcnow(),
            data={
                "student_id": "S003",
                "student_name": "王五",
                "course_id": "C001",
                "course_name": "数学",
                "progress": 75.0,
            },
        ),
        RawRecord(
            type=RecordType.TEACHER_INTERACTION,
            timestamp=datetime.utcnow(),
            data={
                "teacher_id": "T001",
                "teacher_name": "赵老师",
                "student_id": "S003",
                "student_name": "王五",
                "interaction_count": 2,
            },
        ),
    ]
    
    result = await data_import_service.import_batch(records, batch_size=1000)
    
    assert result.success_count == 2
    assert result.failure_count == 0


@pytest.mark.asyncio
async def test_import_batch_with_invalid_records(setup_database):
    """测试导入包含无效记录的批次"""
    records = [
        RawRecord(
            type=RecordType.STUDENT_INTERACTION,
            timestamp=datetime.utcnow(),
            data={
                "student_id_from": "S004",
                "student_id_to": "S005",
                "interaction_type": "chat",
            },
        ),
        RawRecord(
            type=RecordType.STUDENT_INTERACTION,
            timestamp=datetime.utcnow(),
            data={
                "student_id_from": "S006",
                # 缺少必需字段
            },
        ),
    ]
    
    result = await data_import_service.import_batch(records, batch_size=1000)
    
    assert result.success_count == 1
    assert result.failure_count == 1
    assert len(result.errors) == 1


@pytest.mark.asyncio
async def test_import_batch_respects_batch_size(setup_database):
    """测试批处理大小限制"""
    # 创建 2500 条记录，批处理大小为 1000
    records = [
        RawRecord(
            type=RecordType.STUDENT_INTERACTION,
            timestamp=datetime.utcnow(),
            data={
                "student_id_from": f"S{i:04d}",
                "student_id_to": f"S{i+1:04d}",
                "interaction_type": "chat",
            },
        )
        for i in range(2500)
    ]
    
    result = await data_import_service.import_batch(records, batch_size=1000)
    
    # 验证所有记录都被处理
    assert result.success_count + result.failure_count == 2500


@pytest.mark.asyncio
async def test_get_progress_during_import(setup_database):
    """测试在导入过程中获取进度"""
    records = [
        RawRecord(
            type=RecordType.COURSE_RECORD,
            timestamp=datetime.utcnow(),
            data={
                "student_id": f"S{i:04d}",
                "course_id": "C001",
                "progress": 50.0,
            },
        )
        for i in range(10)
    ]
    
    # 启动导入
    result = await data_import_service.import_batch(records, batch_size=5)
    
    # 导入完成后，进度应该显示 100%
    progress = data_import_service.get_progress()
    assert progress is not None
    assert progress.total_records == 10
    assert progress.processed_records == 10
    assert progress.progress_percentage == 100.0


@pytest.mark.asyncio
async def test_import_batch_invalid_batch_size():
    """测试无效的批处理大小"""
    records = [
        RawRecord(
            type=RecordType.STUDENT_INTERACTION,
            timestamp=datetime.utcnow(),
            data={
                "student_id_from": "S001",
                "student_id_to": "S002",
                "interaction_type": "chat",
            },
        )
    ]
    
    # 批处理大小太小
    with pytest.raises(ValueError):
        await data_import_service.import_batch(records, batch_size=0)
    
    # 批处理大小太大
    with pytest.raises(ValueError):
        await data_import_service.import_batch(records, batch_size=20000)


@pytest.mark.asyncio
async def test_process_error_record(setup_database):
    """测试处理错误记录"""
    records = [
        RawRecord(
            type=RecordType.ERROR_RECORD,
            timestamp=datetime.utcnow(),
            data={
                "student_id": "S007",
                "student_name": "测试学生",
                "course_id": "C001",
                "error_text": "计算错误：2+2=5",
                "error_type": "计算错误",
                "severity": "medium",
            },
        )
    ]
    
    result = await data_import_service.import_batch(records, batch_size=1000)
    
    assert result.success_count == 1
    assert result.failure_count == 0
