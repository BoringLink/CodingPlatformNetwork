#!/usr/bin/env python3
"""
数据重构脚本：用于重构Neo4j图数据库中的数据，确保所有数据符合规范要求
"""

import random
import uuid
from datetime import datetime
from neo4j import GraphDatabase
from faker import Faker

# 初始化Faker，用于生成真实姓名
fake = Faker('zh_CN')

# Neo4j数据库连接信息
URI = "bolt://localhost:7687"
AUTH = ("neo4j", "password")

# 定义节点类型和数量分布
NODE_COUNTS = {
    "Student": 30,
    "Teacher": 10,
    "Course": 15,
    "KnowledgePoint": 35,
    "ErrorType": 10
}

# 定义知识点列表（中小学Python编程教育相关）
KNOWLEDGE_POINTS = [
    {"name": "Python基础语法", "description": "变量、数据类型、运算符等基础知识", "category": "基础"},
    {"name": "控制流", "description": "条件语句、循环语句等流程控制", "category": "基础"},
    {"name": "函数", "description": "函数定义、参数、返回值等", "category": "基础"},
    {"name": "列表", "description": "列表的创建、访问、修改和常用方法", "category": "数据结构"},
    {"name": "字典", "description": "字典的创建、访问、修改和常用方法", "category": "数据结构"},
    {"name": "元组", "description": "元组的创建、访问和特性", "category": "数据结构"},
    {"name": "集合", "description": "集合的创建、访问、修改和常用方法", "category": "数据结构"},
    {"name": "字符串操作", "description": "字符串的常用方法和操作", "category": "基础"},
    {"name": "面向对象编程", "description": "类、对象、继承、多态等", "category": "进阶"},
    {"name": "模块和包", "description": "Python模块的导入和使用", "category": "进阶"},
    {"name": "异常处理", "description": "try-except语句和异常类型", "category": "进阶"},
    {"name": "文件操作", "description": "文件的读写和处理", "category": "进阶"},
    {"name": "循环嵌套", "description": "for循环和while循环的嵌套使用", "category": "基础"},
    {"name": "条件表达式", "description": "if-elif-else语句的使用", "category": "基础"},
    {"name": "函数参数", "description": "位置参数、关键字参数、默认参数等", "category": "基础"},
    {"name": "递归函数", "description": "递归函数的定义和使用", "category": "进阶"},
    {"name": "列表推导式", "description": "列表推导式的语法和应用", "category": "进阶"},
    {"name": "字典推导式", "description": "字典推导式的语法和应用", "category": "进阶"},
    {"name": "lambda表达式", "description": "lambda匿名函数的使用", "category": "进阶"},
    {"name": "map函数", "description": "map函数的使用和应用场景", "category": "进阶"},
    {"name": "filter函数", "description": "filter函数的使用和应用场景", "category": "进阶"},
    {"name": "reduce函数", "description": "reduce函数的使用和应用场景", "category": "进阶"},
    {"name": "生成器", "description": "生成器的定义和使用", "category": "进阶"},
    {"name": "迭代器", "description": "迭代器的定义和使用", "category": "进阶"},
    {"name": "装饰器", "description": "装饰器的定义和使用", "category": "高级"},
    {"name": "上下文管理器", "description": "with语句和上下文管理器", "category": "高级"},
    {"name": "正则表达式", "description": "正则表达式的语法和应用", "category": "高级"},
    {"name": "面向对象三大特性", "description": "封装、继承、多态", "category": "进阶"},
    {"name": "类方法和静态方法", "description": "类方法、静态方法的定义和使用", "category": "进阶"},
    {"name": "属性装饰器", "description": "@property装饰器的使用", "category": "进阶"},
    {"name": "异常类的定义", "description": "自定义异常类的定义和使用", "category": "高级"},
    {"name": "文件上下文管理器", "description": "使用with语句操作文件", "category": "进阶"},
    {"name": "二进制文件操作", "description": "二进制文件的读写操作", "category": "进阶"},
    {"name": "CSV文件操作", "description": "CSV文件的读写操作", "category": "进阶"}
]

# 定义错误类型列表
ERROR_TYPES = [
    {"name": "语法错误", "description": "Python语法不符合规范", "severity": "high"},
    {"name": "逻辑错误", "description": "程序运行结果不符合预期", "severity": "medium"},
    {"name": "运行时错误", "description": "程序运行过程中发生的错误", "severity": "high"},
    {"name": "类型错误", "description": "操作对象的类型不符合要求", "severity": "medium"},
    {"name": "名称错误", "description": "使用了未定义的变量或函数名", "severity": "high"},
    {"name": "索引错误", "description": "索引超出序列范围", "severity": "medium"},
    {"name": "属性错误", "description": "访问了对象不存在的属性", "severity": "medium"},
    {"name": "文件错误", "description": "文件操作相关错误", "severity": "high"},
    {"name": "导入错误", "description": "模块导入相关错误", "severity": "high"},
    {"name": "内存错误", "description": "内存不足导致的错误", "severity": "high"}
]

# 定义课程列表
COURSES = [
    {"name": "Python入门编程", "description": "适合零基础学生的Python入门课程", "difficulty": "beginner"},
    {"name": "Python进阶编程", "description": "适合有基础的学生的Python进阶课程", "difficulty": "intermediate"},
    {"name": "Python数据结构", "description": "Python数据结构和算法课程", "difficulty": "intermediate"},
    {"name": "Python面向对象编程", "description": "Python面向对象编程课程", "difficulty": "intermediate"},
    {"name": "Python项目实战", "description": "Python项目实战课程", "difficulty": "advanced"},
    {"name": "Python网络编程", "description": "Python网络编程课程", "difficulty": "advanced"},
    {"name": "Python数据分析", "description": "Python数据分析课程", "difficulty": "intermediate"},
    {"name": "Python爬虫开发", "description": "Python爬虫开发课程", "difficulty": "advanced"},
    {"name": "Python自动化测试", "description": "Python自动化测试课程", "difficulty": "intermediate"},
    {"name": "Python游戏开发", "description": "Python游戏开发课程", "difficulty": "intermediate"},
    {"name": "Python人工智能", "description": "Python人工智能入门课程", "difficulty": "advanced"},
    {"name": "Python Web开发", "description": "Python Web开发课程", "difficulty": "advanced"},
    {"name": "Python数据库编程", "description": "Python数据库编程课程", "difficulty": "intermediate"},
    {"name": "Python运维自动化", "description": "Python运维自动化课程", "difficulty": "advanced"},
    {"name": "Python科学计算", "description": "Python科学计算课程", "difficulty": "intermediate"}
]

# 生成5分制随机评分（0-5之间的整数）
def generate_rating() -> int:
    return random.randint(0, 5)

# 生成百分比随机值（0-1之间的浮点数）
def generate_percentage() -> float:
    return round(random.uniform(0, 1), 2)

# 生成整数随机值（指定范围内）
def generate_integer(min_val: int, max_val: int) -> int:
    return random.randint(min_val, max_val)

# 生成学生节点属性（极简版，仅包含Neo4j支持的基本类型）
def generate_student_properties(student_id: str, name: str) -> dict:
    return {
        "id": str(uuid.uuid4()),
        "student_id": student_id,
        "name": name,
        "age": random.randint(12, 18),
        "gender": random.choice(["male", "female", "other"]),
        "school": random.choice(["第一中学", "第二中学", "第三中学", "实验中学", "外国语学校", "第四中学", "第五中学", "第六中学"]),
        "grade": random.choice(["初一", "初二", "初三", "高一", "高二", "高三"])
    }

# 生成教师节点属性
def generate_teacher_properties(teacher_id: str, name: str) -> dict:
    return {
        "id": str(uuid.uuid4()),
        "teacher_id": teacher_id,
        "name": name,
        "subject": "Python编程"
    }

# 执行数据重构
def reconstruct_data():
    """执行数据重构：删除所有现有节点和关系，然后生成新的数据"""
    
    # 连接Neo4j数据库
    driver = GraphDatabase.driver(URI, auth=AUTH)
    
    try:
        with driver.session() as session:
            # 1. 删除所有现有节点和关系
            print("正在删除所有现有节点和关系...")
            session.run("MATCH (n) DETACH DELETE n")
            print("现有节点和关系删除完成")
            
            # 2. 生成新的节点
            
            # 生成学生节点
            print("正在生成学生节点...")
            student_names = set()
            students = []
            for i in range(NODE_COUNTS["Student"]):
                while True:
                    name = fake.name()
                    if name not in student_names:
                        student_names.add(name)
                        break
                student_id = f"student_{i+1:03d}"
                properties = generate_student_properties(student_id, name)
                session.run(
                    "CREATE (s:Student $properties)",
                    properties=properties
                )
                students.append(student_id)
            print(f"学生节点生成完成，共{len(students)}个")
            
            # 生成教师节点
            print("正在生成教师节点...")
            teacher_names = set()
            teachers = []
            for i in range(NODE_COUNTS["Teacher"]):
                while True:
                    name = fake.name()
                    if name not in teacher_names:
                        teacher_names.add(name)
                        break
                teacher_id = f"teacher_{i+1:03d}"
                properties = generate_teacher_properties(teacher_id, name)
                session.run(
                    "CREATE (t:Teacher $properties)",
                    properties=properties
                )
                teachers.append(teacher_id)
            print(f"教师节点生成完成，共{len(teachers)}个")
            
            # 生成课程节点
            print("正在生成课程节点...")
            courses = []
            for i, course in enumerate(COURSES[:NODE_COUNTS["Course"]]):
                course_id = f"course_{i+1:03d}"
                properties = {
                    "id": str(uuid.uuid4()),
                    "course_id": course_id,
                    "name": course["name"],
                    "description": course["description"],
                    "difficulty": course["difficulty"]
                }
                session.run(
                    "CREATE (c:Course $properties)",
                    properties=properties
                )
                courses.append(course_id)
            print(f"课程节点生成完成，共{len(courses)}个")
            
            # 生成知识点节点
            print("正在生成知识点节点...")
            knowledge_points = []
            for i, kp in enumerate(KNOWLEDGE_POINTS[:NODE_COUNTS["KnowledgePoint"]]):
                kp_id = f"kp_{i+1:03d}"
                properties = {
                    "id": str(uuid.uuid4()),
                    "knowledge_point_id": kp_id,
                    "name": kp["name"],
                    "description": kp["description"],
                    "category": kp["category"]
                }
                session.run(
                    "CREATE (k:KnowledgePoint $properties)",
                    properties=properties
                )
                knowledge_points.append(kp_id)
            print(f"知识点节点生成完成，共{len(knowledge_points)}个")
            
            # 生成错误类型节点
            print("正在生成错误类型节点...")
            error_types = []
            for i, et in enumerate(ERROR_TYPES[:NODE_COUNTS["ErrorType"]]):
                et_id = f"error_{i+1:03d}"
                properties = {
                    "id": str(uuid.uuid4()),
                    "error_type_id": et_id,
                    "name": et["name"],
                    "description": et["description"],
                    "severity": et["severity"]
                }
                session.run(
                    "CREATE (e:ErrorType $properties)",
                    properties=properties
                )
                error_types.append(et_id)
            print(f"错误类型节点生成完成，共{len(error_types)}个")
            
            # 3. 生成关系
            
            # 生成TEACHES关系：教师教授课程
            print("正在生成TEACHES关系...")
            for course_id in courses:
                # 每个课程由1-2个教师教授
                teachers_for_course = random.sample(teachers, random.randint(1, 2))
                for teacher_id in teachers_for_course:
                    session.run(
                        "MATCH (t:Teacher {teacher_id: $teacher_id}), (c:Course {course_id: $course_id}) "
                        "CREATE (t)-[:TEACHES]->(c)",
                        teacher_id=teacher_id,
                        course_id=course_id
                    )
            print("TEACHES关系生成完成")
            
            # 生成LEARNS关系：学生学习课程
            print("正在生成LEARNS关系...")
            for student_id in students:
                # 每个学生学习3-5门课程
                courses_for_student = random.sample(courses, random.randint(3, 5))
                for course_id in courses_for_student:
                    session.run(
                        "MATCH (s:Student {student_id: $student_id}), (c:Course {course_id: $course_id}) "
                        "CREATE (s)-[:LEARNS]->(c)",
                        student_id=student_id,
                        course_id=course_id
                    )
            print("LEARNS关系生成完成")
            
            # 生成CONTAINS关系：课程包含知识点
            print("正在生成CONTAINS关系...")
            for course_id in courses:
                # 每个课程包含5-8个知识点
                kps_for_course = random.sample(knowledge_points, random.randint(5, 8))
                for kp_id in kps_for_course:
                    session.run(
                        "MATCH (c:Course {course_id: $course_id}), (k:KnowledgePoint {knowledge_point_id: $kp_id}) "
                        "CREATE (c)-[:CONTAINS]->(k)",
                        course_id=course_id,
                        kp_id=kp_id
                    )
            print("CONTAINS关系生成完成")
            
            # 生成CHAT_WITH关系：学生与教师聊天
            print("正在生成CHAT_WITH关系...")
            for student_id in students:
                # 每个学生与2-4个教师聊天
                teachers_for_student = random.sample(teachers, random.randint(2, 4))
                for teacher_id in teachers_for_student:
                    session.run(
                        "MATCH (s:Student {student_id: $student_id}), (t:Teacher {teacher_id: $teacher_id}) "
                        "CREATE (s)-[:CHAT_WITH]->(t)",
                        student_id=student_id,
                        teacher_id=teacher_id
                    )
            print("CHAT_WITH关系生成完成")
            
            # 生成HAS_ERROR关系：学生产生错误
            print("正在生成HAS_ERROR关系...")
            for student_id in students:
                # 每个学生产生3-6个错误
                errors_for_student = random.sample(error_types, random.randint(3, 6))
                for error_id in errors_for_student:
                    session.run(
                        "MATCH (s:Student {student_id: $student_id}), (e:ErrorType {error_type_id: $error_id}) "
                        "CREATE (s)-[:HAS_ERROR]->(e)",
                        student_id=student_id,
                        error_id=error_id
                    )
            print("HAS_ERROR关系生成完成")
            
            # 生成RELATES_TO关系：错误与知识点相关
            print("正在生成RELATES_TO关系...")
            for error_id in error_types:
                # 每个错误与2-4个知识点相关
                kps_for_error = random.sample(knowledge_points, random.randint(2, 4))
                for kp_id in kps_for_error:
                    session.run(
                        "MATCH (e:ErrorType {error_type_id: $error_id}), (k:KnowledgePoint {knowledge_point_id: $kp_id}) "
                        "CREATE (e)-[:RELATES_TO]->(k)",
                        error_id=error_id,
                        kp_id=kp_id
                    )
            print("RELATES_TO关系生成完成")
            
            # 生成LIKES关系：学生喜欢知识点
            print("正在生成LIKES关系...")
            for student_id in students:
                # 每个学生喜欢3-5个知识点
                liked_kps = random.sample(knowledge_points, random.randint(3, 5))
                for kp_id in liked_kps:
                    session.run(
                        "MATCH (s:Student {student_id: $student_id}), (k:KnowledgePoint {knowledge_point_id: $kp_id}) "
                        "CREATE (s)-[:LIKES]->(k)",
                        student_id=student_id,
                        kp_id=kp_id
                    )
            print("LIKES关系生成完成")
            
            # 4. 验证生成的数据
            print("正在验证生成的数据...")
            
            # 验证节点总数
            total_nodes = session.run("MATCH (n) RETURN COUNT(n) AS total").single()["total"]
            print(f"总节点数: {total_nodes}")
            
            # 验证各类型节点数量
            node_types = ["Student", "Teacher", "Course", "KnowledgePoint", "ErrorType"]
            for node_type in node_types:
                count = session.run(f"MATCH (n:{node_type}) RETURN COUNT(n) AS count").single()["count"]
                print(f"{node_type}节点数: {count}")
            
            # 验证关系总数
            total_relationships = session.run("MATCH ()-[r]->() RETURN COUNT(r) AS total").single()["total"]
            print(f"总关系数: {total_relationships}")
            
            # 验证错误节点与学生的关系
            error_student_relationships = session.run(
                "MATCH (s:Student)-[:HAS_ERROR]->(e:ErrorType) RETURN COUNT(DISTINCT e) AS count"
            ).single()["count"]
            print(f"与学生建立关系的错误类型节点数: {error_student_relationships}")
            
            # 验证是否存在孤立节点
            isolated_nodes = session.run(
                "MATCH (n) WHERE NOT (n)--() RETURN COUNT(n) AS count"
            ).single()["count"]
            print(f"孤立节点数: {isolated_nodes}")
            
            print("数据重构完成！")
            
    except Exception as e:
        print(f"数据重构过程中发生错误: {e}")
    finally:
        # 关闭数据库连接
        driver.close()

if __name__ == "__main__":
    reconstruct_data()
