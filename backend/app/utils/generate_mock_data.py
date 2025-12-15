#!/usr/bin/env python3
"""生成模拟数据并导入到Neo4j图数据库中"""

import asyncio
import random
from datetime import datetime
from uuid import uuid4

from app.database import neo4j_connection
from app.models.nodes import NodeType
from app.models.relationships import RelationshipType

# 生成随机ID
def generate_id(prefix: str = "") -> str:
    """生成带前缀的随机ID"""
    return f"{prefix}{uuid4().hex[:8]}"

async def generate_mock_data():
    """生成模拟数据并导入到Neo4j"""
    async with neo4j_connection.get_session() as session:
        # 1. 创建学生节点
        students = []
        for i in range(5):
            student_id = generate_id("s")
            student = {
                "id": student_id,
                "name": f"学生{i+1}",
                "student_id": f"STU{i+1:03d}",
                "grade": random.choice(["一年级", "二年级", "三年级", "四年级", "五年级"]),
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
            students.append(student)
            await session.run(
                "CREATE (s:Student $props)",
                props=student
            )
        print(f"创建了 {len(students)} 个学生节点")

        # 2. 创建教师节点
        teachers = []
        for i in range(2):
            teacher_id = generate_id("t")
            teacher = {
                "id": teacher_id,
                "name": f"教师{i+1}",
                "teacher_id": f"TEA{i+1:02d}",
                "subject": random.choice(["数学", "语文", "英语", "科学"]),
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
            teachers.append(teacher)
            await session.run(
                "CREATE (t:Teacher $props)",
                props=teacher
            )
        print(f"创建了 {len(teachers)} 个教师节点")

        # 3. 创建课程节点
        courses = []
        for i in range(3):
            course_id = generate_id("c")
            course = {
                "id": course_id,
                "name": f"课程{i+1}",
                "course_id": f"COURSE{i+1:02d}",
                "description": f"这是第{i+1}门课程",
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
            courses.append(course)
            await session.run(
                "CREATE (c:Course $props)",
                props=course
            )
        print(f"创建了 {len(courses)} 个课程节点")

        # 4. 创建知识点节点
        knowledge_points = []
        for i in range(6):
            kp_id = generate_id("kp")
            kp = {
                "id": kp_id,
                "name": f"知识点{i+1}",
                "knowledge_point_id": f"KP{i+1:03d}",
                "difficulty": random.choice(["简单", "中等", "困难"]),
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
            knowledge_points.append(kp)
            await session.run(
                "CREATE (kp:KnowledgePoint $props)",
                props=kp
            )
        print(f"创建了 {len(knowledge_points)} 个知识点节点")

        # 5. 创建错误类型节点
        error_types = []
        for i in range(4):
            et_id = generate_id("et")
            et = {
                "id": et_id,
                "name": f"错误类型{i+1}",
                "error_type_id": f"ET{i+1:03d}",
                "description": f"这是第{i+1}种错误类型",
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
            error_types.append(et)
            await session.run(
                "CREATE (et:ErrorType $props)",
                props=et
            )
        print(f"创建了 {len(error_types)} 个错误类型节点")

        # 6. 创建关系
        # 教师教授课程 (TEACHES)
        for teacher in teachers:
            # 每个教师教授1-2门课程
            taught_courses = random.sample(courses, k=random.randint(1, 2))
            for course in taught_courses:
                await session.run(
                    "MATCH (t:Teacher {id: $teacher_id}), (c:Course {id: $course_id}) "
                    "CREATE (t)-[r:TEACHES {weight: $weight}]->(c)",
                    teacher_id=teacher["id"],
                    course_id=course["id"],
                    weight=random.uniform(0.5, 1.0)
                )
        print("创建了 TEACHES 关系")

        # 学生学习课程 (LEARNS)
        for student in students:
            # 每个学生学习2-3门课程
            learned_courses = random.sample(courses, k=random.randint(2, 3))
            for course in learned_courses:
                await session.run(
                    "MATCH (s:Student {id: $student_id}), (c:Course {id: $course_id}) "
                    "CREATE (s)-[r:LEARNS {weight: $weight}]->(c)",
                    student_id=student["id"],
                    course_id=course["id"],
                    weight=random.uniform(0.3, 0.9)
                )
        print("创建了 LEARNS 关系")

        # 学生与教师聊天 (CHAT_WITH)
        for student in students:
            # 每个学生与1-2个教师聊天
            chatted_teachers = random.sample(teachers, k=random.randint(1, 2))
            for teacher in chatted_teachers:
                await session.run(
                    "MATCH (s:Student {id: $student_id}), (t:Teacher {id: $teacher_id}) "
                    "CREATE (s)-[r:CHAT_WITH {weight: $weight}]->(t)",
                    student_id=student["id"],
                    teacher_id=teacher["id"],
                    weight=random.uniform(0.1, 0.8)
                )
        print("创建了 CHAT_WITH 关系")

        # 课程包含知识点 (CONTAINS)
        for course in courses:
            # 每门课程包含2-3个知识点
            contained_kps = random.sample(knowledge_points, k=random.randint(2, 3))
            for kp in contained_kps:
                await session.run(
                    "MATCH (c:Course {id: $course_id}), (kp:KnowledgePoint {id: $kp_id}) "
                    "CREATE (c)-[r:CONTAINS {weight: $weight}]->(kp)",
                    course_id=course["id"],
                    kp_id=kp["id"],
                    weight=random.uniform(0.5, 1.0)
                )
        print("创建了 CONTAINS 关系")

        # 学生在知识点上有错误 (HAS_ERROR)
        for student in students:
            # 每个学生有2-4个错误
            error_count = random.randint(2, 4)
            for _ in range(error_count):
                kp = random.choice(knowledge_points)
                et = random.choice(error_types)
                await session.run(
                    "MATCH (s:Student {id: $student_id}), (kp:KnowledgePoint {id: $kp_id}), (et:ErrorType {id: $et_id}) "
                    "CREATE (s)-[r:HAS_ERROR {weight: $weight}]->(kp), "
                    "CREATE (s)-[r2:HAS_ERROR {weight: $weight}]->(et)",
                    student_id=student["id"],
                    kp_id=kp["id"],
                    et_id=et["id"],
                    weight=random.uniform(0.2, 0.7)
                )
        print("创建了 HAS_ERROR 关系")

        # 知识点之间的关联 (RELATES_TO)
        for i, kp in enumerate(knowledge_points):
            # 每个知识点关联1-2个其他知识点
            other_kps = random.sample(knowledge_points[:i] + knowledge_points[i+1:], k=random.randint(1, 2))
            for other_kp in other_kps:
                await session.run(
                    "MATCH (kp1:KnowledgePoint {id: $kp1_id}), (kp2:KnowledgePoint {id: $kp2_id}) "
                    "CREATE (kp1)-[r:RELATES_TO {weight: $weight}]->(kp2)",
                    kp1_id=kp["id"],
                    kp2_id=other_kp["id"],
                    weight=random.uniform(0.3, 0.8)
                )
        print("创建了 RELATES_TO 关系")

        # 7. 学生点赞教师 (LIKES)
        for student in students:
            # 每个学生点赞1-2个教师
            liked_teachers = random.sample(teachers, k=random.randint(1, 2))
            for teacher in liked_teachers:
                await session.run(
                    "MATCH (s:Student {id: $student_id}), (t:Teacher {id: $teacher_id}) "
                    "CREATE (s)-[r:LIKES {weight: $weight}]->(t)",
                    student_id=student["id"],
                    teacher_id=teacher["id"],
                    weight=random.uniform(0.1, 1.0)
                )
        print("创建了 LIKES 关系")

        print("所有模拟数据生成完成！")

if __name__ == "__main__":
    asyncio.run(generate_mock_data())
