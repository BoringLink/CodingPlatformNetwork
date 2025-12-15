#!/usr/bin/env python3
"""检查数据库中是否存在数据"""

import asyncio
from app.database import init_database, close_database, neo4j_connection


async def check_data():
    """检查数据库中是否存在数据"""
    try:
        # 初始化数据库连接
        await init_database()
        print("数据库连接成功")

        # 查询节点数量
        async with neo4j_connection.get_session() as session:
            result = await session.run("MATCH (n) RETURN COUNT(n) AS node_count")
            record = await result.single()
            node_count = record["node_count"] if record else 0
            print(f"数据库中节点数量: {node_count}")

            if node_count > 0:
                # 查询学生节点
                student_result = await session.run("MATCH (s:Student) RETURN s.id AS id, s.name AS name LIMIT 5")
                student_records = await student_result.data()
                print("\n学生节点:")
                for record in student_records:
                    print(f"  - ID: {record['id']}, 姓名: {record['name']}")

                # 查询教师节点
                teacher_result = await session.run("MATCH (t:Teacher) RETURN t.id AS id, t.name AS name LIMIT 5")
                teacher_records = await teacher_result.data()
                print("\n教师节点:")
                for record in teacher_records:
                    print(f"  - ID: {record['id']}, 姓名: {record['name']}")

                # 查询课程节点
                course_result = await session.run("MATCH (c:Course) RETURN c.id AS id, c.name AS name LIMIT 5")
                course_records = await course_result.data()
                print("\n课程节点:")
                for record in course_records:
                    print(f"  - ID: {record['id']}, 名称: {record['name']}")

                # 查询所有节点类型
                node_types_result = await session.run("MATCH (n) RETURN DISTINCT labels(n) AS labels")
                node_types_records = await node_types_result.data()
                print("\n节点类型:")
                for record in node_types_records:
                    print(f"  - {record['labels']}")

    finally:
        # 关闭数据库连接
        await close_database()


if __name__ == "__main__":
    asyncio.run(check_data())