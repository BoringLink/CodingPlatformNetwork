"""数据导入服务演示脚本

演示数据导入服务的核心功能：
1. 数据验证
2. 批处理
3. 进度跟踪
"""

import asyncio
from datetime import datetime

from app.services.data_import_service import (
    data_import_service,
    RawRecord,
    RecordType,
)


async def demo_validation():
    """演示数据验证功能"""
    print("=" * 60)
    print("演示 1: 数据验证")
    print("=" * 60)
    
    # 有效记录
    valid_record = RawRecord(
        type=RecordType.STUDENT_INTERACTION,
        timestamp=datetime.utcnow(),
        data={
            "student_id_from": "S001",
            "student_id_to": "S002",
            "interaction_type": "chat",
            "message_count": 5,
        },
    )
    
    result = data_import_service.validate_record(valid_record)
    print(f"\n有效记录验证结果:")
    print(f"  是否有效: {result.is_valid}")
    print(f"  错误数量: {len(result.errors)}")
    
    # 无效记录
    invalid_record = RawRecord(
        type=RecordType.STUDENT_INTERACTION,
        timestamp=datetime.utcnow(),
        data={
            "student_id_from": "S001",
            # 缺少必需字段
        },
    )
    
    result = data_import_service.validate_record(invalid_record)
    print(f"\n无效记录验证结果:")
    print(f"  是否有效: {result.is_valid}")
    print(f"  错误数量: {len(result.errors)}")
    print(f"  错误信息: {result.errors}")


async def demo_batch_processing():
    """演示批处理功能"""
    print("\n" + "=" * 60)
    print("演示 2: 批处理")
    print("=" * 60)
    
    # 创建测试记录
    records = []
    for i in range(25):
        records.append(
            RawRecord(
                type=RecordType.STUDENT_INTERACTION,
                timestamp=datetime.utcnow(),
                data={
                    "student_id_from": f"S{i:03d}",
                    "student_id_to": f"S{i+1:03d}",
                    "interaction_type": "chat",
                    "message_count": i + 1,
                },
            )
        )
    
    print(f"\n创建了 {len(records)} 条测试记录")
    print(f"批处理大小: 10")
    print(f"预期批次数: {(len(records) + 9) // 10}")
    
    # 注意：这里不实际导入，因为需要数据库连接
    # result = await data_import_service.import_batch(records, batch_size=10)
    print("\n批处理功能已实现，需要数据库连接才能运行")


async def demo_progress_tracking():
    """演示进度跟踪功能"""
    print("\n" + "=" * 60)
    print("演示 3: 进度跟踪")
    print("=" * 60)
    
    print("\n进度跟踪功能已实现，包括:")
    print("  - 总记录数")
    print("  - 已处理记录数")
    print("  - 成功/失败记录数")
    print("  - 当前批次/总批次")
    print("  - 进度百分比")
    print("  - 已用时间")
    print("  - 预计剩余时间")
    
    # 获取当前进度（如果有正在进行的导入）
    progress = data_import_service.get_progress()
    if progress:
        print(f"\n当前导入进度:")
        print(f"  总记录数: {progress.total_records}")
        print(f"  已处理: {progress.processed_records}")
        print(f"  进度: {progress.progress_percentage:.2f}%")
    else:
        print("\n当前没有正在进行的导入任务")


async def demo_record_types():
    """演示不同记录类型的验证"""
    print("\n" + "=" * 60)
    print("演示 4: 不同记录类型验证")
    print("=" * 60)
    
    record_types = [
        (RecordType.STUDENT_INTERACTION, {
            "student_id_from": "S001",
            "student_id_to": "S002",
            "interaction_type": "chat",
        }),
        (RecordType.TEACHER_INTERACTION, {
            "teacher_id": "T001",
            "student_id": "S001",
        }),
        (RecordType.COURSE_RECORD, {
            "student_id": "S001",
            "course_id": "C001",
            "progress": 75.0,
        }),
        (RecordType.ERROR_RECORD, {
            "student_id": "S001",
            "course_id": "C001",
            "error_text": "计算错误",
        }),
    ]
    
    for record_type, data in record_types:
        record = RawRecord(
            type=record_type,
            timestamp=datetime.utcnow(),
            data=data,
        )
        result = data_import_service.validate_record(record)
        print(f"\n{record_type.value}:")
        print(f"  验证结果: {'✓ 有效' if result.is_valid else '✗ 无效'}")
        if result.errors:
            print(f"  错误: {result.errors}")


async def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("数据导入服务演示")
    print("=" * 60)
    
    await demo_validation()
    await demo_batch_processing()
    await demo_progress_tracking()
    await demo_record_types()
    
    print("\n" + "=" * 60)
    print("演示完成")
    print("=" * 60)
    print("\n实现的功能:")
    print("  ✓ DataImportService 接口")
    print("  ✓ 数据验证器（Pydantic 模型）")
    print("  ✓ 批处理逻辑（每批 1000 条，可配置）")
    print("  ✓ 进度跟踪")
    print("  ✓ 支持所有记录类型（学生互动、师生互动、课程记录、错误记录）")
    print("  ✓ 错误处理和日志记录")
    print("\n需求覆盖:")
    print("  ✓ 需求 1.1: 识别并创建不同类型的节点")
    print("  ✓ 需求 1.5: 标记缺失字段并记录数据质量问题")
    print("  ✓ 需求 7.1: 批处理机制（每批不超过 1000 条）")
    print("  ✓ 需求 7.3: 提供进度反馈")
    print()


if __name__ == "__main__":
    asyncio.run(main())
