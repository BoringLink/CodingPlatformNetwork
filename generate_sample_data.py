#!/usr/bin/env python3
"""生成模拟数据脚本"""

import asyncio
from app.database import init_database, close_database, neo4j_connection
from app.services.graph_service import graph_service
from app.models.nodes import NodeType
from app.models.relationships import RelationshipType
from datetime import datetime, timedelta


async def generate_sample_data():
    """生成示例图谱数据"""
    try:
        # 初始化数据库连接
        await init_database()
        print("数据库连接成功")

        # 清理现有数据
        async with neo4j_connection.get_session() as session:
            await session.run("MATCH (n) DETACH DELETE n")
        print("已清理现有数据")

        # 创建学生节点
        student1 = await graph_service.create_node(
            NodeType.STUDENT,
            {
                "student_id": "S001",
                "name": "张三",
                "grade": "3",
            }
        )
        print(f"创建学生节点: {student1.id} - 张三")

        student2 = await graph_service.create_node(
            NodeType.STUDENT,
            {
                "student_id": "S002",
                "name": "李四",
                "grade": "4",
            }
        )
        print(f"创建学生节点: {student2.id} - 李四")

        # 创建教师节点
        teacher = await graph_service.create_node(
            NodeType.TEACHER,
            {
                "teacher_id": "T001",
                "name": "王老师",
                "subject": "数学",
            }
        )
        print(f"创建教师节点: {teacher.id} - 王老师")

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
        print(f"创建课程节点: {course.id} - 高等数学")

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
        print(f"创建知识点节点: {kp1.id} - 微积分")

        kp2 = await graph_service.create_node(
            NodeType.KNOWLEDGE_POINT,
            {
                "knowledge_point_id": "KP002",
                "name": "线性代数",
                "description": "线性代数基础",
                "category": "数学",
            }
        )
        print(f"创建知识点节点: {kp2.id} - 线性代数")

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
        print(f"创建错误类型节点: {error_type.id} - 计算错误")

        # 创建关系
        print("\n创建关系...")

        # 学生学习课程
        await graph_service.create_relationship(
            from_node_id=student1.id,
            to_node_id=course.id,
            relationship_type=RelationshipType.LEARNS,
            properties={
                "enrollment_date": datetime.utcnow(),
                "progress": 50.0,
            }
        )
        print("- 学生1 学习 高等数学")

        # 课程包含知识点
        await graph_service.create_relationship(
            from_node_id=course.id,
            to_node_id=kp1.id,
            relationship_type=RelationshipType.CONTAINS,
            properties={
                "order": 1,
                "importance": "core",
            }
        )
        print("- 高等数学 包含 微积分")

        await graph_service.create_relationship(
            from_node_id=course.id,
            to_node_id=kp2.id,
            relationship_type=RelationshipType.CONTAINS,
            properties={
                "order": 2,
                "importance": "supplementary",
            }
        )
        print("- 高等数学 包含 线性代数")

        # 学生互动
        await graph_service.create_relationship(
            from_node_id=student1.id,
            to_node_id=student2.id,
            relationship_type=RelationshipType.CHAT_WITH,
            properties={
                "message_count": 10,
                "last_interaction_date": datetime.utcnow(),
            }
        )
        print("- 学生1 与 学生2 聊天互动")

        # 教师教学
        await graph_service.create_relationship(
            from_node_id=teacher.id,
            to_node_id=student1.id,
            relationship_type=RelationshipType.TEACHES,
            properties={
                "interaction_count": 5,
                "last_interaction_date": datetime.utcnow(),
            }
        )
        print("- 王老师 教学 学生1")

        # 学生错误
        await graph_service.create_relationship(
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
        print("- 学生1 有 计算错误")

        # 错误关联知识点
        await graph_service.create_relationship(
            from_node_id=error_type.id,
            to_node_id=kp1.id,
            relationship_type=RelationshipType.RELATES_TO,
            properties={
                "strength": 0.8,
                "confidence": 0.9,
            }
        )
        print("- 计算错误 关联 微积分")

        print("\n模拟数据生成成功！")
        print("\n生成的节点:")
        print(f"- 学生: {student1.id}, {student2.id}")
        print(f"- 教师: {teacher.id}")
        print(f"- 课程: {course.id}")
        print(f"- 知识点: {kp1.id}, {kp2.id}")
        print(f"- 错误类型: {error_type.id}")
        print(f"\n可以使用根节点 ID {student1.id} 进行可视化查询")

    finally:
        # 关闭数据库连接
        await close_database()


if __name__ == "__main__":
    asyncio.run(generate_sample_data())