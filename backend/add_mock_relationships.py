#!/usr/bin/env python3
"""
向数据库中添加模拟关系数据的脚本
"""

import asyncio
from datetime import datetime
from app.models.nodes import NodeType
from app.models.relationships import RelationshipType
from app.services.graph_service import GraphManagementService
from app.services.query_service import query_service, NodeFilter

async def add_mock_relationships():
    """向数据库中添加模拟关系数据"""
    print("=" * 60)
    print("向数据库中添加模拟关系数据")
    print("=" * 60)
    
    # 创建GraphManagementService实例
    graph_service = GraphManagementService()
    
    try:
        # 获取所有已创建的节点
        print("\n1. 获取已创建的节点...")
        
        # 获取学生节点
        students = await query_service.query_nodes(NodeFilter(types=[NodeType.STUDENT]))
        print(f"   ✓ 找到 {len(students)} 个学生节点")
        
        # 获取教师节点
        teachers = await query_service.query_nodes(NodeFilter(types=[NodeType.TEACHER]))
        print(f"   ✓ 找到 {len(teachers)} 个教师节点")
        
        # 获取课程节点
        courses = await query_service.query_nodes(NodeFilter(types=[NodeType.COURSE]))
        print(f"   ✓ 找到 {len(courses)} 个课程节点")
        
        # 获取知识点节点
        knowledge_points = await query_service.query_nodes(NodeFilter(types=[NodeType.KNOWLEDGE_POINT]))
        print(f"   ✓ 找到 {len(knowledge_points)} 个知识点节点")
        
        # 获取错误类型节点
        error_types = await query_service.query_nodes(NodeFilter(types=[NodeType.ERROR_TYPE]))
        print(f"   ✓ 找到 {len(error_types)} 个错误类型节点")
        
        # 获取当前时间
        now = datetime.now().isoformat()
        
        # 2. 创建关系
        print("\n2. 创建关系...")
        
        # 学生-学习-课程关系
        print("\n   a. 学生-学习-课程关系...")
        for i, student in enumerate(students):
            for j, course in enumerate(courses[:3]):  # 每个学生学习3门课程
                if (i + j) % 2 == 0:  # 随机分配课程
                    await graph_service.create_relationship(
                        from_node_id=student.id,
                        to_node_id=course.id,
                        relationship_type=RelationshipType.LEARNS,
                        properties={
                            "enrollment_date": now,  # 注册日期（必填）
                            "progress": (i + j) * 20 % 100,  # 学习进度
                        }
                    )
                    print(f"      ✓ 学生{student.properties['name']} - 学习 - {course.properties['name']}")
        
        # 教师-教授-课程关系
        print("\n   b. 教师-教授-课程关系...")
        for i, teacher in enumerate(teachers):
            for j, course in enumerate(courses[i::2]):  # 每个教师教授2门课程
                await graph_service.create_relationship(
                    from_node_id=teacher.id,
                    to_node_id=course.id,
                    relationship_type=RelationshipType.TEACHES,
                    properties={
                        "interaction_count": 1,  # 互动次数（必填）
                        "last_interaction_date": now,  # 最后互动日期（必填）
                    }
                )
                print(f"      ✓ 教师{teacher.properties['name']} - 教授 - {course.properties['name']}")
        
        # 课程-包含-知识点关系
        print("\n   c. 课程-包含-知识点关系...")
        for i, course in enumerate(courses):
            for j, kp in enumerate(knowledge_points[i*2:(i+1)*2]):  # 每门课程包含2个知识点
                await graph_service.create_relationship(
                    from_node_id=course.id,
                    to_node_id=kp.id,
                    relationship_type=RelationshipType.CONTAINS,
                    properties={
                        "order": j + 1,
                        "importance": "core" if j == 0 else "supplementary",
                    }
                )
                print(f"      ✓ 课程{course.properties['name']} - 包含 - 知识点{kp.properties['name']}")
        
        # 学生-错误-错误类型关系
        print("\n   d. 学生-错误-错误类型关系...")
        for i, student in enumerate(students):
            for j, error_type in enumerate(error_types[:2]):  # 每个学生有2种错误类型
                course_id = courses[i % len(courses)].properties["course_id"]
                await graph_service.create_relationship(
                    from_node_id=student.id,
                    to_node_id=error_type.id,
                    relationship_type=RelationshipType.HAS_ERROR,
                    properties={
                        "occurrence_count": i + j + 1,  # 发生次数（必填）
                        "first_occurrence": now,  # 首次发生时间（必填）
                        "last_occurrence": now,  # 最后发生时间（必填）
                        "course_id": course_id,  # 课程ID（必填）
                        "resolved": False,  # 是否已解决
                    }
                )
                print(f"      ✓ 学生{student.properties['name']} - 错误 - {error_type.properties['name']}")
        
        # 错误类型-关联-知识点关系
        print("\n   e. 错误类型-关联-知识点关系...")
        for i, error_type in enumerate(error_types):
            for j, kp in enumerate(knowledge_points[i::2]):  # 每个错误类型关联2个知识点
                await graph_service.create_relationship(
                    from_node_id=error_type.id,
                    to_node_id=kp.id,
                    relationship_type=RelationshipType.RELATES_TO,
                    properties={
                        "strength": 0.7 + (i % 3) * 0.1,  # 关联强度（必填）
                        "confidence": 0.8 + (j % 2) * 0.1,  # 置信度（必填）
                    }
                )
                print(f"      ✓ 错误类型{error_type.properties['name']} - 关联 - 知识点{kp.properties['name']}")
        
        # 学生-聊天-学生关系
        print("\n   f. 学生-聊天-学生关系...")
        for i in range(len(students)-1):
            if i % 2 == 0:  # 随机创建聊天关系
                await graph_service.create_relationship(
                    from_node_id=students[i].id,
                    to_node_id=students[i+1].id,
                    relationship_type=RelationshipType.CHAT_WITH,
                    properties={
                        "message_count": (i+1) * 5,  # 消息数量
                        "last_interaction_date": now,  # 最后互动日期（必填）
                    }
                )
                print(f"      ✓ 学生{students[i].properties['name']} - 聊天 - 学生{students[i+1].properties['name']}")
        
        # 学生-点赞-学生关系
        print("\n   g. 学生-点赞-学生关系...")
        for i in range(len(students)):
            if i % 3 == 0:  # 随机创建点赞关系
                for j in range(i+1, min(i+3, len(students))):
                    await graph_service.create_relationship(
                        from_node_id=students[i].id,
                        to_node_id=students[j].id,
                        relationship_type=RelationshipType.LIKES,
                        properties={
                            "like_count": 1,  # 点赞数量
                            "last_like_date": now,  # 最后点赞日期（必填）
                        }
                    )
                    print(f"      ✓ 学生{students[i].properties['name']} - 点赞 - 学生{students[j].properties['name']}")
        
        print("\n" + "=" * 60)
        print("模拟关系数据添加完成！")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n添加模拟关系数据时出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(add_mock_relationships())