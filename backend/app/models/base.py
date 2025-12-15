"""基础数据模型"""

from datetime import datetime
from typing import Any, Dict
from pydantic import BaseModel, Field, ConfigDict


class BaseNodeProperties(BaseModel):
    """节点属性基类"""
    
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        use_enum_values=True,
    )
    
    metadata: Dict[str, Any] | None = Field(
        default=None,
        description="额外的元数据信息",
    )


class BaseRelationshipProperties(BaseModel):
    """关系属性基类"""
    
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        use_enum_values=True,
    )


class TimestampMixin(BaseModel):
    """时间戳混入类"""
    
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="创建时间",
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="更新时间",
    )


class ResponseModel(BaseModel):
    """API 响应基类"""
    
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )
    
    success: bool = Field(default=True, description="请求是否成功")
    message: str | None = Field(default=None, description="响应消息")


class ErrorResponse(BaseModel):
    """错误响应模型"""
    
    error: str = Field(..., description="错误类型")
    message: str = Field(..., description="错误消息")
    details: Dict[str, Any] | None = Field(default=None, description="错误详情")
