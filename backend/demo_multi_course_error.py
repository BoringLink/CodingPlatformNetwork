"""演示多课程多错误处理功能

这个脚本展示了如何使用新实现的多课程多错误处理功能。

注意：需要先启动 Neo4j 数据库才能运行此脚本。
运行命令：docker-compose up neo4j -d
"""

import asyncio
from datetime import datetime

from app.database import init_database, close_database
from app.services.graph_service import graph_service
from app.models.nodes import NodeType


async def demo_multi_course_error_handling():
    """演示多课程多错误处理功能"""
    
    print("=" * 60)
    print("多课程多错误处理功能演示")
    print("=" * 60)
    
    # 初始化数据库连接
    print("\n1. 初始化数据库连接...")
    await init_database()
    print("✓ 数据库连接成功")
    
    try:
        # 创建测试数据
        print("\n2. 创建测试节点...")
        
        # 创建学生
        student = await graph_service.create_node(
            NodeType.STUDENT,
            {"student_id": "DEMO_S001", "name": "张三"}
        )
        print(f"✓ 创建学生节点: {student.properties['name']} (ID: {student.id})")
        
        # 创建错误类型
        error_type = await graph_service.create_node(
            NodeType.ERROR_TYPE,
            {
                "error_type_id": "DEMO_E001",
                "name": "概念理解错误",
                "description": "对基本概念理解不正确",
                "severity": "medium",
            }
        )
        print(f"✓ 创建错误类型节点: {error_type.properties['name']} (ID: {error_type.id})")
        
        # 创建知识点
        kp1 = await graph_service.create_node(
            NodeType.KNOWLEDGE_POINT,
            {
                "knowledge_point_id": "DEMO_KP001",
                "name": "微积分基础",
                "description": "微积分的基本概念",
            }
        )
        print(f"✓ 创建知识点节点: {kp1.properties['name']} (ID: {kp1.id})")
        
        kp2 = await graph_service.create_node(
            NodeType.KNOWLEDGE_POINT,
            {
                "knowledge_point_id": "DEMO_KP002",
                "name": "导数定义",
                "description": "导数的基本定义",
            }
        )
        print(f"✓ 创建知识点节点: {kp2.properties['name']} (ID: {kp2.id})")
        
        # 创建课程
        course1 = await graph_service.create_node(
            NodeType.COURSE,
            {"course_id": "DEMO_C001", "name": "高等数学A"}
        )
        print(f"✓ 创建课程节点: {course1.properties['name']} (ID: {course1.id})")
        
        course2 = await graph_service.create_node(
            NodeType.COURSE,
            {"course_id": "DEMO_C002", "name": "高等数学B"}
        )
        print(f"✓ 创建课程节点: {course2.properties['name']} (ID: {course2.id})")
        
        # 演示功能 1: 创建学生多课程错误记录
        print("\n3. 演示功能 1: 创建学生多课程错误记录")
        print("-" * 60)
        
        # 在课程 A 中创建错误记录
        result1 = await graph_service.create_student_multi_course_error(
            student_id="DEMO_S001",
            error_type_id="DEMO_E001",
            course_id="DEMO_C001",
            occurrence_time=datetime(2024, 1, 10),
            knowledge_point_ids=["DEMO_KP001", "DEMO_KP002"],
        )
        print(f"✓ 在课程 {course1.properties['name']} 中创建错误记录")
        print(f"  - 是否为新记录: {result1['is_new']}")
        print(f"  - 发生次数: {result1['relationship'].properties['occurrence_count']}")
        print(f"  - 权重: {result1['relationship'].weight}")
        print(f"  - 关联知识点数量: {len(result1['relates_to_relationships'])}")
        
        # 在课程 B 中创建错误记录（同一学生，同一错误类型，不同课程）
        result2 = await graph_service.create_student_multi_course_error(
            student_id="DEMO_S001",
            error_type_id="DEMO_E001",
            course_id="DEMO_C002",
            occurrence_time=datetime(2024, 1, 15),
            knowledge_point_ids=["DEMO_KP001"],
        )
        print(f"✓ 在课程 {course2.properties['name']} 中创建错误记录")
        print(f"  - 是否为新记录: {result2['is_new']}")
        print(f"  - 发生次数: {result2['relationship'].properties['occurrence_count']}")
        
        # 演示功能 2: 重复错误权重更新
        print("\n4. 演示功能 2: 重复错误权重更新")
        print("-" * 60)
        
        # 在课程 A 中再次发生相同错误
        result3 = await graph_service.create_student_multi_course_error(
            student_id="DEMO_S001",
            error_type_id="DEMO_E001",
            course_id="DEMO_C001",
            occurrence_time=datetime(2024, 1, 20),
        )
        print(f"✓ 在课程 {course1.properties['name']} 中再次发生错误")
        print(f"  - 是否为新记录: {result3['is_new']}")
        print(f"  - 发生次数: {result3['relationship'].properties['occurrence_count']}")
        print(f"  - 权重: {result3['relationship'].weight}")
        
        # 演示功能 3: 错误统计聚合
        print("\n5. 演示功能 3: 错误统计聚合")
        print("-" * 60)
        
        stats = await graph_service.aggregate_student_errors("DEMO_S001")
        print(f"✓ 学生 {student.properties['name']} 的错误统计:")
        print(f"  - 总错误次数: {stats['total_errors']}")
        print(f"  - 涉及课程数: {len(stats['errors_by_course'])}")
        print(f"  - 涉及知识点数: {len(stats['errors_by_knowledge_point'])}")
        print(f"  - 错误类型数: {len(stats['errors_by_type'])}")
        
        print("\n  按课程统计:")
        for course_id, course_stats in stats['errors_by_course'].items():
            print(f"    - {course_id}: {course_stats['count']} 次错误")
        
        print("\n  按知识点统计:")
        for kp_id, kp_stats in stats['errors_by_knowledge_point'].items():
            print(f"    - {kp_id}: {kp_stats['count']} 次错误")
        
        # 演示功能 4: 跨课程知识点路径查询
        print("\n6. 演示功能 4: 跨课程知识点路径查询")
        print("-" * 60)
        
        # 首先创建课程到知识点的 CONTAINS 关系
        from app.models.relationships import RelationshipType
        await graph_service.create_relationship(
            course1.id,
            kp1.id,
            RelationshipType.CONTAINS,
            {"importance": "core"},
        )
        await graph_service.create_relationship(
            course2.id,
            kp1.id,
            RelationshipType.CONTAINS,
            {"importance": "core"},
        )
        print("✓ 创建课程到知识点的关联关系")
        
        paths = await graph_service.find_cross_course_knowledge_point_paths(
            course_id_1="DEMO_C001",
            course_id_2="DEMO_C002",
        )
        print(f"✓ 找到 {len(paths)} 条跨课程知识点路径")
        if paths:
            for i, path in enumerate(paths, 1):
                print(f"\n  路径 {i}:")
                print(f"    - 共享知识点: {path['knowledge_point_name']}")
                print(f"    - 路径长度: {path['path_length']}")
                print(f"    - 节点数量: {len(path['nodes'])}")
        
        print("\n" + "=" * 60)
        print("演示完成！")
        print("=" * 60)
        
    finally:
        # 清理测试数据
        print("\n7. 清理测试数据...")
        from app.database import neo4j_connection
        async with neo4j_connection.get_session() as session:
            await session.run(
                """
                MATCH (n)
                WHERE n.student_id STARTS WITH 'DEMO_' 
                   OR n.error_type_id STARTS WITH 'DEMO_'
                   OR n.knowledge_point_id STARTS WITH 'DEMO_'
                   OR n.course_id STARTS WITH 'DEMO_'
                DETACH DELETE n
                """
            )
        print("✓ 测试数据已清理")
        
        # 关闭数据库连接
        await close_database()
        print("✓ 数据库连接已关闭")


if __name__ == "__main__":
    asyncio.run(demo_multi_course_error_handling())
