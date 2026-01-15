"""检查数据库状态"""

from neo4j import GraphDatabase

driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "password"))

with driver.session() as session:
    # 查看孤立的 School 节点
    print("=== 孤立的 School 节点 ===")
    result = session.run("""
        MATCH (s:School)
        WHERE NOT (s)-[]-()
        RETURN s.id as id, s.name as name
    """)
    isolated_schools = [dict(r) for r in result]
    print(f"  共 {len(isolated_schools)} 个孤立 School")
    school_names = [s["name"] for s in isolated_schools[:5]]
    print(f"  示例: {school_names}")

    # 检查是否有学生/教师属于这些孤立的学校
    print("\n=== 检查是否有学生/教师属于孤立学校 ===")
    for school in isolated_schools[:3]:
        result = session.run(
            """
            MATCH (s:Student)
            WHERE s.basic_info_school = $school_name
            RETURN count(s) as cnt
        """,
            school_name=school["name"],
        )
        student_cnt = result.single()["cnt"]

        result = session.run(
            """
            MATCH (t:Teacher)
            WHERE t.basic_info_school = $school_name
            RETURN count(t) as cnt
        """,
            school_name=school["name"],
        )
        teacher_cnt = result.single()["cnt"]

        print(f"  学校 '{school['name']}': {student_cnt} 个学生, {teacher_cnt} 个教师")

    # 最终孤立节点统计
    print("\n=== 最终孤立节点统计 ===")
    result = session.run("""
        MATCH (n)
        WHERE NOT (n)-[]-()
        RETURN labels(n)[0] as label, count(*) as cnt
        ORDER BY cnt DESC
    """)
    for record in result:
        print(f"  {record['label']}: {record['cnt']}")

    # 只统计核心节点（Student, Teacher, KnowledgePoint）
    print("\n=== 核心节点（Student, Teacher, KnowledgePoint）孤立统计 ===")
    result = session.run("""
        MATCH (n)
        WHERE NOT (n)-[]-()
        AND labels(n)[0] IN ['Student', 'Teacher', 'KnowledgePoint']
        RETURN labels(n)[0] as label, count(*) as cnt
    """)
    has_isolated = False
    for record in result:
        has_isolated = True
        print(f"  {record['label']}: {record['cnt']}")
    if not has_isolated:
        print("  ✅ 没有孤立的核心节点！")

driver.close()
