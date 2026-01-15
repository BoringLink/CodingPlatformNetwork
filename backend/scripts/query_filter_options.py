"""查询数据库中的学校、年级、班级层级数据"""

from neo4j import GraphDatabase

driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "password"))

with driver.session() as session:
    # 使用 Student 节点的 basic_info_school 和 basic_info_grade
    print("=== 学校列表 (来自 Student.basic_info_school) ===")
    schools = session.run(
        "MATCH (s:Student) RETURN DISTINCT s.basic_info_school AS school ORDER BY school"
    ).data()
    for s in schools:
        print(f"  - {s['school']}")

    print("\n=== 年级列表 (来自 Student.basic_info_grade) ===")
    grades = session.run(
        "MATCH (s:Student) UNWIND s.basic_info_grade AS grade RETURN DISTINCT grade ORDER BY grade"
    ).data()
    for g in grades:
        print(f"  - {g['grade']}")

    # 检查是否有 School, Grade, Class 节点
    print("\n=== School 节点 ===")
    school_nodes = session.run("MATCH (s:School) RETURN s LIMIT 5").data()
    for s in school_nodes:
        print(f"  - {s['s']}")

    print("\n=== Grade 节点 ===")
    grade_nodes = session.run("MATCH (g:Grade) RETURN g LIMIT 5").data()
    for g in grade_nodes:
        print(f"  - {g['g']}")

    print("\n=== Class 节点 ===")
    class_nodes = session.run("MATCH (c:Class) RETURN c LIMIT 5").data()
    for c in class_nodes:
        print(f"  - {c['c']}")

driver.close()
