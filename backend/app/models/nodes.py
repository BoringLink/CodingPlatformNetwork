"""节点数据模型"""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, field_validator

from app.models.base import BaseNodeProperties, TimestampMixin


class NodeType(str, Enum):
    """节点类型枚举"""

    STUDENT = "Student"
    TEACHER = "Teacher"
    KNOWLEDGE_POINT = "KnowledgePoint"


class BasicInfo(BaseModel):
    """基本信息维度"""

    school: str = Field(..., description="学校")
    grade: int = Field(..., ge=1, le=9, description="年级")
    class_name: str = Field(..., description="班级")


class PriorKnowledge(BaseModel):
    """先前知识储备维度"""

    elementary: int = Field(..., ge=0, le=100, description="小学知识掌握度")
    junior_high: int = Field(..., ge=0, le=100, description="初中知识掌握度")
    senior_high: int = Field(..., ge=0, le=100, description="高中知识掌握度")
    university: int = Field(..., ge=0, le=100, description="大学知识掌握度")
    professional: int = Field(..., ge=0, le=100, description="专业知识掌握度")
    assessment_date: datetime | None = Field(default=None, description="评估时间")


class EmotionalEngagement(BaseModel):
    """情感投入"""

    interest: int = Field(..., ge=1, le=5, description="学习兴趣")
    enjoyment: int = Field(..., ge=1, le=5, description="学习享受度")
    satisfaction: int = Field(..., ge=1, le=5, description="学习满意度")


class BehavioralEngagement(BaseModel):
    """行为投入"""

    participation: int = Field(..., ge=1, le=5, description="参与度")
    effort: int = Field(..., ge=1, le=5, description="努力程度")
    persistence: int = Field(..., ge=1, le=5, description="坚持性")


class CognitiveEngagement(BaseModel):
    """认知投入"""

    deep_thinking: int = Field(..., ge=1, le=5, description="深度思考")
    strategic_learning: int = Field(..., ge=1, le=5, description="策略学习")
    self_regulation: int = Field(..., ge=1, le=5, description="自我调节")


class LearningEngagement(BaseModel):
    """学习投入维度"""

    emotional_engagement: EmotionalEngagement = Field(..., description="情感投入")
    behavioral_engagement: BehavioralEngagement = Field(..., description="行为投入")
    cognitive_engagement: CognitiveEngagement = Field(..., description="认知投入")


class LearningStyle(BaseModel):
    """学习风格维度"""

    visual_auditory: int = Field(..., ge=-5, le=5, description="视觉-听觉偏好")
    verbal_nonverbal: int = Field(..., ge=-5, le=5, description="言语-非言语偏好")
    active_reflective: int = Field(..., ge=-5, le=5, description="主动-反思偏好")
    sensing_intuitive: int = Field(..., ge=-5, le=5, description="感知-直觉偏好")
    sequential_global: int = Field(..., ge=-5, le=5, description="序列-整体偏好")
    inductive_deductive: int = Field(..., ge=-5, le=5, description="归纳-演绎偏好")
    cooperative_competitive: int = Field(..., ge=-5, le=5, description="合作-竞争偏好")
    structured_flexible: int = Field(..., ge=-5, le=5, description="结构化-灵活偏好")
    concrete_abstract: int = Field(..., ge=-5, le=5, description="具体-抽象偏好")
    field_dependent_independent: int = Field(..., ge=-5, le=5, description="场依存-场独立")
    impulsive_reflective: int = Field(..., ge=-5, le=5, description="冲动-反思偏好")


class ExtraneousCognitiveLoad(BaseModel):
    """外部认知负荷"""

    interface_complexity: int = Field(..., ge=1, le=5, description="界面复杂度感知")
    information_overload: int = Field(..., ge=1, le=5, description="信息过载程度")
    distraction_level: int = Field(..., ge=1, le=5, description="干扰水平")
    task_irrelevance: int = Field(..., ge=1, le=5, description="任务无关性")
    presentation_clarity: int = Field(..., ge=1, le=5, description="呈现清晰度")


class IntrinsicCognitiveLoad(BaseModel):
    """内部认知负荷"""

    task_difficulty: int = Field(..., ge=1, le=5, description="任务难度感知")
    concept_complexity: int = Field(..., ge=1, le=5, description="概念复杂度")
    mental_effort: int = Field(..., ge=1, le=5, description="心理努力程度")


class CognitiveLoad(BaseModel):
    """认知负荷维度"""

    extraneous: ExtraneousCognitiveLoad = Field(..., description="外部认知负荷")
    intrinsic: IntrinsicCognitiveLoad = Field(..., description="内部认知负荷")


class LearningMotivation(BaseModel):
    """学习动机维度"""

    intrinsic_motivation: int = Field(..., ge=1, le=5, description="内在动机")
    extrinsic_motivation: int = Field(..., ge=1, le=5, description="外在动机")
    achievement_motivation: int = Field(..., ge=1, le=5, description="成就动机")
    social_motivation: int = Field(..., ge=1, le=5, description="社会动机")
    avoidance_motivation: int = Field(..., ge=1, le=5, description="回避动机")


class Abstraction(BaseModel):
    """抽象能力"""

    pattern_recognition: int = Field(..., ge=1, le=5, description="模式识别")
    conceptualization: int = Field(..., ge=1, le=5, description="概念化能力")
    generalization: int = Field(..., ge=1, le=5, description="泛化能力")
    symbolization: int = Field(..., ge=1, le=5, description="符号化能力")


class Decomposition(BaseModel):
    """分解能力"""

    problem_breakdown: int = Field(..., ge=1, le=5, description="问题分解")
    structural_analysis: int = Field(..., ge=1, le=5, description="结构分析")
    component_identification: int = Field(..., ge=1, le=5, description="组件识别")


class AlgorithmicThinking(BaseModel):
    """算法思维"""

    sequential_logic: int = Field(..., ge=1, le=5, description="序列逻辑")
    conditional_reasoning: int = Field(..., ge=1, le=5, description="条件推理")
    iterative_thinking: int = Field(..., ge=1, le=5, description="迭代思维")
    optimization_mindset: int = Field(..., ge=1, le=5, description="优化思维")


class Evaluation(BaseModel):
    """评价能力"""

    critical_analysis: int = Field(..., ge=1, le=5, description="批判分析")
    evidence_assessment: int = Field(..., ge=1, le=5, description="证据评估")
    quality_judgment: int = Field(..., ge=1, le=5, description="质量判断")
    validity_checking: int = Field(..., ge=1, le=5, description="有效性检查")


class Generalization(BaseModel):
    """泛化能力"""

    transfer_learning: int = Field(..., ge=1, le=5, description="迁移学习")
    analogical_reasoning: int = Field(..., ge=1, le=5, description="类比推理")
    principle_extraction: int = Field(..., ge=1, le=5, description="原理提取")
    application_scope: int = Field(..., ge=1, le=5, description="应用范围")


class HigherOrderThinking(BaseModel):
    """高阶思维维度"""

    abstraction: Abstraction = Field(..., description="抽象能力")
    decomposition: Decomposition = Field(..., description="分解能力")
    algorithmic_thinking: AlgorithmicThinking = Field(..., description="算法思维")
    evaluation: Evaluation = Field(..., description="评价能力")
    generalization: Generalization = Field(..., description="泛化能力")


class HumanAITrust(BaseModel):
    """人机信任度维度"""

    reliability_trust: int = Field(..., ge=1, le=5, description="可靠性信任")
    competence_trust: int = Field(..., ge=1, le=5, description="能力信任")
    predictability_trust: int = Field(..., ge=1, le=5, description="可预测性信任")
    transparency_trust: int = Field(..., ge=1, le=5, description="透明度信任")
    benevolence_trust: int = Field(..., ge=1, le=5, description="善意信任")
    overall_trust: int = Field(..., ge=1, le=5, description="整体信任")


class DeepLearning(BaseModel):
    """深度学习方法"""

    meaning_construction: int = Field(..., ge=1, le=5, description="意义建构")
    critical_thinking: int = Field(..., ge=1, le=5, description="批判思维")
    connection_making: int = Field(..., ge=1, le=5, description="联系建立")
    reflective_practice: int = Field(..., ge=1, le=5, description="反思实践")


class StrategicLearning(BaseModel):
    """策略学习方法"""

    goal_setting: int = Field(..., ge=1, le=5, description="目标设定")
    planning_organization: int = Field(..., ge=1, le=5, description="计划组织")
    monitoring_regulation: int = Field(..., ge=1, le=5, description="监控调节")
    resource_management: int = Field(..., ge=1, le=5, description="资源管理")


class SurfaceLearning(BaseModel):
    """浅表学习方法"""

    memorization: int = Field(..., ge=1, le=5, description="机械记忆")
    repetition_practice: int = Field(..., ge=1, le=5, description="重复练习")
    passive_reception: int = Field(..., ge=1, le=5, description="被动接受")
    minimum_effort: int = Field(..., ge=1, le=5, description="最小努力")


class LearningMethodPreference(BaseModel):
    """学习方法倾向维度"""

    deep_learning: DeepLearning = Field(..., description="深度学习方法")
    strategic_learning: StrategicLearning = Field(..., description="策略学习方法")
    surface_learning: SurfaceLearning = Field(..., description="浅表学习方法")


class LearningAttitude(BaseModel):
    """学习态度维度"""

    enjoyment: int = Field(..., ge=1, le=5, description="享受度")
    confidence: int = Field(..., ge=1, le=5, description="自信心")


class LearningBehaviorData(BaseModel):
    """学习行为数据维度"""

    ai_interaction_count: int = Field(..., ge=0, description="和大模型交互次数")
    error_execution_count: int = Field(..., ge=0, description="错误运行次数")
    session_duration: int = Field(..., ge=0, description="学习会话时长(分钟)")
    resource_access_count: int = Field(..., ge=0, description="资源访问次数")
    help_seeking_frequency: int = Field(..., ge=0, description="求助频率")
    task_completion_rate: float = Field(..., ge=0, le=1, description="任务完成率")
    last_active_date: datetime = Field(..., description="最后活跃时间")


class StudentNodeProperties(BaseNodeProperties):
    """学生节点属性"""

    id: str = Field(..., description="学生唯一标识符")
    name: str = Field(..., min_length=1, max_length=100, description="学生姓名")

    # 基本信息维度 - 扁平化属性
    basic_info_school: str = Field(..., description="学校")
    basic_info_grade: int = Field(..., ge=1, le=9, description="年级")
    basic_info_class: str = Field(..., description="班级")

    # 先前知识储备维度
    prior_knowledge: PriorKnowledge = Field(..., description="先前知识储备")

    # 学习投入维度
    learning_engagement: LearningEngagement = Field(..., description="学习投入")

    # 学习风格维度
    learning_style: LearningStyle = Field(..., description="学习风格")

    # 认知负荷维度
    cognitive_load: CognitiveLoad = Field(..., description="认知负荷")

    # 学习动机维度
    learning_motivation: LearningMotivation = Field(..., description="学习动机")

    # 高阶思维维度
    higher_order_thinking: HigherOrderThinking = Field(..., description="高阶思维")

    # 人机信任度维度
    human_ai_trust: HumanAITrust = Field(..., description="人机信任度")

    # 学习方法倾向维度
    learning_method_preference: LearningMethodPreference = Field(..., description="学习方法倾向")

    # 学习态度维度
    learning_attitude: LearningAttitude = Field(..., description="学习态度")

    # 学习行为数据维度
    learning_behavior_data: LearningBehaviorData = Field(..., description="学习行为数据")

    # 元数据和系统字段
    enrollment_date: datetime | None = Field(default=None, description="入学日期")
    last_updated: datetime = Field(default_factory=datetime.now, description="最后更新时间")
    profile_completeness: float = Field(..., ge=0, le=1, description="画像完整度")
    data_version: str = Field(..., description="数据版本")
    metadata: dict[str, Any] | None = Field(default=None, description="元数据")


class TeacherNodeProperties(BaseNodeProperties):
    """教师节点属性"""

    id: str = Field(..., description="教师唯一标识符")
    name: str = Field(..., min_length=1, max_length=100, description="教师姓名")

    # 基本信息维度 - 扁平化属性
    basic_info_school: str = Field(..., description="学校")
    basic_info_grade: int = Field(..., ge=1, le=9, description="年级")
    basic_info_class: str = Field(..., description="班级")

    grades: list[int] = Field(..., min_items=1, description="教授年级数组")

    @field_validator("grades")
    @classmethod
    def validate_grades(cls, v: list[int]) -> list[int]:
        """验证年级数组"""
        for grade in v:
            if not isinstance(grade, int) or grade < 1 or grade > 9:
                raise ValueError(f"年级必须是1-9的整数，当前值: {grade}")
        return sorted(list(set(v)))


class KnowledgePointNodeProperties(BaseNodeProperties):
    """知识点节点属性"""

    id: str = Field(..., description="知识点唯一标识符")
    name: str = Field(..., min_length=1, max_length=200, description="知识点名称")
    description: str = Field(..., description="知识点描述")
    category: str | None = Field(default=None, description="知识点分类")


class Node(TimestampMixin):
    """节点模型"""

    id: str = Field(..., description="节点 ID")
    type: NodeType = Field(..., description="节点类型")
    properties: dict[str, Any] = Field(..., description="节点属性")

    def to_dict(self) -> dict[str, Any]:
        """将节点模型转换为字典"""
        return self.model_dump()
