"""测试后端核心架构设置"""

import sys
from datetime import datetime

def test_imports():
    """测试所有核心模块导入"""
    print("Testing imports...")
    
    from app.main import app
    from app.config import settings
    from app.models import (
        Node, Relationship,
        NodeType, RelationshipType,
        StudentNodeProperties, TeacherNodeProperties,
        CourseNodeProperties, KnowledgePointNodeProperties,
        ErrorTypeNodeProperties,
    )
    from app.utils.logging import configure_logging, get_logger
    
    print("✓ All imports successful")
    return True


def test_config():
    """测试配置管理"""
    print("\nTesting configuration...")
    
    from app.config import settings
    
    assert settings.app_name == "教育知识图谱系统"
    assert settings.batch_size == 1000
    assert settings.llm_retry_max == 3
    assert settings.log_level in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    assert settings.log_format in ["json", "console"]
    
    # Test computed properties
    redis_url = settings.redis_url
    assert "redis://" in redis_url
    
    print(f"✓ Configuration loaded: {settings.app_name}")
    print(f"  - Debug mode: {settings.debug}")
    print(f"  - Log level: {settings.log_level}")
    print(f"  - Batch size: {settings.batch_size}")
    return True


def test_pydantic_models():
    """测试 Pydantic 数据模型"""
    print("\nTesting Pydantic models...")
    
    from app.models import (
        StudentNodeProperties, CourseNodeProperties,
        LearnsProperties, HasErrorProperties,
    )
    
    # Test student node
    student = StudentNodeProperties(
        student_id="S001",
        name="张三",
        grade="5",
        enrollment_date=datetime.now(),
    )
    assert student.student_id == "S001"
    assert student.name == "张三"
    
    # Test course node
    course = CourseNodeProperties(
        course_id="C001",
        name="数学基础",
        description="基础数学课程",
        difficulty="beginner",
    )
    assert course.difficulty == "beginner"
    
    # Test relationship properties
    learns = LearnsProperties(
        enrollment_date=datetime.now(),
        progress=50.0,
    )
    assert 0 <= learns.progress <= 100
    
    # Test validation
    try:
        invalid_course = CourseNodeProperties(
            course_id="C002",
            name="",  # Invalid: empty name
        )
        print("✗ Validation failed to catch empty name")
        return False
    except Exception:
        pass
    
    try:
        invalid_difficulty = CourseNodeProperties(
            course_id="C003",
            name="Test Course",
            difficulty="invalid",  # Invalid difficulty
        )
        print("✗ Validation failed to catch invalid difficulty")
        return False
    except Exception:
        pass
    
    print("✓ Pydantic models working correctly")
    print("  - Student node validation: OK")
    print("  - Course node validation: OK")
    print("  - Relationship properties validation: OK")
    return True


def test_logging():
    """测试结构化日志"""
    print("\nTesting structured logging...")
    
    from app.utils.logging import configure_logging, get_logger
    
    configure_logging()
    logger = get_logger("test")
    
    # Test different log levels
    logger.debug("debug_message", test=True)
    logger.info("info_message", test=True)
    logger.warning("warning_message", test=True)
    
    print("✓ Structured logging configured")
    return True


def test_fastapi_app():
    """测试 FastAPI 应用"""
    print("\nTesting FastAPI application...")
    
    from app.main import app
    
    assert app.title == "教育知识图谱神经网络系统"
    assert app.version == "0.1.0"
    
    # Check routes
    routes = [route.path for route in app.routes]
    assert "/" in routes
    assert "/health" in routes
    
    print("✓ FastAPI application configured")
    print(f"  - Title: {app.title}")
    print(f"  - Version: {app.version}")
    print(f"  - Routes: {len(routes)}")
    return True


def main():
    """运行所有测试"""
    print("=" * 60)
    print("后端核心架构测试")
    print("=" * 60)
    
    tests = [
        test_imports,
        test_config,
        test_pydantic_models,
        test_logging,
        test_fastapi_app,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"✗ {test.__name__} failed: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"测试结果: {passed} 通过, {failed} 失败")
    print("=" * 60)
    
    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
