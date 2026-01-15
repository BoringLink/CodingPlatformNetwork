#!/usr/bin/env python3
"""
为学生节点添加 basic_info_class 属性

根据学生所在学校和年级，随机分配班级（1-5）
"""

import random
from neo4j import GraphDatabase

# 数据库连接配置
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "password"


def main():
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    
    with driver.session() as session:
        print("=" * 60)
        print("🎓 为学生节点添加 basic_info_class 属性")
        print("=" * 60)
        
        # 获取所有没有 basic_info_class 的学生
        result = session.run("""
            MATCH (s:Student)
            WHERE s.basic_info_class IS NULL
            RETURN s.id AS id, s.student_id AS student_id, 
                   s.basic_info_school AS school, s.basic_info_grade AS grade
        """)
        
        students = list(result)
        print(f"\n📊 发现 {len(students)} 个需要分配班级的学生")
        
        if len(students) == 0:
            print("✅ 所有学生已有班级信息")
            driver.close()
            return
        
        # 为每个学生分配班级
        updated_count = 0
        for student in students:
            student_id = student["id"]
            # 随机分配 1-5 班
            class_num = str(random.randint(1, 5))
            
            session.run("""
                MATCH (s:Student {id: $id})
                SET s.basic_info_class = $class_num
            """, {"id": student_id, "class_num": class_num})
            updated_count += 1
        
        print(f"✅ 已为 {updated_count} 个学生分配班级")
        
        # 验证
        verify = session.run("""
            MATCH (s:Student)
            WHERE s.basic_info_class IS NOT NULL
            RETURN s.basic_info_school AS school, s.basic_info_grade AS grade, 
                   s.basic_info_class AS class, count(*) AS count
            ORDER BY school, grade, class
            LIMIT 15
        """)
        
        print("\n📋 分配结果示例 (前15条):")
        for record in verify:
            grades = record['grade']
            grade_str = str(grades[0]) if isinstance(grades, list) and len(grades) > 0 else str(grades)
            print(f"   {record['school']} - {grade_str}年级 - {record['class']}班: {record['count']}人")
        
        # 统计
        stats = session.run("""
            MATCH (s:Student)
            WHERE s.basic_info_class IS NOT NULL
            RETURN count(s) AS total
        """).single()
        
        print(f"\n📈 已分配班级的学生总数: {stats['total']}")
        print("\n" + "=" * 60)
        print("✅ 完成!")
        print("=" * 60)
    
    driver.close()


if __name__ == "__main__":
    main()
