"""LLM分析服务

提供与大语言模型的交互能力，用于分析教育数据并生成知识图谱节点。
"""

from typing import Any, Dict, List, Optional, Tuple
from enum import Enum
from dataclasses import dataclass
from pydantic import BaseModel, Field
import structlog
from app.config import settings
import asyncio
import time
import hashlib
from functools import wraps

logger = structlog.get_logger(__name__)


class SentimentType(str, Enum):
    """互动情感类型"""

    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"


class DifficultyLevel(str, Enum):
    """错误难度等级"""

    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class InteractionAnalysis(BaseModel):
    """互动分析结果

    包含情感、主题和互动类型的分析结果
    """

    sentiment: SentimentType
    topics: List[str]
    interactionType: str = Field(..., alias="interaction_type")
    confidence: float

    class Config:
        populate_by_name = True


class ErrorAnalysis(BaseModel):
    """错误分析结果

    包含错误类型、相关知识点和难度等信息
    """

    error_type: str
    related_knowledge_points: List[str]
    difficulty: DifficultyLevel
    severity: str
    confidence: float
    course_context: str


class KnowledgePoint(BaseModel):
    """知识点

    包含知识点的基本信息和依赖关系
    """

    id: str
    name: str
    description: str
    dependencies: List[str] = Field(default_factory=list)
    category: Optional[str] = None
    embedding: Optional[List[float]] = None


class ClassifiedData(BaseModel):
    """分类后的数据

    包含有效和无效记录，以及提取的实体
    """

    valid_records: List[Dict[str, Any]]
    invalid_records: List[Dict[str, Any]]
    entities: List[Dict[str, Any]]
    confidence: float


class ExtractedEntity(BaseModel):
    """提取的实体

    包含实体文本、类型和置信度
    """

    text: str
    type: str
    confidence: float
    embedding: Optional[List[float]] = None


class EntityMergeResult(BaseModel):
    """实体合并结果

    包含主要实体和重复实体
    """

    primary_entity: ExtractedEntity
    duplicate_entities: List[ExtractedEntity]
    similarity_score: float


class AnalysisRequest(BaseModel):
    """分析请求

    用于批量分析的请求结构
    """

    type: str
    data: Dict[str, Any]


class AnalysisResult(BaseModel):
    """分析结果

    批量分析的结果结构
    """

    request_id: str
    success: bool
    result: Optional[Any] = None
    error: Optional[str] = None


class LLMAnalysisService:
    """LLM分析服务

    提供与大语言模型的交互能力，用于分析教育数据并生成知识图谱节点。
    """

    def __init__(self, cache_service=None):
        """初始化LLM分析服务

        设置API凭证、配置和缓存

        Args:
            cache_service: 缓存服务实例，用于缓存LLM响应
        """
        self._initialized = False
        self._cache_service = cache_service
        self._api_key = settings.dashscope_api_key
        self._base_url = (
            "https://dashscope.aliyuncs.com/api/v1"  # 默认DashScope API地址
        )
        self._timeout = 30  # 默认超时30秒
        self._max_retries = settings.llm_retry_max  # 从配置获取最大重试次数
        self._rate_limit = settings.llm_rate_limit  # 从配置获取速率限制
        self._last_request_time = 0.0
        self._request_interval = 60.0 / self._rate_limit  # 请求间隔（秒）

        # 配置模型
        self._models = {
            "turbo": settings.qwen_model_simple,
            "instruct": settings.qwen_model_medium,
            "embedding": "text-embedding-v2",
        }

        logger.info(
            "llm_service_initialized",
            models=self._models,
            timeout=self._timeout,
            max_retries=self._max_retries,
            rate_limit=self._rate_limit,
            cache_enabled=self._cache_service is not None,
        )

    async def connect(self) -> None:
        """建立连接

        初始化服务，建立与外部服务的连接
        """
        if self._initialized:
            logger.warning("llm_service_already_initialized")
            return

        try:
            # 在这里可以添加API连接测试
            logger.info("llm_service_connected")
            self._initialized = True
        except Exception as e:
            logger.error("llm_service_connection_failed", error=str(e))
            raise

    def _rate_limit_decorator(func):
        """速率限制装饰器

        确保API调用不超过速率限制
        """

        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            current_time = time.time()
            time_since_last_request = current_time - self._last_request_time

            if time_since_last_request < self._request_interval:
                await asyncio.sleep(self._request_interval - time_since_last_request)

            self._last_request_time = time.time()
            return await func(self, *args, **kwargs)

        return wrapper

    def _generate_request_id(self, data: Any) -> str:
        """生成请求ID

        基于请求数据生成唯一ID，用于缓存和日志记录
        """
        data_str = str(data)
        return hashlib.md5(data_str.encode()).hexdigest()

    async def _call_api(self, model: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """调用大语言模型API

        Args:
            model: 模型名称
            payload: API请求负载

        Returns:
            API响应结果

        Raises:
            Exception: API调用失败时抛出
        """
        retry_count = 0
        backoff_factor = 1

        while retry_count < self._max_retries:
            try:
                # 这里实现实际的API调用
                # 目前使用模拟实现，后续替换为真实的DashScope API调用
                logger.info(
                    "calling_llm_api",
                    model=model,
                    payload_len=len(str(payload)),
                    retry_count=retry_count,
                )

                # 模拟API调用延迟
                await asyncio.sleep(0.1)

                # 模拟API响应
                response = {
                    "request_id": self._generate_request_id(payload),
                    "output": {"text": "", "finish_reason": "stop"},
                    "usage": {
                        "prompt_tokens": 100,
                        "completion_tokens": 200,
                        "total_tokens": 300,
                    },
                    "model": model,
                }

                logger.info(
                    "llm_api_call_successful",
                    request_id=response["request_id"],
                    model=model,
                    tokens_used=response["usage"]["total_tokens"],
                )

                return response
            except Exception as e:
                retry_count += 1
                logger.error(
                    "llm_api_call_failed",
                    model=model,
                    error=str(e),
                    retry_count=retry_count,
                    max_retries=self._max_retries,
                )

                if retry_count < self._max_retries:
                    wait_time = backoff_factor * (2 ** (retry_count - 1)) + (
                        retry_count % 2
                    )
                    logger.info(
                        "retrying_llm_api_call",
                        model=model,
                        wait_time=wait_time,
                        retry_count=retry_count,
                    )
                    await asyncio.sleep(wait_time)
                else:
                    logger.error(
                        "llm_api_call_failed_after_max_retries",
                        model=model,
                        error=str(e),
                        max_retries=self._max_retries,
                    )
                    raise

    @_rate_limit_decorator
    async def analyze_interaction(self, text: str) -> InteractionAnalysis:
        """分析互动内容

        使用大语言模型分析互动文本，识别情感、主题和互动类型

        Args:
            text: 互动内容文本

        Returns:
            互动分析结果
        """
        logger.info("analyzing_interaction", text_length=len(text))

        # 构建提示词
        prompt = f"""
        请分析以下互动内容，输出JSON格式结果，包含：
        1. sentiment: 情感（positive/neutral/negative）
        2. topics: 主题列表
        3. interaction_type: 互动类型（chat/like/teaching）
        4. confidence: 置信度（0-1）
        
        互动内容：{text}
        """

        # 调用API
        response = await self._call_api(
            model=self._models["turbo"],
            payload={
                "messages": [
                    {
                        "role": "system",
                        "content": "你是一个教育数据分析专家，擅长分析互动内容。",
                    },
                    {"role": "user", "content": prompt},
                ],
                "temperature": 0.3,
                "top_p": 0.8,
            },
        )

        # 解析响应（模拟实现，实际应解析API返回的JSON）
        analysis_result = InteractionAnalysis(
            sentiment=SentimentType.NEUTRAL,
            topics=["education", "interaction"],
            interaction_type="chat",
            confidence=0.9,
        )

        logger.info(
            "interaction_analysis_completed",
            sentiment=analysis_result.sentiment,
            topics_count=len(analysis_result.topics),
            confidence=analysis_result.confidence,
        )

        return analysis_result

    @_rate_limit_decorator
    async def analyze_error(
        self, error_text: str
    ) -> ErrorAnalysis:
        """分析错误记录

        使用大语言模型分析错误文本，识别错误类型和相关知识点

        Args:
            error_text: 错误记录文本

        Returns:
            错误分析结果
        """
        logger.info(
            "analyzing_error",
            error_text_length=len(error_text),
        )

        # 构建提示词
        context_str = ""

        prompt = f"""
        请分析以下错误记录，输出JSON格式结果，包含：
        1. error_type: 错误类型
        2. related_knowledge_points: 相关知识点列表
        3. difficulty: 难度等级（easy/medium/hard）
        4. severity: 严重程度（low/medium/high）
        5. confidence: 置信度（0-1）
        6. course_context: 课程上下文
        
        错误记录：{error_text}
        """

        # 调用API
        response = await self._call_api(
            model=self._models["instruct"],
            payload={
                "messages": [
                    {
                        "role": "system",
                        "content": "你是一个教育数据分析专家，擅长分析错误记录和识别知识点。",
                    },
                    {"role": "user", "content": prompt},
                ],
                "temperature": 0.3,
                "top_p": 0.8,
            },
        )

        # 解析响应（模拟实现，实际应解析API返回的JSON）
        analysis_result = ErrorAnalysis(
            error_type="syntax_error",
            related_knowledge_points=["变量声明", "语法规则"],
            difficulty=DifficultyLevel.EASY,
            severity="low",
            confidence=0.85,
            course_context=context_str,
        )

        logger.info(
            "error_analysis_completed",
            error_type=analysis_result.error_type,
            knowledge_points_count=len(analysis_result.related_knowledge_points),
            difficulty=analysis_result.difficulty,
            confidence=analysis_result.confidence,
        )

        return analysis_result

    @_rate_limit_decorator
    async def extract_knowledge_points(
        self, course_content: str
    ) -> List[KnowledgePoint]:
        """提取知识点

        从课程内容中提取知识点及其依赖关系

        Args:
            course_content: 课程内容文本

        Returns:
            提取的知识点列表
        """
        logger.info("extracting_knowledge_points", content_length=len(course_content))

        # 构建提示词
        prompt = f"""
        请从以下课程内容中提取知识点，输出JSON格式结果，每个知识点包含：
        1. id: 唯一标识符
        2. name: 知识点名称
        3. description: 知识点描述
        4. dependencies: 依赖的知识点列表
        5. category: 知识点分类（可选）
        
        课程内容：{course_content}
        """

        # 调用API
        response = await self._call_api(
            model=self._models["instruct"],
            payload={
                "messages": [
                    {
                        "role": "system",
                        "content": "你是一个教育数据分析专家，擅长从课程内容中提取知识点。",
                    },
                    {"role": "user", "content": prompt},
                ],
                "temperature": 0.2,
                "top_p": 0.8,
            },
        )

        # 解析响应（模拟实现，实际应解析API返回的JSON）
        knowledge_points = [
            KnowledgePoint(
                id="kp_001",
                name="变量声明",
                description="用于声明和初始化变量的语法规则",
                dependencies=[],
                category="语法基础",
            ),
            KnowledgePoint(
                id="kp_002",
                name="条件语句",
                description="根据条件执行不同代码块的结构",
                dependencies=["kp_001"],
                category="控制结构",
            ),
        ]

        logger.info("knowledge_points_extracted", count=len(knowledge_points))

        return knowledge_points

    @_rate_limit_decorator
    async def generate_embedding(self, text: str) -> List[float]:
        """生成文本嵌入向量

        为文本生成向量嵌入，用于相似性匹配和聚类

        Args:
            text: 要生成嵌入的文本

        Returns:
            文本嵌入向量
        """
        logger.info("generating_embedding", text_length=len(text))

        # 调用API
        response = await self._call_api(
            model=self._models["embedding"], payload={"input": text}
        )

        # 生成模拟嵌入向量
        embedding = [0.1] * 1024

        logger.info("embedding_generated", dimension=len(embedding))

        return embedding

    async def screen_and_classify_data(
        self, records: List[Dict[str, Any]]
    ) -> ClassifiedData:
        """筛查和分类数据

        使用LLM筛查和分类结构化数据

        Args:
            records: 原始数据记录列表

        Returns:
            分类后的数据
        """
        logger.info("screening_and_classifying_data", record_count=len(records))

        # 模拟实现
        valid_records = records
        invalid_records = []
        entities = []

        logger.info(
            "data_screening_completed",
            valid_count=len(valid_records),
            invalid_count=len(invalid_records),
            entities_count=len(entities),
        )

        return ClassifiedData(
            valid_records=valid_records,
            invalid_records=invalid_records,
            entities=entities,
            confidence=0.9,
        )

    async def analyze_batch(
        self, requests: List[AnalysisRequest]
    ) -> List[AnalysisResult]:
        """批量分析请求

        批量处理多个分析请求，支持速率限制和错误处理

        Args:
            requests: 分析请求列表

        Returns:
            分析结果列表
        """
        logger.info("starting_batch_analysis", request_count=len(requests))

        results = []

        for request in requests:
            request_id = self._generate_request_id(request)

            try:
                if request.type == "interaction":
                    result = await self.analyze_interaction(request.data["text"])
                elif request.type == "error":
                    result = await self.analyze_error(
                        request.data["error_text"]
                    )
                elif request.type == "knowledge_points":
                    result = await self.extract_knowledge_points(
                        request.data["course_content"]
                    )
                else:
                    raise ValueError(f"Unknown request type: {request.type}")

                results.append(
                    AnalysisResult(
                        request_id=request_id, success=True, result=result.model_dump()
                    )
                )
            except Exception as e:
                logger.error(
                    "batch_analysis_request_failed",
                    request_id=request_id,
                    request_type=request.type,
                    error=str(e),
                )
                results.append(
                    AnalysisResult(request_id=request_id, success=False, error=str(e))
                )

        logger.info(
            "batch_analysis_completed",
            total_requests=len(requests),
            successful=sum(1 for r in results if r.success),
            failed=sum(1 for r in results if not r.success),
        )

        return results

    async def detect_similar_entities(
        self, entities: List[ExtractedEntity]
    ) -> List[EntityMergeResult]:
        """检测相似实体

        基于嵌入向量检测和合并相似实体

        Args:
            entities: 实体列表

        Returns:
            实体合并结果列表
        """
        logger.info("detecting_similar_entities", entity_count=len(entities))

        # 模拟实现
        merge_results = []

        logger.info(
            "similar_entities_detection_completed", merge_count=len(merge_results)
        )

        return merge_results

    async def analyze_learning_behavior(
        self, behavior_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """分析学习行为

        分析学习行为数据，推断认知特征

        Args:
            behavior_data: 学习行为数据

        Returns:
            认知推断结果
        """
        logger.info("analyzing_learning_behavior")

        # 模拟实现
        result = {
            "inferred_learning_style": {
                "visual_auditory": 0.5,
                "active_reflective": -0.2,
            },
            "inferred_engagement": {"emotional": 0.8, "behavioral": 0.7},
            "confidence": 0.85,
        }

        return result

    async def assess_learning_style(
        self, learning_history: Dict[str, Any]
    ) -> Dict[str, Any]:
        """评估学习风格

        基于学习历史评估学习风格

        Args:
            learning_history: 学习历史数据

        Returns:
            学习风格评估结果
        """
        logger.info("assessing_learning_style")

        # 模拟实现
        result = {
            "visual_auditory": 0.5,
            "verbal_nonverbal": -0.3,
            "active_reflective": -0.2,
            "sensing_intuitive": 0.4,
            "sequential_global": -0.1,
            "confidence": 0.8,
        }

        return result

    async def analyze_learning_engagement(
        self, interaction_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """分析学习投入

        分析学习投入水平

        Args:
            interaction_data: 互动数据

        Returns:
            学习投入分析结果
        """
        logger.info("analyzing_learning_engagement")

        # 模拟实现
        result = {
            "emotional_engagement": 0.8,
            "behavioral_engagement": 0.7,
            "cognitive_engagement": 0.6,
            "overall_engagement": 0.7,
            "risk_factors": [],
            "strengths": ["high emotional engagement"],
        }

        return result

    async def assess_cognitive_load(
        self, task_data: Dict[str, Any], performance_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """评估认知负荷

        评估认知负荷水平

        Args:
            task_data: 任务数据
            performance_data: 表现数据

        Returns:
            认知负荷评估结果
        """
        logger.info("assessing_cognitive_load")

        # 模拟实现
        result = {
            "intrinsic_load": 0.6,
            "extraneous_load": 0.4,
            "germane_load": 0.5,
            "total_load": 1.5,
            "recommendations": ["simplify task instructions"],
        }

        return result

    async def analyze_higher_order_thinking(
        self, problem_solving_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """分析高阶思维能力

        分析高阶思维能力表现

        Args:
            problem_solving_data: 问题解决数据

        Returns:
            高阶思维能力分析结果
        """
        logger.info("analyzing_higher_order_thinking")

        # 模拟实现
        result = {
            "abstraction": 0.7,
            "decomposition": 0.6,
            "algorithmic_thinking": 0.8,
            "evaluation": 0.5,
            "generalization": 0.6,
            "evidence_examples": ["used algorithmic approach"],
        }

        return result

    async def assess_human_ai_trust(
        self, interaction_patterns: Dict[str, Any]
    ) -> Dict[str, Any]:
        """评估人机信任度

        基于互动模式评估人机信任度

        Args:
            interaction_patterns: 互动模式数据

        Returns:
            人机信任度评估结果
        """
        logger.info("assessing_human_ai_trust")

        # 模拟实现
        result = {
            "reliability_trust": 0.8,
            "competence_trust": 0.7,
            "predictability_trust": 0.6,
            "transparency_trust": 0.5,
            "benevolence_trust": 0.7,
            "overall_trust": 0.7,
        }

        return result

    async def generate_personalized_recommendations(
        self, cognitive_profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """生成个性化学习建议

        基于认知画像生成个性化学习建议

        Args:
            cognitive_profile: 认知画像数据

        Returns:
            个性化学习建议
        """
        logger.info("generating_personalized_recommendations")

        # 模拟实现
        result = {
            "personalized_content": ["visual learning materials"],
            "learning_strategies": ["active recall"],
            "difficulty_adjustments": ["start with easy tasks"],
            "motivational_support": ["gamification elements"],
            "cognitive_support": ["chunking strategies"],
            "intervention_suggestions": ["weekly progress checks"],
        }

        return result


# 全局LLM服务实例
llm_service: Optional[LLMAnalysisService] = None


async def init_llm_service() -> None:
    """初始化LLM服务

    创建并初始化全局LLM服务实例
    """
    global llm_service

    if llm_service is None:
        logger.info("initializing_llm_service")
        llm_service = LLMAnalysisService()
        await llm_service.connect()
        logger.info("llm_service_initialized_successfully")


def get_llm_service() -> LLMAnalysisService:
    """获取LLM服务实例

    Returns:
        LLM分析服务实例

    Raises:
        RuntimeError: 如果服务未初始化
    """
    if llm_service is None:
        raise RuntimeError("LLM service not initialized")
    return llm_service
