"""演示分析报告生成服务的使用"""

import asyncio
from datetime import datetime

from app.database import init_database, close_database
from app.services.report_service import report_service, ReportFormat
from app.services.graph_service import graph_service
from app.models.nodes import NodeType
from app.models.relationships import RelationshipType


async def create_sample_data():
    """创建示例数据"""
    print("创建示例数据...")
    
    # 创建学生
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
        print(f"  创建学生: {student.properties['name']}")
    
    # 创建课程
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
        print(f"  创建课程: {course.properties['name']}")
    
    # 创建知识点
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
        print(f"  创建知识点: {kp.properties['name']}")
    
    # 创建错误类型
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
        print(f"  创建错误类型: {error_type.properties['name']}")
    
    # 创建学习关系
    print("\n创建学习关系...")
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
    print("创建课程-知识点关系...")
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
    print("创建学生互动关系...")
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
    
    # 创建学生错误关系
    print("创建学生错误关系...")
    await graph_service.create_student_multi_course_error(
        student_id="S001",
        error_type_id="E001",
        course_id="C001",
        occurrence_time=datetime.utcnow(),
        knowledge_point_ids=["KP001"],
    )
    
    # 重复错误
    await graph_service.create_student_multi_course_error(
        student_id="S001",
        error_type_id="E001",
        course_id="C001",
        occurrence_time=datetime.utcnow(),
        knowledge_point_ids=["KP001"],
    )
    
    await graph_service.create_student_multi_course_error(
        student_id="S002",
        error_type_id="E001",
        course_id="C001",
        occurrence_time=datetime.utcnow(),
        knowledge_point_ids=["KP001"],
    )
    
    print("\n示例数据创建完成！\n")


async def demo_graph_statistics():
    """演示图谱统计功能"""
    print("=" * 60)
    print("1. 图谱统计")
    print("=" * 60)
    
    stats = await report_service.generate_graph_statistics()
    
    print(f"\n节点总数: {stats.total_nodes}")
    print("\n节点类型分布:")
    for node_type, count in stats.node_type_distribution.items():
        print(f"  {node_type}: {count}")
    
    print(f"\n关系总数: {stats.total_relationships}")
    print("\n关系类型分布:")
    for rel_type, count in stats.relationship_type_distribution.items():
        print(f"  {rel_type}: {count}")
    
    print(f"\n统计时间: {stats.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")


async def demo_student_performance():
    """演示学生表现分析"""
    print("\n" + "=" * 60)
    print("2. 学生表现分析")
    print("=" * 60)
    
    analysis = await report_service.analyze_student_performance(top_n=5)
    
    print(f"\n高频错误知识点 (前 {len(analysis.high_frequency_errors)} 个):")
    for i, error in enumerate(analysis.high_frequency_errors, 1):
        print(f"\n  {i}. {error['knowledge_point_name']}")
        print(f"     错误类型: {error['error_type_name']}")
        print(f"     总发生次数: {error['total_occurrences']}")
        print(f"     涉及学生数: {error['student_count']}")
    
    print(f"\n需要关注的学生 (前 {len(analysis.students_needing_attention)} 个):")
    for i, student in enumerate(analysis.students_needing_attention, 1):
        print(f"\n  {i}. {student['student_name']} ({student['student_id']})")
        print(f"     总错误数: {student['total_errors']}")
        print(f"     错误类型数: {student['error_types_count']}")


async def demo_course_effectiveness():
    """演示课程效果分析"""
    print("\n" + "=" * 60)
    print("3. 课程效果分析")
    print("=" * 60)
    
    analysis = await report_service.analyze_course_effectiveness()
    
    print(f"\n课程指标 (共 {len(analysis.course_metrics)} 个课程):")
    for i, course in enumerate(analysis.course_metrics, 1):
        print(f"\n  {i}. {course['course_name']} ({course['course_id']})")
        print(f"     参与人数: {course['participation']}")
        print(f"     有错误的学生数: {course['students_with_errors']}")
        print(f"     总错误数: {course['total_errors']}")
        print(f"     错误率: {course['error_rate']:.2%}")


async def demo_interaction_patterns():
    """演示互动模式分析"""
    print("\n" + "=" * 60)
    print("4. 互动模式分析")
    print("=" * 60)
    
    analysis = await report_service.analyze_interaction_patterns(min_network_size=1)
    
    print(f"\n活跃社交网络 (前 {len(analysis.social_networks)} 个):")
    for i, network in enumerate(analysis.social_networks, 1):
        print(f"\n  {i}. {network['student_name']} ({network['student_id']})")
        print(f"     连接数: {network['connection_count']}")
        print(f"     连接的学生: {', '.join(network['connected_students'][:5])}")
    
    print(f"\n孤立学生 (共 {len(analysis.isolated_students)} 个):")
    for i, student in enumerate(analysis.isolated_students[:5], 1):
        print(f"  {i}. {student['student_name']} ({student['student_id']})")
    
    print("\n互动统计:")
    stats = analysis.interaction_statistics
    print(f"  总学生数: {stats['total_students']}")
    print(f"  有互动的学生数: {stats['students_with_interactions']}")
    print(f"  总互动数: {stats['total_interactions']}")
    print(f"  互动率: {stats['interaction_rate']:.2%}")


async def demo_complete_report():
    """演示生成完整报告"""
    print("\n" + "=" * 60)
    print("5. 生成完整报告")
    print("=" * 60)
    
    print("\n生成完整分析报告...")
    report = await report_service.generate_report()
    
    print(f"报告生成时间: {report.generated_at.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 导出为 JSON
    print("\n导出为 JSON 格式...")
    json_bytes = await report_service.export_report(report, format=ReportFormat.JSON)
    print(f"JSON 报告大小: {len(json_bytes)} 字节")
    
    # 保存到文件
    with open("report.json", "wb") as f:
        f.write(json_bytes)
    print("JSON 报告已保存到: report.json")
    
    # 尝试导出为 PDF
    try:
        print("\n导出为 PDF 格式...")
        pdf_bytes = await report_service.export_report(report, format=ReportFormat.PDF)
        print(f"PDF 报告大小: {len(pdf_bytes)} 字节")
        
        # 保存到文件
        with open("report.pdf", "wb") as f:
            f.write(pdf_bytes)
        print("PDF 报告已保存到: report.pdf")
    except RuntimeError as e:
        print(f"PDF 导出失败: {e}")
        print("提示: 安装 reportlab 库以支持 PDF 导出: pip install reportlab")


async def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("教育知识图谱分析报告服务演示")
    print("=" * 60)
    
    try:
        # 初始化数据库
        print("\n初始化数据库连接...")
        await init_database()
        
        # 创建示例数据
        await create_sample_data()
        
        # 演示各项功能
        await demo_graph_statistics()
        await demo_student_performance()
        await demo_course_effectiveness()
        await demo_interaction_patterns()
        await demo_complete_report()
        
        print("\n" + "=" * 60)
        print("演示完成！")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # 关闭数据库连接
        print("\n关闭数据库连接...")
        await close_database()


if __name__ == "__main__":
    asyncio.run(main())
