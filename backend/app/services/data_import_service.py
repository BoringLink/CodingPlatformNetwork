"""数据导入服务

负责从原始教育数据中导入和处理数据，包括：
- 数据验证
- 批处理
- 进度跟踪
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import uuid4
import structlog

from pydantic import BaseModel, Field, field_validator

from app.models.nodes import NodeType
from app.services.graph_service import graph_service

logger = structlog.get_logger()


class RecordType(str, Enum):
    """原始记录类型枚举"""
    
    STUDENT_INTERACTION = "student_interaction"
    TEACHER_INTERACTION = "teacher_interaction"
    COURSE_RECORD = "course_record"
    ERROR_RECORD = "error_record"


class RawRecord(BaseModel):
    """原始记录模型
    
    表示从教育数据源读取的原始数据记录
    """
    
    type: RecordType = Field(..., description="记录类型")
    timestamp: datetime = Field(..., description="记录时间戳")
    data: Dict[str, Any] = Field(..., description="记录数据")
    
    @field_validator("data")
    @classmethod
    def validate_data_not_empty(cls, v):
        """验证数据不为空"""
        if not v:
            raise ValueError("data cannot be empty")
        return v


class ValidationError(BaseModel):
    """验证错误模型"""
    
    record_index: int = Field(..., description="记录索引")
    record_type: RecordType = Field(..., description="记录类型")
    error_message: str = Field(..., description="错误消息")
    field_name: Optional[str] = Field(default=None, description="错误字段名")
    expected_format: Optional[str] = Field(default=None, description="期望格式")
    actual_value: Optional[Any] = Field(default=None, description="实际值")


class ValidationResult(BaseModel):
    """验证结果模型"""
    
    is_valid: bool = Field(..., description="是否有效")
    errors: List[str] = Field(default_factory=list, description="错误列表")
    warnings: List[str] = Field(default_factory=list, description="警告列表")


class ImportProgress(BaseModel):
    """导入进度模型"""
    
    total_records: int = Field(..., description="总记录数")
    processed_records: int = Field(..., description="已处理记录数")
    successful_records: int = Field(..., description="成功记录数")
    failed_records: int = Field(..., description="失败记录数")
    current_batch: int = Field(..., description="当前批次号")
    total_batches: int = Field(..., description="总批次数")
    progress_percentage: float = Field(..., description="进度百分比")
    start_time: datetime = Field(..., description="开始时间")
    elapsed_time: float = Field(..., description="已用时间（秒）")
    estimated_remaining_time: Optional[float] = Field(
        default=None,
        description="预计剩余时间（秒）",
    )


class ImportResult(BaseModel):
    """导入结果模型"""
    
    success_count: int = Field(..., description="成功数量")
    failure_count: int = Field(..., description="失败数量")
    errors: List[ValidationError] = Field(default_factory=list, description="错误列表")
    total_time: float = Field(..., description="总耗时（秒）")
    records_per_second: float = Field(..., description="每秒处理记录数")


class DataImportService:
    """数据导入服务
    
    提供数据导入、验证和批处理功能
    """
    
    def __init__(self):
        """初始化数据导入服务"""
        self._progress: Optional[ImportProgress] = None
        self._import_id: Optional[str] = None
    
    async def import_batch(
        self,
        records: List[RawRecord],
        batch_size: int = 1000,
    ) -> ImportResult:
        """导入数据批次
        
        将原始记录批量导入到图数据库中
        
        Args:
            records: 原始记录列表
            batch_size: 批处理大小（默认1000）
            
        Returns:
            导入结果
            
        Raises:
            ValueError: 如果批处理大小无效
        """
        if batch_size < 1 or batch_size > 10000:
            raise ValueError("batch_size must be between 1 and 10000")
        
        # 初始化导入会话
        self._import_id = str(uuid4())
        start_time = datetime.utcnow()
        
        total_records = len(records)
        total_batches = (total_records + batch_size - 1) // batch_size
        
        # 初始化进度
        self._progress = ImportProgress(
            total_records=total_records,
            processed_records=0,
            successful_records=0,
            failed_records=0,
            current_batch=0,
            total_batches=total_batches,
            progress_percentage=0.0,
            start_time=start_time,
            elapsed_time=0.0,
        )
        
        logger.info(
            "import_started",
            import_id=self._import_id,
            total_records=total_records,
            batch_size=batch_size,
            total_batches=total_batches,
        )
        
        success_count = 0
        failure_count = 0
        errors: List[ValidationError] = []
        
        # 分批处理记录
        for batch_num in range(total_batches):
            batch_start = batch_num * batch_size
            batch_end = min(batch_start + batch_size, total_records)
            batch_records = records[batch_start:batch_end]
            
            self._progress.current_batch = batch_num + 1
            
            logger.info(
                "processing_batch",
                import_id=self._import_id,
                batch_num=batch_num + 1,
                batch_size=len(batch_records),
            )
            
            # 处理批次中的每条记录
            for idx, record in enumerate(batch_records):
                record_index = batch_start + idx
                
                try:
                    # 验证记录
                    validation_result = self.validate_record(record)
                    
                    if not validation_result.is_valid:
                        # 记录验证错误
                        error = ValidationError(
                            record_index=record_index,
                            record_type=record.type,
                            error_message="; ".join(validation_result.errors),
                        )
                        errors.append(error)
                        failure_count += 1
                        
                        logger.warning(
                            "record_validation_failed",
                            import_id=self._import_id,
                            record_index=record_index,
                            record_type=record.type,
                            errors=validation_result.errors,
                        )
                    else:
                        # 处理有效记录
                        await self._process_record(record)
                        success_count += 1
                        
                except Exception as e:
                    # 记录处理错误
                    error = ValidationError(
                        record_index=record_index,
                        record_type=record.type,
                        error_message=str(e),
                    )
                    errors.append(error)
                    failure_count += 1
                    
                    logger.error(
                        "record_processing_failed",
                        import_id=self._import_id,
                        record_index=record_index,
                        record_type=record.type,
                        error=str(e),
                    )
                
                # 更新进度
                self._progress.processed_records += 1
                self._progress.successful_records = success_count
                self._progress.failed_records = failure_count
                
                # 计算进度百分比
                self._progress.progress_percentage = (
                    self._progress.processed_records / total_records * 100
                )
                
                # 计算已用时间和预计剩余时间
                elapsed = (datetime.utcnow() - start_time).total_seconds()
                self._progress.elapsed_time = elapsed
                
                if self._progress.processed_records > 0:
                    avg_time_per_record = elapsed / self._progress.processed_records
                    remaining_records = total_records - self._progress.processed_records
                    self._progress.estimated_remaining_time = (
                        avg_time_per_record * remaining_records
                    )
        
        # 计算总耗时
        end_time = datetime.utcnow()
        total_time = (end_time - start_time).total_seconds()
        records_per_second = total_records / total_time if total_time > 0 else 0
        
        logger.info(
            "import_completed",
            import_id=self._import_id,
            success_count=success_count,
            failure_count=failure_count,
            total_time=total_time,
            records_per_second=records_per_second,
        )
        
        return ImportResult(
            success_count=success_count,
            failure_count=failure_count,
            errors=errors,
            total_time=total_time,
            records_per_second=records_per_second,
        )
    
    def validate_record(self, record: RawRecord) -> ValidationResult:
        """验证数据格式
        
        验证记录的数据格式和完整性
        
        Args:
            record: 原始记录
            
        Returns:
            验证结果
        """
        errors: List[str] = []
        warnings: List[str] = []
        
        # 根据记录类型验证必需字段
        if record.type == RecordType.STUDENT_INTERACTION:
            errors.extend(self._validate_student_interaction(record.data))
        elif record.type == RecordType.TEACHER_INTERACTION:
            errors.extend(self._validate_teacher_interaction(record.data))
        elif record.type == RecordType.COURSE_RECORD:
            errors.extend(self._validate_course_record(record.data))
        elif record.type == RecordType.ERROR_RECORD:
            errors.extend(self._validate_error_record(record.data))
        else:
            errors.append(f"Unknown record type: {record.type}")
        
        # 检查数据质量问题（警告）
        if not record.data:
            warnings.append("Record data is empty")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
        )
    
    def _validate_student_interaction(self, data: Dict[str, Any]) -> List[str]:
        """验证学生互动记录
        
        Args:
            data: 记录数据
            
        Returns:
            错误列表
        """
        errors = []
        
        # 必需字段
        required_fields = ["student_id_from", "student_id_to", "interaction_type"]
        for field in required_fields:
            if field not in data or not data[field]:
                errors.append(f"Missing required field: {field}")
        
        # 验证互动类型
        if "interaction_type" in data:
            valid_types = ["chat", "like"]
            if data["interaction_type"] not in valid_types:
                errors.append(
                    f"Invalid interaction_type: {data['interaction_type']}. "
                    f"Must be one of {valid_types}"
                )
        
        return errors
    
    def _validate_teacher_interaction(self, data: Dict[str, Any]) -> List[str]:
        """验证师生互动记录
        
        Args:
            data: 记录数据
            
        Returns:
            错误列表
        """
        errors = []
        
        # 必需字段
        required_fields = ["teacher_id", "student_id"]
        for field in required_fields:
            if field not in data or not data[field]:
                errors.append(f"Missing required field: {field}")
        
        return errors
    
    def _validate_course_record(self, data: Dict[str, Any]) -> List[str]:
        """验证课程记录
        
        Args:
            data: 记录数据
            
        Returns:
            错误列表
        """
        errors = []
        
        # 必需字段
        required_fields = ["student_id", "course_id"]
        for field in required_fields:
            if field not in data or not data[field]:
                errors.append(f"Missing required field: {field}")
        
        # 验证进度范围
        if "progress" in data:
            try:
                progress = float(data["progress"])
                if progress < 0 or progress > 100:
                    errors.append("progress must be between 0 and 100")
            except (ValueError, TypeError):
                errors.append("progress must be a number")
        
        return errors
    
    def _validate_error_record(self, data: Dict[str, Any]) -> List[str]:
        """验证错误记录
        
        Args:
            data: 记录数据
            
        Returns:
            错误列表
        """
        errors = []
        
        # 必需字段
        required_fields = ["student_id", "course_id", "error_text"]
        for field in required_fields:
            if field not in data or not data[field]:
                errors.append(f"Missing required field: {field}")
        
        return errors
    
    async def _process_record(self, record: RawRecord) -> None:
        """处理单条记录
        
        根据记录类型创建相应的节点和关系
        
        Args:
            record: 原始记录
            
        Raises:
            RuntimeError: 如果处理失败
        """
        try:
            if record.type == RecordType.STUDENT_INTERACTION:
                await self._process_student_interaction(record)
            elif record.type == RecordType.TEACHER_INTERACTION:
                await self._process_teacher_interaction(record)
            elif record.type == RecordType.COURSE_RECORD:
                await self._process_course_record(record)
            elif record.type == RecordType.ERROR_RECORD:
                await self._process_error_record(record)
        except Exception as e:
            logger.error(
                "record_processing_error",
                record_type=record.type,
                error=str(e),
            )
            raise RuntimeError(f"Failed to process record: {e}")
    
    async def _process_student_interaction(self, record: RawRecord) -> None:
        """处理学生互动记录
        
        创建学生节点和互动关系
        
        Args:
            record: 原始记录
        """
        data = record.data
        
        # 创建或获取学生节点
        student_from = await graph_service.create_node(
            NodeType.STUDENT,
            {
                "student_id": data["student_id_from"],
                "name": data.get("student_name_from", f"Student {data['student_id_from']}"),
            },
        )
        
        student_to = await graph_service.create_node(
            NodeType.STUDENT,
            {
                "student_id": data["student_id_to"],
                "name": data.get("student_name_to", f"Student {data['student_id_to']}"),
            },
        )
        
        # 创建互动关系
        from app.models.relationships import RelationshipType
        
        if data["interaction_type"] == "chat":
            await graph_service.create_relationship(
                student_from.id,
                student_to.id,
                RelationshipType.CHAT_WITH,
                {
                    "message_count": data.get("message_count", 1),
                    "last_interaction_date": record.timestamp,
                    "topics": data.get("topics"),
                },
            )
        elif data["interaction_type"] == "like":
            await graph_service.create_relationship(
                student_from.id,
                student_to.id,
                RelationshipType.LIKES,
                {
                    "like_count": data.get("like_count", 1),
                    "last_like_date": record.timestamp,
                },
            )
    
    async def _process_teacher_interaction(self, record: RawRecord) -> None:
        """处理师生互动记录
        
        创建教师节点、学生节点和教学关系
        
        Args:
            record: 原始记录
        """
        data = record.data
        
        # 创建或获取教师节点
        teacher = await graph_service.create_node(
            NodeType.TEACHER,
            {
                "teacher_id": data["teacher_id"],
                "name": data.get("teacher_name", f"Teacher {data['teacher_id']}"),
                "subject": data.get("subject"),
            },
        )
        
        # 创建或获取学生节点
        student = await graph_service.create_node(
            NodeType.STUDENT,
            {
                "student_id": data["student_id"],
                "name": data.get("student_name", f"Student {data['student_id']}"),
            },
        )
        
        # 创建教学关系
        from app.models.relationships import RelationshipType
        
        await graph_service.create_relationship(
            teacher.id,
            student.id,
            RelationshipType.TEACHES,
            {
                "interaction_count": data.get("interaction_count", 1),
                "last_interaction_date": record.timestamp,
                "feedback": data.get("feedback"),
            },
        )
    
    async def _process_course_record(self, record: RawRecord) -> None:
        """处理课程记录
        
        创建学生节点、课程节点和学习关系
        
        Args:
            record: 原始记录
        """
        data = record.data
        
        # 创建或获取学生节点
        student = await graph_service.create_node(
            NodeType.STUDENT,
            {
                "student_id": data["student_id"],
                "name": data.get("student_name", f"Student {data['student_id']}"),
            },
        )
        
        # 创建或获取课程节点
        course = await graph_service.create_node(
            NodeType.COURSE,
            {
                "course_id": data["course_id"],
                "name": data.get("course_name", f"Course {data['course_id']}"),
                "description": data.get("course_description"),
                "difficulty": data.get("difficulty"),
            },
        )
        
        # 创建学习关系
        from app.models.relationships import RelationshipType
        
        await graph_service.create_relationship(
            student.id,
            course.id,
            RelationshipType.LEARNS,
            {
                "enrollment_date": data.get("enrollment_date", record.timestamp),
                "progress": data.get("progress", 0.0),
                "completion_date": data.get("completion_date"),
                "time_spent": data.get("time_spent"),
            },
        )
    
    async def _process_error_record(self, record: RawRecord) -> None:
        """处理错误记录
        
        创建学生节点、错误类型节点和错误关系
        注意：知识点提取需要LLM服务，这里暂时不处理
        
        Args:
            record: 原始记录
        """
        data = record.data
        
        # 创建或获取学生节点
        student = await graph_service.create_node(
            NodeType.STUDENT,
            {
                "student_id": data["student_id"],
                "name": data.get("student_name", f"Student {data['student_id']}"),
            },
        )
        
        # 创建或获取错误类型节点
        error_type = await graph_service.create_node(
            NodeType.ERROR_TYPE,
            {
                "error_type_id": data.get("error_type_id", f"error_{uuid4().hex[:8]}"),
                "name": data.get("error_type", "Unknown Error"),
                "description": data.get("error_text", ""),
                "severity": data.get("severity"),
            },
        )
        
        # 创建错误关系
        from app.models.relationships import RelationshipType
        
        await graph_service.create_relationship(
            student.id,
            error_type.id,
            RelationshipType.HAS_ERROR,
            {
                "occurrence_count": data.get("occurrence_count", 1),
                "first_occurrence": data.get("first_occurrence", record.timestamp),
                "last_occurrence": record.timestamp,
                "course_id": data["course_id"],
                "resolved": data.get("resolved", False),
            },
        )
    
    def get_progress(self) -> Optional[ImportProgress]:
        """获取导入进度
        
        Returns:
            当前导入进度，如果没有正在进行的导入则返回 None
        """
        return self._progress


# 全局服务实例
data_import_service = DataImportService()
