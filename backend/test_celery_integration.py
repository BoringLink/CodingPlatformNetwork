"""Celery集成测试脚本

测试Celery任务队列的基本功能
"""

import asyncio
from datetime import datetime
from app.tasks.data_import import import_batch_task
from app.tasks.llm_analysis import (
    analyze_interaction_task,
    analyze_error_task,
    extract_knowledge_points_task,
)


def test_data_import_task():
    """测试数据导入任务"""
    print("\n=== 测试数据导入任务 ===")
    
    # 准备测试数据
    records_data = [
        {
            "type": "student_interaction",
            "timestamp": datetime.utcnow().isoformat(),
            "data": {
                "student_id_from": "S001",
                "student_id_to": "S002",
                "interaction_type": "chat",
                "message_count": 5,
            }
        },
        {
            "type": "course_record",
            "timestamp": datetime.utcnow().isoformat(),
            "data": {
                "student_id": "S001",
                "course_id": "C001",
                "course_name": "数学",
                "progress": 50.0,
            }
        },
    ]
    
    # 提交任务
    print("提交数据导入任务...")
    task = import_batch_task.delay(records_data, batch_size=100)
    print(f"任务ID: {task.id}")
    print(f"任务状态: {task.state}")
    
    # 等待结果（最多30秒）
    try:
        print("等待任务完成...")
        result = task.get(timeout=30)
        print(f"✓ 任务完成")
        print(f"  成功: {result['success_count']}")
        print(f"  失败: {result['failure_count']}")
        print(f"  耗时: {result['total_time']:.2f}秒")
        return True
    except Exception as e:
        print(f"✗ 任务失败: {e}")
        return False


def test_analyze_interaction_task():
    """测试互动分析任务"""
    print("\n=== 测试互动分析任务 ===")
    
    # 提交任务
    print("提交互动分析任务...")
    task = analyze_interaction_task.delay(
        text="小明和小红讨论了数学作业中的分数加法问题，气氛很友好",
        interaction_id="INT001"
    )
    print(f"任务ID: {task.id}")
    print(f"任务状态: {task.state}")
    
    # 等待结果（最多30秒）
    try:
        print("等待任务完成...")
        result = task.get(timeout=30)
        print(f"✓ 任务完成")
        print(f"  情感: {result['sentiment']}")
        print(f"  主题: {result['topics']}")
        print(f"  置信度: {result['confidence']}")
        return True
    except Exception as e:
        print(f"✗ 任务失败: {e}")
        return False


def test_analyze_error_task():
    """测试错误分析任务"""
    print("\n=== 测试错误分析任务 ===")
    
    # 提交任务
    print("提交错误分析任务...")
    task = analyze_error_task.delay(
        error_text="学生在计算 1/2 + 1/3 时，直接将分子分母相加得到 2/5",
        error_id="ERR001",
        course_id="C001",
        course_name="小学数学",
        course_description="小学三年级数学课程"
    )
    print(f"任务ID: {task.id}")
    print(f"任务状态: {task.state}")
    
    # 等待结果（最多30秒）
    try:
        print("等待任务完成...")
        result = task.get(timeout=30)
        print(f"✓ 任务完成")
        print(f"  错误类型: {result['error_type']}")
        print(f"  相关知识点: {result['related_knowledge_points']}")
        print(f"  难度: {result['difficulty']}")
        print(f"  置信度: {result['confidence']}")
        return True
    except Exception as e:
        print(f"✗ 任务失败: {e}")
        return False


def test_extract_knowledge_points_task():
    """测试知识点提取任务"""
    print("\n=== 测试知识点提取任务 ===")
    
    # 提交任务
    print("提交知识点提取任务...")
    task = extract_knowledge_points_task.delay(
        course_content="""
        本课程介绍分数的基本概念和运算。
        主要内容包括：
        1. 分数的定义和表示
        2. 分数的比较
        3. 分数的加减法
        4. 分数的乘除法
        """,
        course_id="C001"
    )
    print(f"任务ID: {task.id}")
    print(f"任务状态: {task.state}")
    
    # 等待结果（最多30秒）
    try:
        print("等待任务完成...")
        result = task.get(timeout=30)
        print(f"✓ 任务完成")
        print(f"  提取的知识点数量: {len(result['knowledge_points'])}")
        for kp in result['knowledge_points']:
            print(f"  - {kp['name']}: {kp['description'][:50]}...")
        return True
    except Exception as e:
        print(f"✗ 任务失败: {e}")
        return False


def main():
    """运行所有测试"""
    print("=" * 60)
    print("Celery集成测试")
    print("=" * 60)
    print("\n注意：运行此测试前，请确保：")
    print("1. Redis服务已启动")
    print("2. Celery Worker已启动")
    print("3. Neo4j数据库已启动")
    print("4. 已配置DASHSCOPE_API_KEY环境变量")
    print("\n按Enter键继续...")
    input()
    
    results = []
    
    # 测试数据导入任务
    results.append(("数据导入任务", test_data_import_task()))
    
    # 测试LLM分析任务（需要API密钥）
    print("\n是否测试LLM分析任务？（需要配置DASHSCOPE_API_KEY）[y/N]: ", end="")
    if input().lower() == 'y':
        results.append(("互动分析任务", test_analyze_interaction_task()))
        results.append(("错误分析任务", test_analyze_error_task()))
        results.append(("知识点提取任务", test_extract_knowledge_points_task()))
    
    # 打印测试结果
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    for name, success in results:
        status = "✓ 通过" if success else "✗ 失败"
        print(f"{name}: {status}")
    
    total = len(results)
    passed = sum(1 for _, success in results if success)
    print(f"\n总计: {passed}/{total} 通过")


if __name__ == "__main__":
    main()
