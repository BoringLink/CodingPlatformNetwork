#!/usr/bin/env python3
"""
为孤立节点创建合理的模拟关系（仅使用现有关系类型）

现有关系类型：
- CHAT_WITH: 学生之间聊天
- LIKES: 点赞互动
- TEACHES: 教师教授
- LEARNS: 学生学习知识点
- CONTAINS: 包含关系
- RELATES_TO: 知识点间关联
"""

import asyncio
import random
from datetime import datetime, timedelta

from neo4j import AsyncGraphDatabase

NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "password"


def random_date(days_ago_max=365):
    """生成随机的过去日期"""
    days = random.randint(1, days_ago_max)
    return (datetime.now() - timedelta(days=days)).isoformat()


async def analyze_database(session):
    """分析数据库结构"""
    print("=== 数据库分析 ===\n")

    r1 = await session.run(
        "MATCH (n) RETURN labels(n)[0] AS label, count(n) AS cnt ORDER BY cnt DESC"
    )
    print("节点类型统计:")
    node_counts = {}
    for rec in await r1.data():
        node_counts[rec["label"]] = rec["cnt"]
        print(f"  {rec['label']}: {rec['cnt']}")

    r2 = await session.run(
        "MATCH ()-[r]->() RETURN type(r) AS rel_type, count(r) AS cnt ORDER BY cnt DESC"
    )
    print("\n关系类型统计:")
    for rec in await r2.data():
        print(f"  {rec['rel_type']}: {rec['cnt']}")

    r3 = await session.run("""
        MATCH (n) WHERE NOT (n)--()
        RETURN labels(n)[0] AS label, count(n) AS cnt
    """)
    print("\n孤立节点统计:")
    isolated_counts = {}
    for rec in await r3.data():
        isolated_counts[rec["label"]] = rec["cnt"]
        print(f"  {rec['label']}: {rec['cnt']}")

    return node_counts, isolated_counts


async def get_isolated_nodes(session, label: str, limit: int = 1000):
    """获取指定类型的孤立节点"""
    result = await session.run(
        f"""
        MATCH (n:{label}) WHERE NOT (n)--()
        RETURN n.id AS id, n.name AS name, 
               n.basic_info_school AS school, 
               n.basic_info_grade AS grade,
               n.basic_info_class AS class
        LIMIT $limit
    """,
        limit=limit,
    )
    return await result.data()


async def get_connected_nodes(session, label: str, limit: int = 100):
    """获取有连接的节点"""
    result = await session.run(
        f"""
        MATCH (n:{label})-[r]-()
        WITH n, count(r) AS rel_count WHERE rel_count > 0
        RETURN DISTINCT n.id AS id, n.name AS name,
               n.basic_info_school AS school,
               n.basic_info_grade AS grade,
               n.basic_info_class AS class
        LIMIT $limit
    """,
        limit=limit,
    )
    return await result.data()


async def get_knowledge_points(session, limit: int = 100):
    """获取知识点节点"""
    result = await session.run(
        "MATCH (k:KnowledgePoint) RETURN k.id AS id, k.name AS name LIMIT $limit",
        limit=limit,
    )
    return await result.data()


async def get_teachers(session, limit: int = 50):
    """获取教师节点"""
    result = await session.run(
        "MATCH (t:Teacher) RETURN t.id AS id, t.name AS name LIMIT $limit",
        limit=limit,
    )
    return await result.data()


async def create_student_relationships(
    session, isolated_students, connected_students, knowledge_points, teachers
):
    """为孤立学生创建关系（仅使用现有关系类型）"""
    print(f"\n为 {len(isolated_students)} 个孤立学生创建关系...")
    total_created = 0
    batch_size = 50

    for i in range(0, len(isolated_students), batch_size):
        batch = isolated_students[i : i + batch_size]

        for student in batch:
            student_id = student["id"]
            student_school = student.get("school")
            student_grade = student.get("grade")

            # 1. 与其他学生建立 CHAT_WITH 关系（优先同校同年级）
            similar = [
                s
                for s in connected_students
                if s["id"] != student_id
                and (s.get("school") == student_school or s.get("grade") == student_grade)
            ]
            if not similar:
                similar = [s for s in connected_students if s["id"] != student_id]

            if similar:
                for target in random.sample(similar, min(2, len(similar))):
                    # CHAT_WITH 需要 message_count 和 last_interaction_date
                    await session.run(
                        """
                        MATCH (a {id: $from_id}), (b {id: $to_id})
                        MERGE (a)-[r:CHAT_WITH]->(b)
                        SET r.message_count = $msg_count,
                            r.last_interaction_date = datetime($last_date)
                    """,
                        from_id=student_id,
                        to_id=target["id"],
                        msg_count=random.randint(1, 50),
                        last_date=random_date(90),
                    )
                    total_created += 1

            # 2. 与知识点建立 LEARNS 关系
            if knowledge_points:
                for kp in random.sample(knowledge_points, min(2, len(knowledge_points))):
                    # LEARNS 需要 enrollment_date 和 progress
                    await session.run(
                        """
                        MATCH (a {id: $from_id}), (b {id: $to_id})
                        MERGE (a)-[r:LEARNS]->(b)
                        SET r.enrollment_date = datetime($enroll_date),
                            r.progress = $progress,
                            r.time_spent = $time_spent
                    """,
                        from_id=student_id,
                        to_id=kp["id"],
                        enroll_date=random_date(180),
                        progress=random.uniform(10.0, 100.0),
                        time_spent=random.randint(30, 500),
                    )
                    total_created += 1

            # 3. 可选：与其他学生建立 LIKES 关系
            if similar and random.random() > 0.5:
                target = random.choice(similar)
                await session.run(
                    """
                    MATCH (a {id: $from_id}), (b {id: $to_id})
                    MERGE (a)-[r:LIKES]->(b)
                    SET r.like_count = $like_count,
                        r.last_like_date = datetime($last_date)
                """,
                    from_id=student_id,
                    to_id=target["id"],
                    like_count=random.randint(1, 10),
                    last_date=random_date(30),
                )
                total_created += 1

        print(
            f"  已处理 {min(i + batch_size, len(isolated_students))}/{len(isolated_students)}，"
            f"创建 {total_created} 个关系"
        )

    return total_created


async def create_other_relationships(session, isolated_counts, knowledge_points, teachers):
    """为其他类型孤立节点创建关系"""
    total = 0

    # 处理孤立的知识点
    if isolated_counts.get("KnowledgePoint", 0) > 0:
        print("\n为孤立知识点创建关系...")
        result = await session.run(
            "MATCH (k:KnowledgePoint) WHERE NOT (k)--() RETURN k.id AS id LIMIT 500"
        )
        isolated_kps = await result.data()

        for kp in isolated_kps:
            # 与其他知识点建立 RELATES_TO 关系
            if knowledge_points:
                others = [k for k in knowledge_points if k["id"] != kp["id"]]
                if others:
                    target = random.choice(others)
                    await session.run(
                        """
                        MATCH (a {id: $from_id}), (b {id: $to_id})
                        MERGE (a)-[r:RELATES_TO]->(b)
                    """,
                        from_id=kp["id"],
                        to_id=target["id"],
                    )
                    total += 1

            # 让教师 TEACHES 这个知识点
            if teachers:
                teacher = random.choice(teachers)
                await session.run(
                    """
                    MATCH (t {id: $tid}), (k {id: $kid})
                    MERGE (t)-[r:TEACHES]->(k)
                    SET r.interaction_count = $count,
                        r.last_interaction_date = datetime($last_date)
                """,
                    tid=teacher["id"],
                    kid=kp["id"],
                    count=random.randint(1, 20),
                    last_date=random_date(60),
                )
                total += 1

        print(f"  为 {len(isolated_kps)} 个知识点创建了关系")

    # 处理孤立的教师
    if isolated_counts.get("Teacher", 0) > 0:
        print("\n为孤立教师创建关系...")
        result = await session.run(
            "MATCH (t:Teacher) WHERE NOT (t)--() RETURN t.id AS id LIMIT 100"
        )
        isolated_teachers = await result.data()

        for teacher in isolated_teachers:
            # 教师 TEACHES 知识点
            if knowledge_points:
                for kp in random.sample(knowledge_points, min(3, len(knowledge_points))):
                    await session.run(
                        """
                        MATCH (t {id: $tid}), (k {id: $kid})
                        MERGE (t)-[r:TEACHES]->(k)
                        SET r.interaction_count = $count,
                            r.last_interaction_date = datetime($last_date)
                    """,
                        tid=teacher["id"],
                        kid=kp["id"],
                        count=random.randint(5, 30),
                        last_date=random_date(30),
                    )
                    total += 1

        print(f"  为 {len(isolated_teachers)} 个教师创建了关系")

    return total


async def main():
    """主函数"""
    print("=" * 60)
    print("孤立节点关系创建脚本（仅使用现有关系类型）")
    print("关系类型: CHAT_WITH, LIKES, TEACHES, LEARNS, RELATES_TO")
    print("=" * 60)

    driver = AsyncGraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    async with driver.session() as session:
        node_counts, isolated_counts = await analyze_database(session)

        if sum(isolated_counts.values()) == 0:
            print("\n✅ 没有孤立节点")
            await driver.close()
            return

        connected_students = await get_connected_nodes(session, "Student", 200)
        knowledge_points = await get_knowledge_points(session, 100)
        teachers = await get_teachers(session, 50)

        print(
            f"\n可用节点: 学生{len(connected_students)}, "
            f"知识点{len(knowledge_points)}, 教师{len(teachers)}"
        )

        total = 0
        if isolated_counts.get("Student", 0) > 0:
            isolated = await get_isolated_nodes(session, "Student", 10000)
            total += await create_student_relationships(
                session, isolated, connected_students, knowledge_points, teachers
            )

        total += await create_other_relationships(
            session, isolated_counts, knowledge_points, teachers
        )

        # 验证
        r = await session.run(
            "MATCH (n) WHERE NOT (n)--() RETURN labels(n)[0] AS label, count(n) AS cnt"
        )
        remaining = [rec for rec in await r.data() if rec["cnt"] > 0]

        print(f"\n{'=' * 60}")
        if not remaining:
            print("✅ 所有节点都已连接")
        else:
            print("剩余孤立节点:", remaining)
        print(f"总共创建 {total} 个关系")

    await driver.close()


if __name__ == "__main__":
    asyncio.run(main())
