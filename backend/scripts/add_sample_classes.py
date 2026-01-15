#!/usr/bin/env python3
"""
添加示例班级数据脚本

为现有的 Grade 节点添加 1-5 班级，用于测试级联筛选功能
"""

import uuid

from neo4j import GraphDatabase

# 数据库连接配置
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "password"


def main():
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

    with driver.session() as session:
        print("=" * 60)
        print("🏫 添加示例班级数据")
        print("=" * 60)

        # 获取所有 Grade 节点
        result = session.run("""
            MATCH (s:School)-[:HAS_GRADE]->(g:Grade)
            RETURN s.name AS school, g.id AS grade_id, g.level AS grade_level
            ORDER BY s.name, g.level
        """)

        grades = list(result)
        print(f"\n📊 发现 {len(grades)} 个年级节点")

        # 为每个年级创建 1-5 班级
        class_count = 0
        for grade in grades:
            school = grade["school"]
            grade_id = grade["grade_id"]
            grade_level = grade["grade_level"]

            for class_num in range(1, 6):  # 1-5 班
                class_id = str(uuid.uuid4())
                class_name = str(class_num)

                session.run(
                    """
                    MATCH (g:Grade {id: $grade_id})
                    MERGE (c:Class {name: $class_name, grade_id: $grade_id})
                    ON CREATE SET c.id = $class_id
                    MERGE (g)-[:HAS_CLASS]->(c)
                """,
                    {"grade_id": grade_id, "class_id": class_id, "class_name": class_name},
                )
                class_count += 1

        print(f"✅ 创建 {class_count} 个班级节点 (每个年级 5 个班)")

        # 验证
        verify = session.run("""
            MATCH (s:School)-[:HAS_GRADE]->(g:Grade)-[:HAS_CLASS]->(c:Class)
            RETURN s.name AS school, g.level AS grade, c.name AS class
            ORDER BY s.name, g.level, toInteger(c.name)
            LIMIT 15
        """)

        print("\n📋 示例数据 (前15条):")
        for record in verify:
            print(f"   {record['school']} - {record['grade']}年级 - {record['class']}班")

        # 统计
        stats = session.run("""
            MATCH (c:Class)
            RETURN count(c) AS total_classes
        """).single()

        print(f"\n📈 班级总数: {stats['total_classes']}")
        print("\n" + "=" * 60)
        print("✅ 完成!")
        print("=" * 60)

    driver.close()


if __name__ == "__main__":
    main()
