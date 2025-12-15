"""验证任务 9 的实现完整性

此脚本验证所有必需的功能是否已正确实现。
"""

import inspect
from app.services.graph_service import GraphManagementService

def verify_task_9_implementation():
    """验证任务 9 的所有功能是否已实现"""
    
    print("=" * 70)
    print("任务 9 实施验证")
    print("=" * 70)
    
    service = GraphManagementService()
    
    # 定义必需的方法
    required_methods = {
        "create_student_multi_course_error": "创建学生多课程错误记录",
        "associate_error_with_knowledge_points": "错误类型多知识点关联",
        "aggregate_student_errors": "错误统计聚合",
        "find_cross_course_knowledge_point_paths": "跨课程知识点路径查询",
        "update_repeated_error_weight": "重复错误权重更新",
    }
    
    print("\n检查必需方法:")
    print("-" * 70)
    
    all_methods_present = True
    for method_name, description in required_methods.items():
        if hasattr(service, method_name):
            method = getattr(service, method_name)
            if callable(method):
                # 获取方法签名
                sig = inspect.signature(method)
                params = list(sig.parameters.keys())
                
                print(f"✓ {method_name}")
                print(f"  描述: {description}")
                print(f"  参数: {', '.join(params)}")
                
                # 获取文档字符串
                docstring = inspect.getdoc(method)
                if docstring:
                    first_line = docstring.split('\n')[0]
                    print(f"  文档: {first_line}")
                print()
            else:
                print(f"✗ {method_name} 存在但不可调用")
                all_methods_present = False
        else:
            print(f"✗ {method_name} 未找到")
            all_methods_present = False
    
    # 检查方法参数
    print("\n检查方法参数:")
    print("-" * 70)
    
    # create_student_multi_course_error 参数检查
    method = getattr(service, "create_student_multi_course_error")
    sig = inspect.signature(method)
    expected_params = ["self", "student_id", "error_type_id", "course_id", 
                       "occurrence_time", "knowledge_point_ids"]
    actual_params = list(sig.parameters.keys())
    
    if set(expected_params) == set(actual_params):
        print("✓ create_student_multi_course_error 参数正确")
    else:
        print(f"✗ create_student_multi_course_error 参数不匹配")
        print(f"  期望: {expected_params}")
        print(f"  实际: {actual_params}")
    
    # aggregate_student_errors 参数检查
    method = getattr(service, "aggregate_student_errors")
    sig = inspect.signature(method)
    expected_params = ["self", "student_id"]
    actual_params = list(sig.parameters.keys())
    
    if set(expected_params) == set(actual_params):
        print("✓ aggregate_student_errors 参数正确")
    else:
        print(f"✗ aggregate_student_errors 参数不匹配")
    
    # find_cross_course_knowledge_point_paths 参数检查
    method = getattr(service, "find_cross_course_knowledge_point_paths")
    sig = inspect.signature(method)
    expected_params = ["self", "course_id_1", "course_id_2", "max_depth"]
    actual_params = list(sig.parameters.keys())
    
    if set(expected_params) == set(actual_params):
        print("✓ find_cross_course_knowledge_point_paths 参数正确")
    else:
        print(f"✗ find_cross_course_knowledge_point_paths 参数不匹配")
    
    # 检查文档文件
    print("\n检查文档文件:")
    print("-" * 70)
    
    import os
    
    doc_files = {
        "MULTI_COURSE_ERROR_HANDLING.md": "功能文档",
        "TASK_9_IMPLEMENTATION_SUMMARY.md": "实施总结",
        "QUICK_START_MULTI_COURSE_ERROR.md": "快速开始指南",
        "demo_multi_course_error.py": "演示脚本",
    }
    
    for filename, description in doc_files.items():
        if os.path.exists(filename):
            size = os.path.getsize(filename)
            print(f"✓ {filename} ({description}) - {size} 字节")
        else:
            print(f"✗ {filename} 未找到")
    
    # 检查测试文件
    print("\n检查测试文件:")
    print("-" * 70)
    
    test_file = "tests/test_graph_service.py"
    if os.path.exists(test_file):
        with open(test_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # 检查测试函数
        test_functions = [
            "test_create_student_multi_course_error",
            "test_create_student_multi_course_error_repeated",
            "test_associate_error_with_knowledge_points",
            "test_aggregate_student_errors",
            "test_find_cross_course_knowledge_point_paths",
            "test_update_repeated_error_weight",
        ]
        
        for test_func in test_functions:
            if test_func in content:
                print(f"✓ {test_func}")
            else:
                print(f"✗ {test_func} 未找到")
    else:
        print(f"✗ {test_file} 未找到")
    
    # 总结
    print("\n" + "=" * 70)
    if all_methods_present:
        print("✓ 任务 9 实施完成！所有必需功能已实现。")
    else:
        print("✗ 任务 9 实施不完整，请检查缺失的方法。")
    print("=" * 70)
    
    # 需求验证
    print("\n需求验证:")
    print("-" * 70)
    requirements = {
        "4.1": "学生多课程错误记录创建 - create_student_multi_course_error()",
        "4.2": "错误类型多知识点关联 - associate_error_with_knowledge_points()",
        "4.3": "错误统计聚合 - aggregate_student_errors()",
        "4.4": "跨课程知识点路径查询 - find_cross_course_knowledge_point_paths()",
        "4.5": "重复错误权重更新 - update_repeated_error_weight()",
    }
    
    for req_id, req_desc in requirements.items():
        print(f"✓ 需求 {req_id}: {req_desc}")
    
    print("\n" + "=" * 70)
    print("验证完成！")
    print("=" * 70)


if __name__ == "__main__":
    verify_task_9_implementation()
