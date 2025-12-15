"""关系数据模型"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict
from pydantic import Field, field_validator

from app.models.base import BaseRelationshipProperties


class RelationshipType(str, Enum):
    """关系类型枚举"""
    
    CHAT_WITH = "CHAT_WITH"
    LIKES = "LIKES"
    TEACHES = "TEACHES"
    LEARNS = "LEARNS"
    CONTAINS = "CONTAINS"
    HAS_ERROR = "HAS_ERROR"
    RELATES_TO = "RELATES_TO"


class ChatWithProperties(BaseRelationshipProperties):
    """聊天互动关系属性"""
    
    message_count: int = Field(default=1, ge=1, description="消息数量")
    last_interaction_date: datetime = Field(..., description="最后互动日期")
    topics: list[str] | None = Field(default=None, description="讨论主题")


class LikesProperties(BaseRelationshipProperties):
    """点赞互动关系属性"""
    
    like_count: int = Field(default=1, ge=1, description="点赞数量")
    last_like_date: datetime = Field(..., description="最后点赞日期")


class TeachesProperties(BaseRelationshipProperties):
    """教学互动关系属性"""
    
    interaction_count: int = Field(default=1, ge=1, description="互动次数")
    last_interaction_date: datetime = Field(..., description="最后互动日期")
    feedback: str | None = Field(default=None, description="反馈信息")


class LearnsProperties(BaseRelationshipProperties):
    """学习关系属性"""
    
    enrollment_date: datetime = Field(..., description="注册日期")
    progress: float = Field(default=0.0, ge=0.0, le=100.0, description="学习进度（0-100）")
    completion_date: datetime | None = Field(default=None, description="完成日期")
    time_spent: int | None = Field(default=None, ge=0, description="学习时长（分钟）")


class ContainsProperties(BaseRelationshipProperties):
    """包含关系属性"""
    
    order: int | None = Field(default=None, ge=0, description="顺序")
    importance: str | None = Field(default=None, description="重要性")
    
    @field_validator("importance")
    @classmethod
    def validate_importance(cls, v):
        """验证重要性"""
        if v is not None:
            valid_importance = ["core", "supplementary"]
            if v not in valid_importance:
                raise ValueError(f"importance must be one of {valid_importance}")
        return v


class HasErrorProperties(BaseRelationshipProperties):
    """错误关系属性"""
    
    occurrence_count: int = Field(default=1, ge=1, description="发生次数")
    first_occurrence: datetime = Field(..., description="首次发生时间")
    last_occurrence: datetime = Field(..., description="最后发生时间")
    course_id: str = Field(..., description="课程 ID")
    resolved: bool = Field(default=False, description="是否已解决")


class RelatesToProperties(BaseRelationshipProperties):
    """关联关系属性"""
    
    strength: float = Field(..., ge=0.0, le=1.0, description="关联强度（0-1）")
    confidence: float = Field(..., ge=0.0, le=1.0, description="置信度（0-1）")


class Relationship(BaseRelationshipProperties):
    """关系模型"""
    
    id: str = Field(..., description="关系 ID")
    type: RelationshipType = Field(..., description="关系类型")
    from_node_id: str = Field(..., description="起始节点 ID")
    to_node_id: str = Field(..., description="目标节点 ID")
    properties: Dict[str, Any] | None = Field(default=None, description="关系属性")
    weight: float | None = Field(default=None, ge=0.0, description="关系权重")
