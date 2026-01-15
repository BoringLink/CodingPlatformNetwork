#!/usr/bin/env python3
"""
为孤立的 Teacher 节点创建 CHAT_WITH 关系

业务逻辑：
- School/Grade/Class 仅用于筛选，它们之间已有级联关系（HAS_GRADE, HAS_CLASS）
- 需要建立关系的节点只有 Student, Teacher, KnowledgePoint 三种
- Teacher 通过 CHAT_WITH 与 Student 交流
- 由于没有 KnowledgePoint 节点，Teacher 只能用 CHAT_WITH 连接 Student
"""

import random
from datetime import datetime, timedelta

from neo4j import GraphDatabase

# 连接数据库
driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "password"))


def get_isolated_teachers(session):
    """获取所有孤立的教师节点"""
    result = session.run("""
        MATCH (t:Teacher)
        WHERE NOT (t)-[]-()
        RETURN t.id as id, t.basic_info_school as school, t.basic_info_grade as grades
    """)
    return [dict(record) for record in result]


def get_students_by_school(session, school):
    """根据学校获取学生ID列表"""
    result = session.run(
        """
        MATCH (s:Student)
        WHERE s.basic_info_school = $school
        RETURN s.id as id
    """,
        school=school,
    )
    return [record["id"] for record in result]


def get_random_students(session, limit=100):
    """随机获取一些学生ID"""
    result = session.run(
        """
        MATCH (s:Student)
        RETURN s.id as id
        ORDER BY rand()
        LIMIT $limit
    """,
        limit=limit,
    )
    return [record["id"] for record in result]


def create_relationships_for_teacher(tx, teacher_id, student_ids):
    """为一个教师创建与学生的 CHAT_WITH 关系"""
    relationships_created = 0

    # 选择 3-8 个学生进行 CHAT_WITH（教师与学生交流）
    num_chats = min(random.randint(3, 8), len(student_ids))
    chat_partners = random.sample(student_ids, num_chats)

    for student_id in chat_partners:
        tx.run(
            """
            MATCH (t:Teacher {id: $teacher_id})
            MATCH (s:Student {id: $student_id})
            MERGE (t)-[r:CHAT_WITH]->(s)
            ON CREATE SET 
                r.message_count = $msg_count,
                r.last_interaction_date = $last_date
        """,
            teacher_id=teacher_id,
            student_id=student_id,
            msg_count=random.randint(10, 200),
            last_date=(datetime.now() - timedelta(days=random.randint(1, 30))).isoformat(),
        )
        relationships_created += 1

    return relationships_created


def main():
    with driver.session() as session:
        # 获取孤立教师
        isolated_teachers = get_isolated_teachers(session)
        print(f"发现 {len(isolated_teachers)} 个孤立的教师节点")

        if not isolated_teachers:
            print("没有孤立的教师节点")
            return

        # 预先获取一批随机学生（用于没有匹配学校的教师）
        fallback_students = get_random_students(session, 100)

        total_relationships = 0
        for i, teacher in enumerate(isolated_teachers):
            teacher_id = teacher["id"]
            school = teacher.get("school")

            # 优先选择同校学生
            student_ids = []
            if school:
                student_ids = get_students_by_school(session, school)

            # 如果同校学生不足，使用随机学生补充
            if len(student_ids) < 5:
                student_ids = fallback_students

            if not student_ids:
                print(f"警告: 教师 {teacher_id} 找不到可用的学生")
                continue

            with driver.session() as tx_session:
                count = tx_session.execute_write(
                    lambda tx, tid=teacher_id, sids=student_ids: create_relationships_for_teacher(
                        tx, tid, sids
                    )
                )
                total_relationships += count

            if (i + 1) % 50 == 0:
                print(f"已处理 {i + 1}/{len(isolated_teachers)}，创建 {total_relationships} 个关系")

        print(f"\n完成！已处理 {len(isolated_teachers)} 个教师，创建 {total_relationships} 个关系")

        # 验证是否还有孤立的教师节点
        remaining = get_isolated_teachers(session)
        print(f"剩余孤立教师节点: {len(remaining)}")

        # 检查所有孤立节点统计
        result = session.run("""
            MATCH (n)
            WHERE NOT (n)-[]-()
            RETURN labels(n)[0] as label, count(*) as cnt
        """)
        print("\n所有孤立节点统计:")
        for record in result:
            print(f"  {record['label']}: {record['cnt']}")


if __name__ == "__main__":
    main()
    driver.close()
