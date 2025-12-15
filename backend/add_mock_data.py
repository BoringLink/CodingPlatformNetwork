#!/usr/bin/env python3
"""
向数据库中添加模拟数据的脚本
"""

import asyncio
from datetime import datetime
from app.models.nodes import NodeType
from app.models.relationships import RelationshipType
from app.services.graph_service import GraphManagementService


async def add_mock_data():
    """添加模拟数据到数据库中"""
    print("=" * 60)
    print("向数据库中添加模拟数据")
    print("=" * 60)

    # 创建GraphManagementService实例
    graph_service = GraphManagementService()

    try:
        # 1. 创建学生节点
        print("\n1. 创建学生节点...")
        students = []
        for i in range(5):
            student = await graph_service.create_node(
                node_type=NodeType.STUDENT,
                properties={
                    "student_id": f"S{i+1:03d}",
                    "name": f"学生{i+1}",
                    "grade": f"{i+1}年级",
                    "age": 12 + i,
                    "gender": "男" if i % 2 == 0 else "女",
                },
            )
            students.append(student)
            print(f"   ✓ 创建学生: {student.properties['name']} (ID: {student.id})")

        # 2. 创建教师节点
        print("\n2. 创建教师节点...")
        teachers = []
        for i in range(3):
            teacher = await graph_service.create_node(
                node_type=NodeType.TEACHER,
                properties={
                    "teacher_id": f"T{i+1:03d}",
                    "name": f"教师{i+1}",
                    "subject": ["数学", "语文", "英语"][i],
                    "experience": 5 + i,
                },
            )
            teachers.append(teacher)
            print(f"   ✓ 创建教师: {teacher.properties['name']} (ID: {teacher.id})")

        # 3. 创建课程节点
        print("\n3. 创建课程节点...")
        courses = []
        course_names = ["数学基础", "语文阅读", "英语写作", "物理实验", "化学入门"]
        for i, course_name in enumerate(course_names):
            course = await graph_service.create_node(
                node_type=NodeType.COURSE,
                properties={
                    "course_id": f"C{i+1:03d}",
                    "name": course_name,
                    "credit": 2 + (i % 2),
                    "duration": 30,
                },
            )
            courses.append(course)
            print(f"   ✓ 创建课程: {course.properties['name']} (ID: {course.id})")

        # 4. 创建知识点节点
        print("\n4. 创建知识点节点...")
        knowledge_points = []
        kp_data = [
            ("数学", "代数", "数学的基础分支，研究数、数量、关系和结构"),
            ("数学", "几何", "研究空间、形状、大小和相对位置的学科"),
            ("数学", "函数", "描述变量之间对应关系的数学概念"),
            ("数学", "概率", "研究随机现象数量规律的数学分支"),
            ("数学", "统计", "收集、分析、解释和呈现数据的学科"),
            ("语文", "阅读理解", "对书面材料的理解和分析能力"),
            ("语文", "写作技巧", "提高写作质量和表达效果的方法"),
            ("语文", "语法", "语言的结构规则和使用规范"),
            ("语文", "修辞", "提高语言表达效果的修辞手法"),
            ("语文", "文言文", "古代汉语的书面形式"),
            ("英语", "语法结构", "英语语言的结构规则"),
            ("英语", "词汇", "英语语言的单词和短语"),
            ("英语", "听力", "理解英语口语的能力"),
            ("英语", "口语", "用英语进行口头表达的能力"),
            ("英语", "写作", "用英语进行书面表达的能力"),
        ]

        for i, (subject, kp_name, description) in enumerate(kp_data):
            kp = await graph_service.create_node(
                node_type=NodeType.KNOWLEDGE_POINT,
                properties={
                    "knowledge_point_id": f"KP{i+1:03d}",
                    "name": kp_name,
                    "description": description,
                    "category": subject,
                },
            )
            knowledge_points.append(kp)
            print(f"   ✓ 创建知识点: {kp.properties['name']} (ID: {kp.id})")

        # 5. 创建错误类型节点
        print("\n5. 创建错误类型节点...")
        error_types = []
        error_data = [
            ("计算错误", "学生在数学计算过程中出现的错误", "high"),
            ("概念理解错误", "对数学概念或原理理解不准确导致的错误", "high"),
            ("逻辑推理错误", "在推理过程中逻辑不严谨或错误", "medium"),
            ("审题错误", "对题目理解不准确或遗漏关键信息", "medium"),
            ("书写错误", "书写不规范或笔误导致的错误", "low"),
        ]
        for i, (error_name, description, severity) in enumerate(error_data):
            error_type = await graph_service.create_node(
                node_type=NodeType.ERROR_TYPE,
                properties={
                    "error_type_id": f"ET{i+1:03d}",
                    "name": error_name,
                    "description": description,
                    "severity": severity,
                },
            )
            error_types.append(error_type)
            print(
                f"   ✓ 创建错误类型: {error_type.properties['name']} (ID: {error_type.id})"
            )

        # 6. 创建关系
        print("\n6. 创建关系...")

        # 学生-学习-课程关系
        for i, student in enumerate(students):
            for j, course in enumerate(courses[:3]):  # 每个学生学习3门课程
                if (i + j) % 2 == 0:  # 随机分配课程
                    await graph_service.create_relationship(
                        from_node_id=student.id,
                        to_node_id=course.id,
                        relationship_type=RelationshipType.LEARNS,
                        properties={
                            "progress": (i + j) * 20 % 100,  # 学习进度
                            "start_date": datetime.now().isoformat(),
                        },
                    )
                    print(
                        f"   ✓ 学生{student.properties['name']} - 学习 - {course.properties['name']}"
                    )

        # 教师-教授-课程关系
        for i, teacher in enumerate(teachers):
            for j, course in enumerate(courses[i::2]):  # 每个教师教授2门课程
                await graph_service.create_relationship(
                    from_node_id=teacher.id,
                    to_node_id=course.id,
                    relationship_type=RelationshipType.TEACHES,
                    properties={
                        "classroom": f"{i+1}0{j+1}教室",
                        "semester": "2024春季",
                    },
                )
                print(
                    f"   ✓ 教师{teacher.properties['name']} - 教授 - {course.properties['name']}"
                )

        # 课程-包含-知识点关系
        for i, course in enumerate(courses):
            for j, kp in enumerate(
                knowledge_points[i * 2 : (i + 1) * 2]
            ):  # 每门课程包含2个知识点
                await graph_service.create_relationship(
                    from_node_id=course.id,
                    to_node_id=kp.id,
                    relationship_type=RelationshipType.CONTAINS,
                    properties={
                        "importance": "core" if j == 0 else "supplementary",
                        "difficulty": kp.properties["difficulty"],
                    },
                )
                print(
                    f"   ✓ 课程{course.properties['name']} - 包含 - 知识点{kp.properties['name']}"
                )

        # 学生-错误-错误类型关系
        for i, student in enumerate(students):
            for j, error_type in enumerate(error_types[:2]):  # 每个学生有2种错误类型
                await graph_service.create_relationship(
                    from_node_id=student.id,
                    to_node_id=error_type.id,
                    relationship_type=RelationshipType.HAS_ERROR,
                    properties={
                        "occurrence_count": i + j + 1,
                        "first_occurrence": datetime.now().isoformat(),
                        "last_occurrence": datetime.now().isoformat(),
                        "course_id": courses[i % len(courses)].properties["course_id"],
                        "resolved": False,
                    },
                )
                print(
                    f"   ✓ 学生{student.properties['name']} - 错误 - {error_type.properties['name']}"
                )

        # 错误类型-关联-知识点关系
        for i, error_type in enumerate(error_types):
            for j, kp in enumerate(knowledge_points[i::2]):  # 每个错误类型关联2个知识点
                await graph_service.create_relationship(
                    from_node_id=error_type.id,
                    to_node_id=kp.id,
                    relationship_type=RelationshipType.RELATES_TO,
                    properties={
                        "strength": 0.7 + (i % 3) * 0.1,
                        "confidence": 0.8 + (j % 2) * 0.1,
                    },
                )
                print(
                    f"   ✓ 错误类型{error_type.properties['name']} - 关联 - 知识点{kp.properties['name']}"
                )

        # 学生-聊天-学生关系
        for i in range(len(students) - 1):
            if i % 2 == 0:  # 随机创建聊天关系
                await graph_service.create_relationship(
                    from_node_id=students[i].id,
                    to_node_id=students[i + 1].id,
                    relationship_type=RelationshipType.CHAT_WITH,
                    properties={
                        "message_count": (i + 1) * 5,
                        "last_chat_time": datetime.now().isoformat(),
                        "interaction_level": "high" if i < 2 else "medium",
                    },
                )
                print(
                    f"   ✓ 学生{students[i].properties['name']} - 聊天 - 学生{students[i+1].properties['name']}"
                )

        # 学生-点赞-学生关系
        for i in range(len(students)):
            if i % 3 == 0:  # 随机创建点赞关系
                for j in range(i + 1, min(i + 3, len(students))):
                    await graph_service.create_relationship(
                        from_node_id=students[i].id,
                        to_node_id=students[j].id,
                        relationship_type=RelationshipType.LIKES,
                        properties={
                            "like_count": 1,
                            "timestamp": datetime.now().isoformat(),
                        },
                    )
                    print(
                        f"   ✓ 学生{students[i].properties['name']} - 点赞 - 学生{students[j].properties['name']}"
                    )

        print("\n" + "=" * 60)
        print("模拟数据添加完成！")
        print("=" * 60)
        print("添加的数据统计:")
        print(f"   - 学生节点: {len(students)}个")
        print(f"   - 教师节点: {len(teachers)}个")
        print(f"   - 课程节点: {len(courses)}个")
        print(f"   - 知识点节点: {len(knowledge_points)}个")
        print(f"   - 错误类型节点: {len(error_types)}个")
        print("=" * 60)

    except Exception as e:
        print(f"\n添加模拟数据时出错: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(add_mock_data())
