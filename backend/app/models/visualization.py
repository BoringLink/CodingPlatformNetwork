"""可视化数据模型"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

from app.models.nodes import NodeType
from app.models.relationships import RelationshipType


class VisualizationOptions(BaseModel):
    """可视化选项"""
    root_node_id: str = Field(..., description="根节点ID")
    depth: int = Field(default=2, ge=1, le=10, description="可视化深度")
    node_types: List[NodeType] = Field(default_factory=list, description="节点类型过滤")
    relationship_types: List[RelationshipType] = Field(default_factory=list, description="关系类型过滤")
    schools: List[str] = Field(default_factory=list, description="学校过滤")
    grades: List[int] = Field(default_factory=list, description="年级过滤")
    classes: List[str] = Field(default_factory=list, description="班级过滤")
    start_date: Optional[str] = Field(default=None, description="开始日期")
    end_date: Optional[str] = Field(default=None, description="结束日期")


class NodeVisualization(BaseModel):
    """可视化节点"""
    id: str = Field(..., description="节点ID")
    type: NodeType = Field(..., description="节点类型")
    label: str = Field(..., description="节点标签")
    properties: Dict[str, Any] = Field(default_factory=dict, description="节点属性")
    size: Optional[float] = Field(default=10, ge=5, le=50, description="节点大小")
    color: Optional[str] = Field(default=None, description="节点颜色")


class EdgeVisualization(BaseModel):
    """可视化边"""
    id: str = Field(..., description="边ID")
    type: RelationshipType = Field(..., description="关系类型")
    source: str = Field(..., description="起点节点ID")
    target: str = Field(..., description="终点节点ID")
    label: Optional[str] = Field(default=None, description="边标签")
    properties: Dict[str, Any] = Field(default_factory=dict, description="边属性")
    weight: Optional[float] = Field(default=1.0, ge=0.1, le=10.0, description="边权重")
    color: Optional[str] = Field(default=None, description="边颜色")


class GraphVisualization(BaseModel):
    """图可视化数据"""
    nodes: List[NodeVisualization] = Field(default_factory=list, description="节点列表")
    edges: List[EdgeVisualization] = Field(default_factory=list, description="边列表")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="元数据")
