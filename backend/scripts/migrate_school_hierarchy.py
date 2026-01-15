"""
数据迁移脚本：创建 School-Grade-Class 层级结构

从 Student 和 Teacher 节点的属性中提取学校、年级、班级信息，
创建独立的 School、Grade、Class 节点，并建立级联关系。

节点结构：
  - School: {id: UUID, name: str}
  - Grade: {id: UUID, level: int, school_id: UUID}
  - Class: {id: UUID, name: str, grade_id: UUID}

关系结构：
  School -[:HAS_GRADE]-> Grade -[:HAS_CLASS]-> Class

使用方法：
  cd backend
  source .venv/bin/activate
  python scripts/migrate_school_hierarchy.py
"""

import os
import sys
import uuid
from collections import defaultdict

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv
from neo4j import GraphDatabase

# 加载环境变量
load_dotenv()

# 数据库连接配置
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")


def get_driver():
    """创建数据库连接"""
    return GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))


def analyze_current_data(session):
    """分析当前数据库中的学校、年级、班级数据"""
    print("\n" + "=" * 60)
    print("📊 分析当前数据...")
    print("=" * 60)

    # 统计 Student 节点中的学校、年级、班级
    student_stats = session.run("""
        MATCH (s:Student)
        WHERE s.basic_info_school IS NOT NULL
        RETURN 
            s.basic_info_school AS school,
            s.basic_info_grade AS grade,
            s.basic_info_class AS class,
            count(*) AS count
        ORDER BY school, grade, class
    """).data()

    # 统计 Teacher 节点中的学校信息
    teacher_stats = session.run("""
        MATCH (t:Teacher)
        WHERE t.school IS NOT NULL OR t.basic_info_school IS NOT NULL
        RETURN 
            COALESCE(t.school, t.basic_info_school) AS school,
            count(*) AS count
        ORDER BY school
    """).data()

    # 构建层级结构: {school: {grade: {class1, class2, ...}}}
    hierarchy = defaultdict(lambda: defaultdict(set))

    for row in student_stats:
        school = row["school"]
        grade = row["grade"]
        class_name = row.get("class")

        if school:
            if grade is not None:
                # 处理 grade 可能是列表的情况
                grades = grade if isinstance(grade, list) else [grade]
                for g in grades:
                    if g is not None:
                        if class_name:
                            hierarchy[school][g].add(class_name)
                        else:
                            # 有年级但无班级，用占位符
                            hierarchy[school][g].add("__NO_CLASS__")
            else:
                hierarchy[school][None] = set()

    # 添加教师的学校
    for row in teacher_stats:
        school = row["school"]
        if school and school not in hierarchy:
            hierarchy[school] = defaultdict(set)

    # 打印统计信息
    print(f"\n📌 发现 {len(hierarchy)} 所学校:")
    total_grades = 0
    total_classes = 0

    for school in sorted(hierarchy.keys()):
        grades = hierarchy[school]
        grade_count = len([g for g in grades.keys() if g is not None])
        class_count = sum(
            len([c for c in classes if c != "__NO_CLASS__"]) for classes in grades.values()
        )
        total_grades += grade_count
        total_classes += class_count

        print(f"\n  🏫 {school}")
        for grade in sorted([g for g in grades.keys() if g is not None]):
            classes = grades[grade]
            valid_classes = sorted([c for c in classes if c and c != "__NO_CLASS__"])
            if valid_classes:
                print(f"      📚 {grade}年级: {valid_classes}")
            else:
                print(f"      📚 {grade}年级: (无班级数据)")

    print("\n📈 统计汇总:")
    print(f"   - 学校总数: {len(hierarchy)}")
    print(f"   - 年级总数: {total_grades}")
    print(f"   - 班级总数: {total_classes}")

    return hierarchy


def clean_existing_hierarchy(session):
    """清理现有的 School、Grade、Class 节点和关系"""
    print("\n" + "=" * 60)
    print("🧹 清理现有层级结构...")
    print("=" * 60)

    # 删除关系
    result = session.run("""
        MATCH ()-[r:HAS_GRADE|HAS_CLASS]->()
        DELETE r
        RETURN count(r) AS deleted_rels
    """).single()
    print(f"   删除 HAS_GRADE/HAS_CLASS 关系: {result['deleted_rels']} 条")

    # 删除现有节点
    for label in ["Class", "Grade", "School"]:
        result = session.run(f"""
            MATCH (n:{label})
            DETACH DELETE n
            RETURN count(n) AS deleted
        """).single()
        print(f"   删除 {label} 节点: {result['deleted']} 个")


def create_constraints_and_indexes(session):
    """创建唯一性约束和索引"""
    print("\n" + "=" * 60)
    print("📇 创建约束和索引...")
    print("=" * 60)

    constraints = [
        ("school_id_unique", "School", "id"),
        ("grade_id_unique", "Grade", "id"),
        ("class_id_unique", "Class", "id"),
    ]

    for name, label, prop in constraints:
        try:
            session.run(f"""
                CREATE CONSTRAINT {name} IF NOT EXISTS 
                FOR (n:{label}) REQUIRE n.{prop} IS UNIQUE
            """)
            print(f"   ✓ 创建约束: {label}.{prop} UNIQUE")
        except Exception as e:
            print(f"   ⚠ 约束 {name} 创建失败或已存在: {e}")

    indexes = [
        ("School", "name"),
        ("Grade", "level"),
        ("Grade", "school_id"),
        ("Class", "name"),
        ("Class", "grade_id"),
    ]

    for label, prop in indexes:
        try:
            session.run(f"CREATE INDEX IF NOT EXISTS FOR (n:{label}) ON (n.{prop})")
            print(f"   ✓ 创建索引: {label}.{prop}")
        except Exception as e:
            print(f"   ⚠ 索引 {label}.{prop} 创建失败: {e}")


def create_hierarchy(session, hierarchy):
    """创建 School-Grade-Class 层级结构"""
    print("\n" + "=" * 60)
    print("🏗️  创建新的层级结构...")
    print("=" * 60)

    school_count = 0
    grade_count = 0
    class_count = 0

    # 存储 ID 映射，用于建立关系
    school_ids = {}  # {school_name: school_id}
    grade_ids = {}  # {(school_name, grade_level): grade_id}

    # 1. 创建 School 节点
    print("\n   创建 School 节点...")
    for school_name in sorted(hierarchy.keys()):
        if not school_name:
            continue

        school_id = str(uuid.uuid4())
        school_ids[school_name] = school_id

        session.run(
            """
            CREATE (s:School {
                id: $id,
                name: $name,
                created_at: datetime()
            })
        """,
            {"id": school_id, "name": school_name},
        )
        school_count += 1

    print(f"      ✓ 创建 {school_count} 个 School 节点")

    # 2. 创建 Grade 节点并关联到 School
    print("\n   创建 Grade 节点...")
    for school_name in sorted(hierarchy.keys()):
        if not school_name:
            continue

        school_id = school_ids[school_name]
        grades = hierarchy[school_name]

        for grade_level in sorted([g for g in grades.keys() if g is not None]):
            grade_id = str(uuid.uuid4())
            grade_ids[(school_name, grade_level)] = grade_id

            session.run(
                """
                MATCH (s:School {id: $school_id})
                CREATE (g:Grade {
                    id: $grade_id,
                    level: $level,
                    school_id: $school_id,
                    created_at: datetime()
                })
                CREATE (s)-[:HAS_GRADE]->(g)
            """,
                {"school_id": school_id, "grade_id": grade_id, "level": grade_level},
            )
            grade_count += 1

    print(f"      ✓ 创建 {grade_count} 个 Grade 节点")

    # 3. 创建 Class 节点并关联到 Grade
    print("\n   创建 Class 节点...")
    for school_name in sorted(hierarchy.keys()):
        if not school_name:
            continue

        grades = hierarchy[school_name]

        for grade_level in sorted([g for g in grades.keys() if g is not None]):
            grade_id = grade_ids.get((school_name, grade_level))
            if not grade_id:
                continue

            classes = grades[grade_level]
            for class_name in sorted([c for c in classes if c and c != "__NO_CLASS__"]):
                class_id = str(uuid.uuid4())

                session.run(
                    """
                    MATCH (g:Grade {id: $grade_id})
                    CREATE (c:Class {
                        id: $class_id,
                        name: $name,
                        grade_id: $grade_id,
                        created_at: datetime()
                    })
                    CREATE (g)-[:HAS_CLASS]->(c)
                """,
                    {"grade_id": grade_id, "class_id": class_id, "name": class_name},
                )
                class_count += 1

    print(f"      ✓ 创建 {class_count} 个 Class 节点")

    print("\n✅ 层级结构创建完成:")
    print(f"   - School 节点: {school_count} 个")
    print(f"   - Grade 节点: {grade_count} 个")
    print(f"   - Class 节点: {class_count} 个")

    return school_count, grade_count, class_count


def verify_hierarchy(session):
    """验证层级结构是否正确创建"""
    print("\n" + "=" * 60)
    print("🔍 验证层级结构...")
    print("=" * 60)

    # 验证 School 节点
    schools = session.run("MATCH (s:School) RETURN count(s) AS count").single()
    print(f"   School 节点数: {schools['count']}")

    # 验证 Grade 节点和关系
    grades = session.run("""
        MATCH (s:School)-[:HAS_GRADE]->(g:Grade)
        RETURN count(DISTINCT g) AS count
    """).single()
    print(f"   Grade 节点数 (已关联): {grades['count']}")

    # 验证 Class 节点和关系
    classes = session.run("""
        MATCH (g:Grade)-[:HAS_CLASS]->(c:Class)
        RETURN count(DISTINCT c) AS count
    """).single()
    print(f"   Class 节点数 (已关联): {classes['count']}")

    # 显示完整层级示例
    print("\n📋 层级结构示例 (前3所学校):")
    examples = session.run("""
        MATCH (s:School)
        WITH s ORDER BY s.name LIMIT 3
        OPTIONAL MATCH (s)-[:HAS_GRADE]->(g:Grade)
        OPTIONAL MATCH (g)-[:HAS_CLASS]->(c:Class)
        RETURN s.name AS school, 
               s.id AS school_id,
               collect(DISTINCT {level: g.level, id: g.id}) AS grades,
               collect(DISTINCT {name: c.name, id: c.id}) AS classes
        ORDER BY school
    """).data()

    for ex in examples:
        print(f"\n   🏫 {ex['school']} (id: {ex['school_id'][:8]}...)")
        grades = sorted(
            [g for g in ex["grades"] if g["level"] is not None], key=lambda x: x["level"]
        )
        for g in grades[:3]:
            print(f"      📚 {g['level']}年级 (id: {g['id'][:8]}...)")
        if len(grades) > 3:
            print(f"      ... 还有 {len(grades) - 3} 个年级")

        classes = [c for c in ex["classes"] if c["name"] is not None]
        if classes:
            print(f"      📝 班级: {[c['name'] for c in classes[:5]]}")
            if len(classes) > 5:
                print(f"         ... 还有 {len(classes) - 5} 个班级")


def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("🚀 School-Grade-Class 层级结构迁移脚本")
    print("=" * 60)
    print(f"数据库: {NEO4J_URI}")

    driver = get_driver()

    try:
        with driver.session() as session:
            # 1. 分析当前数据
            hierarchy = analyze_current_data(session)

            if not hierarchy:
                print("\n⚠️  未发现任何学校数据，跳过迁移")
                return

            # 2. 询问用户确认
            print("\n" + "-" * 60)
            user_input = input("是否继续执行迁移? (y/N): ").strip().lower()
            if user_input != "y":
                print("已取消迁移")
                return

            # 3. 清理现有结构
            clean_existing_hierarchy(session)

            # 4. 创建约束和索引
            create_constraints_and_indexes(session)

            # 5. 创建新的层级结构
            create_hierarchy(session, hierarchy)

            # 6. 验证结果
            verify_hierarchy(session)

            print("\n" + "=" * 60)
            print("✅ 迁移完成!")
            print("=" * 60)

    except Exception as e:
        print(f"\n❌ 迁移失败: {e}")
        import traceback

        traceback.print_exc()
        raise
    finally:
        driver.close()


if __name__ == "__main__":
    main()
