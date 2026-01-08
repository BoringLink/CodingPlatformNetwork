"""生成符合要求的真实测试数据"""

import asyncio
import logging
from datetime import datetime
from app.database import init_database, close_database, neo4j_connection

# 配置日志
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)


async def clear_database():
    """清空数据库中的所有节点和关系"""
    logger.info("正在清空数据库...")
    async with neo4j_connection.get_session() as session:
        await session.run("MATCH (n) DETACH DELETE n")
    logger.info("数据库清空完成")


async def create_nodes_and_relationships():
    """创建节点和关系"""
    logger.info("正在创建测试数据...")

    async with neo4j_connection.get_session() as session:
        # 创建错误类型节点
        error_types = [
            ("error_syntax", "语法错误", "代码编写不符合Python语法规则", "high"),
            ("error_logic", "逻辑错误", "代码逻辑不正确导致运行结果错误", "high"),
            ("error_runtime", "运行时错误", "程序运行过程中出现的错误", "high"),
            ("error_type", "类型错误", "操作对象的类型不符合预期", "medium"),
            ("error_name", "名称错误", "使用了未定义的变量或函数", "medium"),
            ("error_index", "索引错误", "访问列表/字典时使用了无效索引/键", "medium"),
            ("error_attribute", "属性错误", "访问对象不存在的属性", "medium"),
            ("error_file", "文件错误", "文件操作失败", "low"),
            ("error_import", "导入错误", "模块导入失败", "low"),
            ("error_memory", "内存错误", "程序使用了过多内存", "high"),
        ]

        for error_id, name, desc, severity in error_types:
            await session.run(
                "CREATE (et:ErrorType {error_type_id: $error_id, name: $name, description: $desc, severity: $severity})",
                error_id=error_id,
                name=name,
                desc=desc,
                severity=severity,
            )
        logger.info(f"创建了 {len(error_types)} 个错误类型节点")

        # 创建知识点节点（Python编程相关）
        knowledge_points = [
            (
                "kp_basic_syntax",
                "Python基础语法",
                "变量、数据类型、运算符等基础知识",
                "基础",
            ),
            ("kp_control_flow", "控制流", "条件语句、循环语句等流程控制", "基础"),
            ("kp_functions", "函数", "函数定义、参数、返回值等", "基础"),
            ("kp_data_structures", "数据结构", "列表、字典、元组、集合等", "基础"),
            ("kp_oop", "面向对象编程", "类、对象、继承、多态等", "中级"),
            ("kp_modules", "模块和包", "Python模块的导入和使用", "中级"),
            ("kp_exception", "异常处理", "try-except语句和异常类型", "中级"),
            ("kp_file_io", "文件操作", "文件的读写和处理", "中级"),
            ("kp_database", "数据库操作", "与数据库的交互", "高级"),
            ("kp_algorithms", "算法基础", "常见算法的Python实现", "高级"),
        ]

        for kp_id, name, desc, category in knowledge_points:
            await session.run(
                "CREATE (k:KnowledgePoint {knowledge_point_id: $kp_id, name: $name, description: $desc, category: $category})",
                kp_id=kp_id,
                name=name,
                desc=desc,
                category=category,
            )
        logger.info(f"创建了 {len(knowledge_points)} 个知识点节点")

        # 创建课程节点
        courses = [
            (
                "course_python_beginner",
                "Python编程入门",
                "适合零基础的Python入门课程",
                "beginner",
            ),
            (
                "course_python_intermediate",
                "Python编程进阶",
                "适合有一定基础的Python课程",
                "intermediate",
            ),
            (
                "course_python_advanced",
                "Python编程高级",
                "适合有较好基础的Python课程",
                "advanced",
            ),
            (
                "course_python_web",
                "Python Web开发",
                "使用Python进行Web应用开发",
                "intermediate",
            ),
            (
                "course_python_data_analysis",
                "Python数据分析",
                "使用Python进行数据分析和可视化",
                "intermediate",
            ),
            (
                "course_python_machine_learning",
                "Python机器学习",
                "Python机器学习基础与应用",
                "advanced",
            ),
            (
                "course_python_automation",
                "Python自动化测试",
                "使用Python进行自动化测试",
                "intermediate",
            ),
            (
                "course_python_django",
                "Django框架入门",
                "Python Web框架Django的使用",
                "intermediate",
            ),
            (
                "course_python_flask",
                "Flask框架入门",
                "Python轻量级Web框架Flask的使用",
                "beginner",
            ),
            (
                "course_python_data_structures",
                "Python数据结构与算法",
                "Python中的数据结构和算法实现",
                "advanced",
            ),
        ]

        for course_id, name, desc, difficulty in courses:
            await session.run(
                "CREATE (c:Course {course_id: $course_id, name: $name, description: $desc, difficulty: $difficulty})",
                course_id=course_id,
                name=name,
                desc=desc,
                difficulty=difficulty,
            )
        logger.info(f"创建了 {len(courses)} 个课程节点")

        # 创建教师节点（真实姓名）
        teachers = [
            ("teacher_li", "李晓明", "Python编程"),
            ("teacher_wang", "王芳", "数据结构"),
            ("teacher_zhang", "张伟", "算法设计"),
            ("teacher_chen", "陈静", "人工智能"),
            ("teacher_liu", "刘建国", "网络编程"),
            ("teacher_sun", "孙秀英", "Web开发"),
            ("teacher_zhou", "周建国", "数据分析"),
            ("teacher_wu", "吴敏", "机器学习"),
            ("teacher_xu", "徐磊", "自动化测试"),
            ("teacher_gao", "高翔", "框架开发"),
        ]

        for teacher_id, name, subject in teachers:
            await session.run(
                "CREATE (t:Teacher {teacher_id: $teacher_id, name: $name, subject: $subject})",
                teacher_id=teacher_id,
                name=name,
                subject=subject,
            )
        logger.info(f"创建了 {len(teachers)} 个教师节点")

        # 创建学生节点（真实姓名和详细信息）
        students = [
            (
                "student_001",
                "李明",
                18,
                "male",
                "北京大学",
                "大一",
                "2024-09-01",
                80,
                75,
                85,
                90,
                88,
            ),
            (
                "student_002",
                "王芳",
                19,
                "female",
                "清华大学",
                "大二",
                "2023-09-01",
                75,
                80,
                70,
                85,
                82,
            ),
            (
                "student_003",
                "张伟",
                17,
                "male",
                "复旦大学",
                "大一",
                "2024-09-01",
                85,
                88,
                75,
                80,
                90,
            ),
            (
                "student_004",
                "陈静",
                20,
                "female",
                "浙江大学",
                "大三",
                "2022-09-01",
                70,
                75,
                80,
                88,
                78,
            ),
            (
                "student_005",
                "刘建国",
                18,
                "male",
                "南京大学",
                "大一",
                "2024-09-01",
                88,
                90,
                82,
                85,
                92,
            ),
            (
                "student_006",
                "孙秀英",
                19,
                "female",
                "上海交通大学",
                "大二",
                "2023-09-01",
                72,
                78,
                85,
                75,
                80,
            ),
            (
                "student_007",
                "赵云飞",
                17,
                "male",
                "武汉大学",
                "大一",
                "2024-09-01",
                83,
                85,
                78,
                82,
                88,
            ),
            (
                "student_008",
                "杨丽",
                20,
                "female",
                "华中科技大学",
                "大三",
                "2022-09-01",
                68,
                72,
                78,
                85,
                75,
            ),
            (
                "student_009",
                "林俊杰",
                18,
                "male",
                "中山大学",
                "大一",
                "2024-09-01",
                90,
                88,
                85,
                92,
                95,
            ),
            (
                "student_010",
                "陈敏",
                19,
                "female",
                "四川大学",
                "大二",
                "2023-09-01",
                75,
                82,
                75,
                80,
                85,
            ),
        ]

        for (
            student_id,
            name,
            age,
            gender,
            school,
            grade,
            enrollment_date,
            elementary,
            junior_high,
            senior_high,
            university,
            professional,
        ) in students:

            await session.run(
                """
                CREATE (s:Student {
                    student_id: $student_id,
                    name: $name,
                    age: $age,
                    gender: $gender,
                    school: $school,
                    grade: $grade,
                    elementary_knowledge: $elementary,
                    junior_high_knowledge: $junior_high,
                    senior_high_knowledge: $senior_high,
                    university_knowledge: $university,
                    professional_knowledge: $professional,
                    enrollment_date: datetime($enrollment_date),
                    last_updated: datetime(),
                    created_at: datetime()
                })
                """,
                student_id=student_id,
                name=name,
                age=age,
                gender=gender,
                school=school,
                grade=grade,
                elementary=elementary,
                junior_high=junior_high,
                senior_high=senior_high,
                university=university,
                professional=professional,
                enrollment_date=enrollment_date,
            )
        logger.info(f"创建了 {len(students)} 个学生节点")

        # 建立关系

        # 1. 学生学习课程 (LEARNS)
        for i, (student_id, _, _, _, _, _, _, _, _, _, _, _) in enumerate(students):
            course_index = i % len(courses) + 1
            await session.run(
                "MATCH (s:Student {student_id: $student_id}), (c:Course) WHERE c.course_id ENDS WITH 'beginner' OR c.course_id ENDS WITH 'intermediate' MERGE (s)-[:LEARNS]->(c)",
                student_id=student_id,
            )
        logger.info("建立了学生-课程关系 (LEARNS)")

        # 2. 课程包含知识点 (CONTAINS)
        # 基础课程
        await session.run(
            """
            MATCH (c:Course {course_id: 'course_python_beginner'}), (k:KnowledgePoint)
            WHERE k.knowledge_point_id IN ['kp_basic_syntax', 'kp_control_flow', 'kp_functions', 'kp_data_structures']
            MERGE (c)-[:CONTAINS]->(k)
            """
        )

        # 进阶课程
        await session.run(
            """
            MATCH (c:Course {course_id: 'course_python_intermediate'}), (k:KnowledgePoint)
            WHERE k.knowledge_point_id IN ['kp_oop', 'kp_modules', 'kp_exception', 'kp_file_io']
            MERGE (c)-[:CONTAINS]->(k)
            """
        )

        # 高级课程
        await session.run(
            """
            MATCH (c:Course {course_id: 'course_python_advanced'}), (k:KnowledgePoint)
            WHERE k.knowledge_point_id IN ['kp_database', 'kp_algorithms']
            MERGE (c)-[:CONTAINS]->(k)
            """
        )

        # Web开发课程
        await session.run(
            """
            MATCH (c:Course {course_id: 'course_python_web'}), (k:KnowledgePoint)
            WHERE k.knowledge_point_id IN ['kp_basic_syntax', 'kp_functions', 'kp_data_structures', 'kp_file_io']
            MERGE (c)-[:CONTAINS]->(k)
            """
        )

        # 数据分析课程
        await session.run(
            """
            MATCH (c:Course {course_id: 'course_python_data_analysis'}), (k:KnowledgePoint)
            WHERE k.knowledge_point_id IN ['kp_basic_syntax', 'kp_data_structures', 'kp_file_io', 'kp_algorithms']
            MERGE (c)-[:CONTAINS]->(k)
            """
        )

        # 机器学习课程
        await session.run(
            """
            MATCH (c:Course {course_id: 'course_python_machine_learning'}), (k:KnowledgePoint)
            WHERE k.knowledge_point_id IN ['kp_data_structures', 'kp_algorithms', 'kp_file_io', 'kp_database']
            MERGE (c)-[:CONTAINS]->(k)
            """
        )

        # 自动化测试课程
        await session.run(
            """
            MATCH (c:Course {course_id: 'course_python_automation'}), (k:KnowledgePoint)
            WHERE k.knowledge_point_id IN ['kp_basic_syntax', 'kp_functions', 'kp_modules', 'kp_file_io']
            MERGE (c)-[:CONTAINS]->(k)
            """
        )

        # Django框架课程
        await session.run(
            """
            MATCH (c:Course {course_id: 'course_python_django'}), (k:KnowledgePoint)
            WHERE k.knowledge_point_id IN ['kp_basic_syntax', 'kp_functions', 'kp_oop', 'kp_modules']
            MERGE (c)-[:CONTAINS]->(k)
            """
        )

        # Flask框架课程
        await session.run(
            """
            MATCH (c:Course {course_id: 'course_python_flask'}), (k:KnowledgePoint)
            WHERE k.knowledge_point_id IN ['kp_basic_syntax', 'kp_functions', 'kp_modules']
            MERGE (c)-[:CONTAINS]->(k)
            """
        )

        # 数据结构与算法课程
        await session.run(
            """
            MATCH (c:Course {course_id: 'course_python_data_structures'}), (k:KnowledgePoint)
            WHERE k.knowledge_point_id IN ['kp_data_structures', 'kp_algorithms', 'kp_control_flow', 'kp_functions']
            MERGE (c)-[:CONTAINS]->(k)
            """
        )
        logger.info("建立了课程-知识点关系 (CONTAINS)")

        # 3. 教师教授课程 (TEACHES)
        # 为每位教师分配对应的课程
        await session.run(
            "MATCH (t:Teacher {teacher_id: 'teacher_li'}), (c:Course {course_id: 'course_python_beginner'}) MERGE (t)-[:TEACHES]->(c)"
        )

        await session.run(
            "MATCH (t:Teacher {teacher_id: 'teacher_wang'}), (c:Course {course_id: 'course_python_data_structures'}) MERGE (t)-[:TEACHES]->(c)"
        )

        await session.run(
            "MATCH (t:Teacher {teacher_id: 'teacher_zhang'}), (c:Course {course_id: 'course_python_advanced'}) MERGE (t)-[:TEACHES]->(c)"
        )

        await session.run(
            "MATCH (t:Teacher {teacher_id: 'teacher_chen'}), (c:Course {course_id: 'course_python_machine_learning'}) MERGE (t)-[:TEACHES]->(c)"
        )

        await session.run(
            "MATCH (t:Teacher {teacher_id: 'teacher_liu'}), (c:Course {course_id: 'course_python_web'}) MERGE (t)-[:TEACHES]->(c)"
        )

        await session.run(
            "MATCH (t:Teacher {teacher_id: 'teacher_sun'}), (c:Course {course_id: 'course_python_django'}) MERGE (t)-[:TEACHES]->(c)"
        )

        await session.run(
            "MATCH (t:Teacher {teacher_id: 'teacher_zhou'}), (c:Course {course_id: 'course_python_data_analysis'}) MERGE (t)-[:TEACHES]->(c)"
        )

        await session.run(
            "MATCH (t:Teacher {teacher_id: 'teacher_wu'}), (c:Course {course_id: 'course_python_machine_learning'}) MERGE (t)-[:TEACHES]->(c)"
        )

        await session.run(
            "MATCH (t:Teacher {teacher_id: 'teacher_xu'}), (c:Course {course_id: 'course_python_automation'}) MERGE (t)-[:TEACHES]->(c)"
        )

        await session.run(
            "MATCH (t:Teacher {teacher_id: 'teacher_gao'}), (c:Course {course_id: 'course_python_flask'}) MERGE (t)-[:TEACHES]->(c)"
        )

        # 为部分教师分配额外课程
        await session.run(
            "MATCH (t:Teacher {teacher_id: 'teacher_li'}), (c:Course {course_id: 'course_python_flask'}) MERGE (t)-[:TEACHES]->(c)"
        )

        await session.run(
            "MATCH (t:Teacher {teacher_id: 'teacher_wang'}), (c:Course {course_id: 'course_python_intermediate'}) MERGE (t)-[:TEACHES]->(c)"
        )
        logger.info("建立了教师-课程关系 (TEACHES)")

        # 4. 学生与教师交流 (CHAT_WITH)
        # 所有学生都与至少两位教师交流
        for i, (student_id, _, _, _, _, _, _, _, _, _, _, _) in enumerate(students):
            # 为每个学生分配两位不同的教师
            teacher1_index = i % len(teachers)
            teacher2_index = (i + 1) % len(teachers)
            teacher1_id = teachers[teacher1_index][0]
            teacher2_id = teachers[teacher2_index][0]

            await session.run(
                "MATCH (s:Student {student_id: $student_id}), (t:Teacher {teacher_id: $teacher_id}) MERGE (s)-[:CHAT_WITH]->(t)",
                student_id=student_id,
                teacher_id=teacher1_id,
            )

            await session.run(
                "MATCH (s:Student {student_id: $student_id}), (t:Teacher {teacher_id: $teacher_id}) MERGE (s)-[:CHAT_WITH]->(t)",
                student_id=student_id,
                teacher_id=teacher2_id,
            )
        logger.info("建立了学生-教师交流关系 (CHAT_WITH)")

        # 5. 学生学习知识点 (LEARNS)
        for i, (student_id, _, _, _, _, _, _, _, _, _, _, _) in enumerate(students):
            kp_index = i % len(knowledge_points)
            kp_id = knowledge_points[kp_index][0]
            await session.run(
                "MATCH (s:Student {student_id: $student_id}), (k:KnowledgePoint {knowledge_point_id: $kp_id}) MERGE (s)-[:LEARNS]->(k)",
                student_id=student_id,
                kp_id=kp_id,
            )
        logger.info("建立了学生-知识点关系 (LEARNS)")

        # 6. 知识点与错误类型相关 (HAS_ERROR)
        await session.run(
            """
            MATCH (k:KnowledgePoint {knowledge_point_id: 'kp_basic_syntax'}), (e:ErrorType)
            WHERE e.error_type_id IN ['error_syntax', 'error_name'] MERGE (k)-[:HAS_ERROR]->(e)
            """
        )

        await session.run(
            """
            MATCH (k:KnowledgePoint {knowledge_point_id: 'kp_control_flow'}), (e:ErrorType)
            WHERE e.error_type_id IN ['error_logic', 'error_type'] MERGE (k)-[:HAS_ERROR]->(e)
            """
        )

        await session.run(
            """
            MATCH (k:KnowledgePoint {knowledge_point_id: 'kp_data_structures'}), (e:ErrorType)
            WHERE e.error_type_id IN ['error_index', 'error_attribute'] MERGE (k)-[:HAS_ERROR]->(e)
            """
        )
        logger.info("建立了知识点-错误类型关系 (HAS_ERROR)")

        # 7. 知识点之间的关联 (RELATES_TO)
        related_pairs = [
            ("kp_basic_syntax", "kp_control_flow"),
            ("kp_control_flow", "kp_functions"),
            ("kp_functions", "kp_data_structures"),
            ("kp_data_structures", "kp_oop"),
            ("kp_oop", "kp_modules"),
            ("kp_modules", "kp_exception"),
            ("kp_exception", "kp_file_io"),
            ("kp_file_io", "kp_database"),
            ("kp_database", "kp_algorithms"),
        ]

        for kp1, kp2 in related_pairs:
            await session.run(
                "MATCH (k1:KnowledgePoint {knowledge_point_id: $kp1}), (k2:KnowledgePoint {knowledge_point_id: $kp2}) MERGE (k1)-[:RELATES_TO]->(k2)",
                kp1=kp1,
                kp2=kp2,
            )
        logger.info("建立了知识点之间的关联关系 (RELATES_TO)")

    logger.info("测试数据创建完成")


async def verify_data():
    """验证数据创建情况"""
    logger.info("\n=== 数据验证 ===")

    async with neo4j_connection.get_session() as session:
        # 统计各类型节点数量
        node_types = ["Student", "Teacher", "Course", "KnowledgePoint", "ErrorType"]
        for node_type in node_types:
            result = await session.run(
                f"MATCH (n:{node_type}) RETURN count(n) AS count"
            )
            record = await result.single()
            logger.info(f"{node_type} 节点数量: {record['count']}")

        # 统计关系数量
        result = await session.run(
            "MATCH ()-[r]->() RETURN type(r) AS type, count(r) AS count"
        )
        logger.info("\n关系数量统计:")
        async for record in result:
            logger.info(f"{record['type']}: {record['count']}")

    logger.info("\n=== 验证完成 ===")


async def main():
    """主函数"""
    try:
        # 初始化数据库连接
        await init_database()

        # 清空数据库
        await clear_database()

        # 创建节点和关系
        await create_nodes_and_relationships()

        # 验证数据
        await verify_data()

    except Exception as e:
        logger.error(f"生成测试数据时发生错误: {e}", exc_info=True)
    finally:
        # 关闭数据库连接
        await close_database()


if __name__ == "__main__":
    asyncio.run(main())
