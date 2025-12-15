"""分析报告服务集成测试"""

import pytest
from datetime import datetime, timedelta

from app.database import init_database, close_database, neo4j_connection
from app.services.graph_service import graph_service
from app.services.report_service import report_service, ReportFormat
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
async def sample_graph_with_errors(setup_database):
    """创建包含错误数据的示例图谱"""
    # 创建学生节点
    students = []
    for i in range(5):
        student = await graph_service.create_node(
            NodeType.STUDENT,
            {
                "student_id": f"S{i+1:03d}",
                "name": f"学生{i+1}",
                "grade": str((i % 3) + 1),
            }
        )
        students.append(student)
    
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
    courses = []
    for i in range(3):
        course = await graph_service.create_node(
            NodeType.COURSE,
            {
                "course_id": f"C{i+1:03d}",
                "name": f"课程{i+1}",
                "description": f"课程{i+1}描述",
                "difficulty": ["beginner", "intermediate", "advanced"][i],
            }
        )
        courses.append(course)
    
    # 创建知识点节点
    knowledge_points = []
    for i in range(4):
        kp = await graph_service.create_node(
            NodeType.KNOWLEDGE_POINT,
            {
                "knowledge_point_id": f"KP{i+1:03d}",
                "name": f"知识点{i+1}",
                "description": f"知识点{i+1}描述",
                "category": "数学",
            }
        )
        knowledge_points.append(kp)
    
    # 创建错误类型节点
    error_types = []
    for i in range(3):
        error_type = await graph_service.create_node(
            NodeType.ERROR_TYPE,
            {
                "error_type_id": f"E{i+1:03d}",
                "name": f"错误类型{i+1}",
                "description": f"错误类型{i+1}描述",
                "severity": ["low", "medium", "high"][i],
            }
        )
        error_types.append(error_type)
    
    # 创建学习关系
    for student in students[:4]:
        for course in courses[:2]:
            await graph_service.create_relationship(
                from_node_id=student.id,
                to_node_id=course.id,
                relationship_type=RelationshipType.LEARNS,
                properties={
                    "enrollment_date": datetime.utcnow(),
                    "progress": 50.0,
                }
            )
    
    # 创建课程包含知识点关系
    for i, course in enumerate(courses):
        for kp in knowledge_points[i:i+2]:
            await graph_service.create_relationship(
                from_node_id=course.id,
                to_node_id=kp.id,
                relationship_type=RelationshipType.CONTAINS,
                properties={
                    "order": 1,
                    "importance": "core",
                }
            )
    
    # 创建学生互动关系
    await graph_service.create_relationship(
        from_node_id=students[0].id,
        to_node_id=students[1].id,
        relationship_type=RelationshipType.CHAT_WITH,
        properties={
            "message_count": 10,
            "last_interaction_date": datetime.utcnow(),
        }
    )
    
    await graph_service.create_relationship(
        from_node_id=students[1].id,
        to_node_id=students[2].id,
        relationship_type=RelationshipType.CHAT_WITH,
        properties={
            "message_count": 5,
            "last_interaction_date": datetime.utcnow(),
        }
    )
    
    # 创建学生错误关系（使用多课程错误功能）
    # 学生1在课程1中有多个错误
    await graph_service.create_student_multi_course_error(
        student_id="S001",
        error_type_id="E001",
        course_id="C001",
        occurrence_time=datetime.utcnow(),
        knowledge_point_ids=["KP001"],
    )
    
    # 学生1在课程1中重复错误
    await graph_service.create_student_multi_course_error(
        student_id="S001",
        error_type_id="E001",
        course_id="C001",
        occurrence_time=datetime.utcnow(),
        knowledge_point_ids=["KP001"],
    )
    
    # 学生2也有错误
    await graph_service.create_student_multi_course_error(
        student_id="S002",
        error_type_id="E001",
        course_id="C001",
        occurrence_time=datetime.utcnow(),
        knowledge_point_ids=["KP001"],
    )
    
    # 学生3有不同的错误
    await graph_service.create_student_multi_course_error(
        student_id="S003",
        error_type_id="E002",
        course_id="C002",
        occurrence_time=datetime.utcnow(),
        knowledge_point_ids=["KP002"],
    )
    
    return {
        "students": students,
        "teacher": teacher,
        "courses": courses,
        "knowledge_points": knowledge_points,
        "error_types": error_types,
    }


@pytest.mark.asyncio
async def test_generate_graph_statistics(sample_graph_with_errors):
    """测试生成图谱统计信息"""
    stats = await report_service.generate_graph_statistics()
    
    # 验证节点统计
    assert stats.total_nodes > 0
    assert "Student" in stats.node_type_distribution
    assert "Course" in stats.node_type_distribution
    assert "KnowledgePoint" in stats.node_type_distribution
    assert "ErrorType" in stats.node_type_distribution
    
    # 验证节点数量
    assert stats.node_type_distribution["Student"] == 5
    assert stats.node_type_distribution["Course"] == 3
    assert stats.node_type_distribution["KnowledgePoint"] == 4
    assert stats.node_type_distribution["ErrorType"] == 3
    
    # 验证关系统计
    assert stats.total_relationships > 0
    assert "LEARNS" in stats.relationship_type_distribution
    assert "CONTAINS" in stats.relationship_type_distribution
    
    # 验证时间戳
    assert isinstance(stats.timestamp, datetime)


@pytest.mark.asyncio
async def test_analyze_student_performance(sample_graph_with_errors):
    """测试学生表现分析"""
    analysis = await report_service.analyze_student_performance(top_n=5)
    
    # 验证高频错误
    assert len(analysis.high_frequency_errors) > 0
    
    # 验证高频错误包含必要字段
    for error in analysis.high_frequency_errors:
        assert "knowledge_point_id" in error
        assert "knowledge_point_name" in error
        assert "error_type_id" in error
        assert "error_type_name" in error
        assert "total_occurrences" in error
        assert "student_count" in error
    
    # 验证需要关注的学生
    assert len(analysis.students_needing_attention) > 0
    
    # 验证学生信息包含必要字段
    for student in analysis.students_needing_attention:
        assert "student_id" in student
        assert "student_name" in student
        assert "total_errors" in student
        assert "error_types_count" in student
    
    # 验证错误分布
    assert len(analysis.error_distribution) > 0


@pytest.mark.asyncio
async def test_analyze_course_effectiveness(sample_graph_with_errors):
    """测试课程效果分析"""
    analysis = await report_service.analyze_course_effectiveness()
    
    # 验证课程指标
    assert len(analysis.course_metrics) > 0
    
    # 验证课程指标包含必要字段
    for course in analysis.course_metrics:
        assert "course_id" in course
        assert "course_name" in course
        assert "participation" in course
        assert "students_with_errors" in course
        assert "total_errors" in course
        assert "error_rate" in course
        
        # 验证错误率在合理范围内
        assert 0.0 <= course["error_rate"] <= 1.0


@pytest.mark.asyncio
async def test_analyze_interaction_patterns(sample_graph_with_errors):
    """测试互动模式分析"""
    analysis = await report_service.analyze_interaction_patterns(min_network_size=1)
    
    # 验证社交网络
    assert len(analysis.social_networks) > 0
    
    # 验证社交网络包含必要字段
    for network in analysis.social_networks:
        assert "student_id" in network
        assert "student_name" in network
        assert "connection_count" in network
        assert "connected_students" in network
    
    # 验证孤立学生
    assert len(analysis.isolated_students) > 0
    
    # 验证孤立学生包含必要字段
    for student in analysis.isolated_students:
        assert "student_id" in student
        assert "student_name" in student
    
    # 验证互动统计
    assert "total_students" in analysis.interaction_statistics
    assert "students_with_interactions" in analysis.interaction_statistics
    assert "total_interactions" in analysis.interaction_statistics
    assert "interaction_rate" in analysis.interaction_statistics
    
    # 验证互动率在合理范围内
    assert 0.0 <= analysis.interaction_statistics["interaction_rate"] <= 1.0


@pytest.mark.asyncio
async def test_generate_complete_report(sample_graph_with_errors):
    """测试生成完整报告"""
    report = await report_service.generate_report()
    
    # 验证报告包含所有部分
    assert report.graph_statistics is not None
    assert report.student_performance is not None
    assert report.course_effectiveness is not None
    assert report.interaction_patterns is not None
    assert isinstance(report.generated_at, datetime)
    
    # 验证报告可以转换为字典
    report_dict = report.to_dict()
    assert "graph_statistics" in report_dict
    assert "student_performance" in report_dict
    assert "course_effectiveness" in report_dict
    assert "interaction_patterns" in report_dict
    assert "generated_at" in report_dict


@pytest.mark.asyncio
async def test_generate_partial_report(sample_graph_with_errors):
    """测试生成部分报告"""
    # 只生成图谱统计和学生表现分析
    report = await report_service.generate_report(
        include_graph_stats=True,
        include_student_performance=True,
        include_course_effectiveness=False,
        include_interaction_patterns=False,
    )
    
    # 验证包含的部分
    assert report.graph_statistics is not None
    assert report.student_performance is not None
    
    # 验证未包含的部分为空
    assert len(report.course_effectiveness.course_metrics) == 0
    assert len(report.interaction_patterns.social_networks) == 0


@pytest.mark.asyncio
async def test_export_report_json(sample_graph_with_errors):
    """测试导出 JSON 格式报告"""
    report = await report_service.generate_report()
    
    # 导出为 JSON
    json_bytes = await report_service.export_report(report, format=ReportFormat.JSON)
    
    # 验证导出结果
    assert isinstance(json_bytes, bytes)
    assert len(json_bytes) > 0
    
    # 验证可以解析为 JSON
    import json
    json_str = json_bytes.decode("utf-8")
    report_data = json.loads(json_str)
    
    assert "graph_statistics" in report_data
    assert "student_performance" in report_data
    assert "course_effectiveness" in report_data
    assert "interaction_patterns" in report_data


@pytest.mark.asyncio
async def test_export_report_pdf(sample_graph_with_errors):
    """测试导出 PDF 格式报告"""
    report = await report_service.generate_report()
    
    # 尝试导出为 PDF
    try:
        pdf_bytes = await report_service.export_report(report, format=ReportFormat.PDF)
        
        # 验证导出结果
        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0
        
        # 验证 PDF 文件头
        assert pdf_bytes[:4] == b'%PDF'
    except RuntimeError as e:
        # 如果 reportlab 未安装，跳过测试
        if "reportlab" in str(e):
            pytest.skip("reportlab not installed")
        else:
            raise


@pytest.mark.asyncio
async def test_report_to_json_string(sample_graph_with_errors):
    """测试报告转换为 JSON 字符串"""
    report = await report_service.generate_report()
    
    # 转换为 JSON 字符串
    json_str = report.to_json()
    
    # 验证结果
    assert isinstance(json_str, str)
    assert len(json_str) > 0
    
    # 验证可以解析
    import json
    report_data = json.loads(json_str)
    assert "graph_statistics" in report_data


@pytest.mark.asyncio
async def test_empty_graph_statistics(setup_database):
    """测试空图谱的统计"""
    stats = await report_service.generate_graph_statistics()
    
    # 验证空图谱统计
    assert stats.total_nodes == 0
    assert len(stats.node_type_distribution) == 0
    assert stats.total_relationships == 0
    assert len(stats.relationship_type_distribution) == 0


@pytest.mark.asyncio
async def test_student_performance_no_errors(setup_database):
    """测试没有错误时的学生表现分析"""
    # 创建一些学生但没有错误
    await graph_service.create_node(
        NodeType.STUDENT,
        {
            "student_id": "S001",
            "name": "学生1",
        }
    )
    
    analysis = await report_service.analyze_student_performance()
    
    # 验证结果为空
    assert len(analysis.high_frequency_errors) == 0
    assert len(analysis.students_needing_attention) == 0
    assert len(analysis.error_distribution) == 0


@pytest.mark.asyncio
async def test_course_effectiveness_no_students(setup_database):
    """测试没有学生时的课程效果分析"""
    # 创建课程但没有学生
    await graph_service.create_node(
        NodeType.COURSE,
        {
            "course_id": "C001",
            "name": "课程1",
            "description": "课程1描述",
        }
    )
    
    analysis = await report_service.analyze_course_effectiveness()
    
    # 验证课程指标
    assert len(analysis.course_metrics) == 1
    assert analysis.course_metrics[0]["participation"] == 0
    assert analysis.course_metrics[0]["error_rate"] == 0.0


@pytest.mark.asyncio
async def test_interaction_patterns_no_interactions(setup_database):
    """测试没有互动时的互动模式分析"""
    # 创建学生但没有互动
    for i in range(3):
        await graph_service.create_node(
            NodeType.STUDENT,
            {
                "student_id": f"S{i+1:03d}",
                "name": f"学生{i+1}",
            }
        )
    
    analysis = await report_service.analyze_interaction_patterns()
    
    # 验证结果
    assert len(analysis.social_networks) == 0
    assert len(analysis.isolated_students) == 3  # 所有学生都是孤立的
    assert analysis.interaction_statistics["total_students"] == 3
    assert analysis.interaction_statistics["students_with_interactions"] == 0
    assert analysis.interaction_statistics["interaction_rate"] == 0.0
