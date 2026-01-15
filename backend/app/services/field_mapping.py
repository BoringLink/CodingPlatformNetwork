"""字段映射模块"""

from typing import Dict, Type, Any, Optional
from pydantic import BaseModel
from app.models.nodes import (
    NodeType,
    StudentNodeProperties,
    TeacherNodeProperties,
    KnowledgePointNodeProperties,
)


class FieldMapping:
    """字段映射类，用于生成和管理字段映射关系"""

    def __init__(self):
        """初始化字段映射"""
        self.mappings: Dict[NodeType, Dict[str, str]] = {
            NodeType.STUDENT: self._generate_mapping(StudentNodeProperties),
            NodeType.TEACHER: self._generate_mapping(TeacherNodeProperties),
            NodeType.KNOWLEDGE_POINT: self._generate_mapping(
                KnowledgePointNodeProperties
            ),
        }

        # 业务术语映射
        self.term_mappings = {
            # 现有翻译
            "gender": {"male": "男性", "female": "女性", "other": "其他"},
            "difficulty": {
                "beginner": "初级",
                "intermediate": "中级",
                "advanced": "高级",
            },
            "severity": {"low": "低", "medium": "中", "high": "高"},
            # 节点类型
            "node_type": {
                "Student": "学生",
                "Teacher": "教师",
                "KnowledgePoint": "知识点",
            },
            # 深度学习方法
            "deep_learning": {
                "meaning_construction": "意义建构",
                "critical_thinking": "批判思维",
                "connection_making": "联系建立",
                "reflective_practice": "反思实践",
            },
            # 策略学习方法
            "strategic_learning": {
                "goal_setting": "目标设定",
                "planning_organization": "计划组织",
                "monitoring_regulation": "监控调节",
                "resource_management": "资源管理",
            },
            # 浅表学习方法
            "surface_learning": {
                "memorization": "机械记忆",
                "repetition_practice": "重复练习",
                "passive_reception": "被动接受",
                "minimum_effort": "最小努力",
            },
            # 学习风格维度
            "learning_style": {
                "visual_auditory": "视觉-听觉偏好",
                "verbal_nonverbal": "言语-非言语偏好",
                "active_reflective": "主动-反思偏好",
                "sensing_intuitive": "感知-直觉偏好",
                "sequential_global": "序列-整体偏好",
                "inductive_deductive": "归纳-演绎偏好",
                "cooperative_competitive": "合作-竞争偏好",
                "structured_flexible": "结构化-灵活偏好",
                "concrete_abstract": "具体-抽象偏好",
                "field_dependent_independent": "场依存-场独立",
                "impulsive_reflective": "冲动-反思偏好",
            },
            # 外部认知负荷
            "extraneous_cognitive_load": {
                "interface_complexity": "界面复杂度感知",
                "information_overload": "信息过载程度",
                "distraction_level": "干扰水平",
                "task_irrelevance": "任务无关性",
                "presentation_clarity": "呈现清晰度",
            },
            # 内部认知负荷
            "intrinsic_cognitive_load": {
                "task_difficulty": "任务难度感知",
                "concept_complexity": "概念复杂度",
                "mental_effort": "心理努力程度",
            },
            # 学习动机
            "learning_motivation": {
                "intrinsic_motivation": "内在动机",
                "extrinsic_motivation": "外在动机",
                "achievement_motivation": "成就动机",
                "social_motivation": "社会动机",
                "avoidance_motivation": "回避动机",
            },
            # 抽象能力
            "abstraction": {
                "pattern_recognition": "模式识别",
                "conceptualization": "概念化能力",
                "generalization": "泛化能力",
                "symbolization": "符号化能力",
            },
            # 分解能力
            "decomposition": {
                "problem_breakdown": "问题分解",
                "structural_analysis": "结构分析",
                "component_identification": "组件识别",
            },
            # 算法思维
            "algorithmic_thinking": {
                "sequential_logic": "序列逻辑",
                "conditional_reasoning": "条件推理",
                "iterative_thinking": "迭代思维",
                "optimization_mindset": "优化思维",
            },
            # 评价能力
            "evaluation": {
                "critical_analysis": "批判分析",
                "evidence_assessment": "证据评估",
                "quality_judgment": "质量判断",
                "validity_checking": "有效性检查",
            },
            # 泛化能力
            "generalization": {
                "transfer_learning": "迁移学习",
                "analogical_reasoning": "类比推理",
                "principle_extraction": "原理提取",
                "application_scope": "应用范围",
            },
            # 人机信任度
            "human_ai_trust": {
                "reliability_trust": "可靠性信任",
                "competence_trust": "能力信任",
                "predictability_trust": "可预测性信任",
                "transparency_trust": "透明度信任",
                "benevolence_trust": "善意信任",
                "overall_trust": "整体信任",
            },
            # 情感投入
            "emotional_engagement": {
                "interest": "学习兴趣",
                "enjoyment": "学习享受度",
                "satisfaction": "学习满意度",
            },
            # 行为投入
            "behavioral_engagement": {
                "participation": "参与度",
                "effort": "努力程度",
                "persistence": "坚持性",
            },
            # 认知投入
            "cognitive_engagement": {
                "deep_thinking": "深度思考",
                "strategic_learning": "策略学习",
                "self_regulation": "自我调节",
            },
            # 学习态度
            "learning_attitude": {"enjoyment": "享受度", "confidence": "自信心"},
            # 学习行为数据
            "learning_behavior_data": {
                "ai_interaction_count": "和大模型交互次数",
                "error_execution_count": "错误运行次数",
                "session_duration": "学习会话时长(分钟)",
                "resource_access_count": "资源访问次数",
                "help_seeking_frequency": "求助频率",
                "task_completion_rate": "任务完成率",
                "last_active_date": "最后活跃时间",
            },
            # 先前知识储备
            "prior_knowledge": {
                "elementary": "小学知识掌握度",
                "junior_high": "初中知识掌握度",
                "senior_high": "高中知识掌握度",
                "university": "大学知识掌握度",
                "professional": "专业知识掌握度",
                "assessment_date": "评估时间",
            },
        }

    def _generate_mapping(
        self, model_class: Type[BaseModel], prefix: str = ""
    ) -> Dict[str, str]:
        """从Pydantic模型中生成字段映射

        Args:
            model_class: Pydantic模型类
            prefix: 父字段前缀

        Returns:
            字段映射字典
        """
        mapping = {}

        for field_name, field in model_class.model_fields.items():
            field_desc = field.description or field_name
            full_field_name = f"{prefix}{field_name}" if prefix else field_name
            full_desc = f"{prefix}{field_desc}" if prefix else field_desc

            # 处理嵌套模型
            annotation = field.annotation
            # 检查是否为Optional类型
            if hasattr(annotation, "__origin__") and annotation.__origin__ is Optional:
                annotation = annotation.__args__[0]

            if isinstance(annotation, type) and issubclass(annotation, BaseModel):
                # 嵌套模型，递归生成映射
                nested_mapping = self._generate_mapping(
                    annotation, f"{full_field_name}."
                )
                mapping.update(nested_mapping)
            else:
                # 普通字段，直接添加映射
                mapping[full_field_name] = full_desc

        return mapping

    def get_mapping(self, node_type: NodeType) -> Dict[str, str]:
        """获取指定节点类型的字段映射

        Args:
            node_type: 节点类型

        Returns:
            字段映射字典
        """
        return self.mappings.get(node_type, {})

    def get_term_mapping(self, field_name: str, value: Any) -> Any:
        """获取业务术语映射

        Args:
            field_name: 字段名
            value: 字段值

        Returns:
            映射后的值
        """
        # 提取字段名（去除嵌套前缀）
        simple_field_name = field_name.split(".")[-1]
        if simple_field_name in self.term_mappings:
            return self.term_mappings[simple_field_name].get(value, value)
        return value


# 全局字段映射实例
field_mapping = FieldMapping()
