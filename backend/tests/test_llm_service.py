"""LLM服务测试

测试LLM分析服务的基本功能
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
import json
import time

from app.services.llm_service import (
    LLMAnalysisService,
    InteractionAnalysis,
    ErrorAnalysis,
    KnowledgePoint,
    CourseContext,
    SentimentType,
    DifficultyLevel,
)


@pytest.fixture
def mock_cache_service():
    """模拟缓存服务"""
    cache = AsyncMock()
    cache.get = AsyncMock(return_value=None)
    cache.set = AsyncMock(return_value=True)
    return cache


@pytest.fixture
def llm_service(mock_cache_service):
    """创建LLM服务实例"""
    with patch('app.services.llm_service.settings') as mock_settings:
        mock_settings.dashscope_api_key = "test-api-key"
        mock_settings.cache_enabled = True
        mock_settings.llm_retry_max = 3
        mock_settings.llm_retry_delay = 0.1
        mock_settings.qwen_model_simple = "qwen-turbo"
        mock_settings.qwen_model_medium = "qwen-plus"
        mock_settings.qwen_max_tokens = 2000
        mock_settings.qwen_temperature = 0.7
        mock_settings.cache_ttl = 3600
        
        service = LLMAnalysisService(cache_service=mock_cache_service)
        return service


class TestLLMAnalysisService:
    """LLM分析服务测试"""
    
    def test_initialization(self, llm_service):
        """测试服务初始化"""
        assert llm_service is not None
        assert llm_service.cache_enabled is True
        assert llm_service.max_retries == 3
    
    def test_generate_cache_key(self, llm_service):
        """测试缓存键生成"""
        key1 = llm_service._generate_cache_key("test", "content1")
        key2 = llm_service._generate_cache_key("test", "content1")
        key3 = llm_service._generate_cache_key("test", "content2")
        
        # 相同内容应该生成相同的键
        assert key1 == key2
        # 不同内容应该生成不同的键
        assert key1 != key3
        # 键应该包含前缀
        assert key1.startswith("test:")
    
    @pytest.mark.asyncio
    async def test_analyze_interaction_with_cache(self, llm_service, mock_cache_service):
        """测试互动分析（使用缓存）"""
        # 设置缓存返回值
        cached_data = {
            "sentiment": "positive",
            "topics": ["数学", "作业"],
            "confidence": 0.9
        }
        mock_cache_service.get = AsyncMock(return_value=json.dumps(cached_data))
        
        result = await llm_service.analyze_interaction("这是一个测试互动")
        
        assert isinstance(result, InteractionAnalysis)
        assert result.sentiment == SentimentType.POSITIVE
        assert result.topics == ["数学", "作业"]
        assert result.confidence == 0.9
    
    @pytest.mark.asyncio
    async def test_analyze_error_with_cache(self, llm_service, mock_cache_service):
        """测试错误分析（使用缓存）"""
        # 设置缓存返回值
        cached_data = {
            "error_type": "计算错误",
            "related_knowledge_points": ["加法", "减法"],
            "difficulty": "easy",
            "confidence": 0.85
        }
        mock_cache_service.get = AsyncMock(return_value=json.dumps(cached_data))
        
        context = CourseContext(
            course_id="C001",
            course_name="数学基础",
        )
        
        result = await llm_service.analyze_error("学生计算错误", context)
        
        assert isinstance(result, ErrorAnalysis)
        assert result.error_type == "计算错误"
        assert result.related_knowledge_points == ["加法", "减法"]
        assert result.difficulty == DifficultyLevel.EASY
        assert result.confidence == 0.85
    
    @pytest.mark.asyncio
    async def test_extract_knowledge_points_with_cache(self, llm_service, mock_cache_service):
        """测试知识点提取（使用缓存）"""
        # 设置缓存返回值
        cached_data = {
            "knowledge_points": [
                {
                    "id": "kp1",
                    "name": "加法",
                    "description": "基本加法运算",
                    "dependencies": []
                },
                {
                    "id": "kp2",
                    "name": "减法",
                    "description": "基本减法运算",
                    "dependencies": ["kp1"]
                }
            ]
        }
        mock_cache_service.get = AsyncMock(return_value=json.dumps(cached_data))
        
        result = await llm_service.extract_knowledge_points("课程内容")
        
        assert isinstance(result, list)
        assert len(result) == 2
        assert all(isinstance(kp, KnowledgePoint) for kp in result)
        assert result[0].name == "加法"
        assert result[1].dependencies == ["kp1"]
    
    def test_convert_interaction_to_node_properties(self, llm_service):
        """测试互动分析结果转换为节点属性"""
        analysis = InteractionAnalysis(
            sentiment=SentimentType.POSITIVE,
            topics=["数学", "作业"],
            confidence=0.9
        )
        
        properties = llm_service.convert_interaction_to_node_properties(
            analysis=analysis,
            interaction_id="I001",
            from_user_id="U001",
            to_user_id="U002",
            timestamp="2024-01-01T00:00:00Z"
        )
        
        assert properties["interaction_id"] == "I001"
        assert properties["sentiment"] == "positive"
        assert properties["topics"] == ["数学", "作业"]
        assert properties["confidence"] == 0.9
    
    def test_convert_error_to_relationship_data(self, llm_service):
        """测试错误分析结果转换为关系数据"""
        analysis = ErrorAnalysis(
            error_type="计算错误",
            related_knowledge_points=["加法", "减法"],
            difficulty=DifficultyLevel.EASY,
            confidence=0.85
        )
        
        relationships = llm_service.convert_error_to_relationship_data(
            analysis=analysis,
            student_node_id="S001",
            error_type_node_id="E001",
            knowledge_point_node_ids=["KP001", "KP002"]
        )
        
        assert len(relationships) == 3  # 1 HAS_ERROR + 2 RELATES_TO
        assert relationships[0]["type"] == "HAS_ERROR"
        assert relationships[0]["from_node_id"] == "S001"
        assert relationships[0]["to_node_id"] == "E001"
        assert relationships[1]["type"] == "RELATES_TO"
        assert relationships[2]["type"] == "RELATES_TO"
    
    def test_validate_and_recover_llm_output_valid_json(self, llm_service):
        """测试验证和恢复LLM输出（有效JSON）"""
        output = '{"field1": "value1", "field2": "value2"}'
        expected_fields = ["field1", "field2"]
        
        result = llm_service.validate_and_recover_llm_output(output, expected_fields)
        
        assert result["field1"] == "value1"
        assert result["field2"] == "value2"
    
    def test_validate_and_recover_llm_output_with_code_block(self, llm_service):
        """测试验证和恢复LLM输出（包含代码块）"""
        output = '''这是一些文字
```json
{"field1": "value1", "field2": "value2"}
```
更多文字'''
        expected_fields = ["field1", "field2"]
        
        result = llm_service.validate_and_recover_llm_output(output, expected_fields)
        
        assert result["field1"] == "value1"
        assert result["field2"] == "value2"
    
    def test_validate_and_recover_llm_output_missing_fields(self, llm_service):
        """测试验证和恢复LLM输出（缺少字段）"""
        output = '{"field1": "value1"}'
        expected_fields = ["field1", "field2"]
        
        with pytest.raises(Exception):
            llm_service.validate_and_recover_llm_output(output, expected_fields)
    
    def test_convert_knowledge_points_to_node_properties(self, llm_service):
        """测试知识点转换为节点属性"""
        knowledge_points = [
            KnowledgePoint(
                id="kp1",
                name="加法",
                description="基本加法运算",
                dependencies=[]
            ),
            KnowledgePoint(
                id="kp2",
                name="减法",
                description="基本减法运算",
                dependencies=["kp1"]
            )
        ]
        
        properties_list = llm_service.convert_knowledge_points_to_node_properties(
            knowledge_points=knowledge_points,
            course_id="C001"
        )
        
        assert len(properties_list) == 2
        assert properties_list[0]["knowledge_point_id"] == "kp1"
        assert properties_list[0]["name"] == "加法"
        assert properties_list[0]["course_id"] == "C001"
    
    def test_convert_knowledge_points_to_relationship_data(self, llm_service):
        """测试知识点转换为关系数据"""
        knowledge_points = [
            KnowledgePoint(
                id="kp1",
                name="加法",
                description="基本加法运算",
                dependencies=[]
            ),
            KnowledgePoint(
                id="kp2",
                name="减法",
                description="基本减法运算",
                dependencies=["kp1"]
            )
        ]
        
        kp_id_to_node_id = {
            "kp1": "N001",
            "kp2": "N002"
        }
        
        relationships = llm_service.convert_knowledge_points_to_relationship_data(
            knowledge_points=knowledge_points,
            course_node_id="C001",
            kp_id_to_node_id=kp_id_to_node_id
        )
        
        # 应该有2个CONTAINS关系和1个DEPENDS_ON关系
        assert len(relationships) == 3
        contains_rels = [r for r in relationships if r["type"] == "CONTAINS"]
        depends_rels = [r for r in relationships if r["type"] == "DEPENDS_ON"]
        assert len(contains_rels) == 2
        assert len(depends_rels) == 1
    
    @pytest.mark.asyncio
    async def test_extract_relationships(self, llm_service):
        """测试节点关系提取功能"""
        # 使用mock替换实际API调用
        with patch.object(llm_service, '_call_llm_with_retry') as mock_call:
            mock_call.return_value = '''{
                "relationships": [
                    {
                        "from_entity": "张三",
                        "to_entity": "李四",
                        "relationship_type": "CHAT_WITH",
                        "confidence": 0.95,
                        "properties": {
                            "message_count": 5,
                            "sentiment": "positive"
                        }
                    },
                    {
                        "from_entity": "数学101",
                        "to_entity": "分数加法",
                        "relationship_type": "CONTAINS",
                        "confidence": 0.98
                    }
                ]
            }'''
            
            text = "张三和李四经常一起讨论数学问题，张三喜欢数学101这门课。"
            entities = [
                {"text": "张三", "type": "Student"},
                {"text": "李四", "type": "Student"},
                {"text": "数学101", "type": "Course"},
                {"text": "分数加法", "type": "KnowledgePoint"}
            ]
            
            result = await llm_service.extract_relationships(text, entities)
            assert isinstance(result, list)
            assert len(result) == 2
            assert result[0]["relationship_type"] == "CHAT_WITH"
            assert result[1]["relationship_type"] == "CONTAINS"
    
    @pytest.mark.asyncio
    async def test_analyze_knowledge_statistics(self, llm_service):
        """测试知识点统计与知识热点产出"""
        # 使用mock替换实际API调用
        with patch.object(llm_service, '_call_llm_with_retry') as mock_call:
            mock_call.return_value = '''{
                "knowledge_point_counts": {
                    "分数加法": 45,
                    "分数乘法": 32,
                    "代数方程": 28
                },
                "hot_topics": [
                    {"name": "分数加法", "count": 45},
                    {"name": "分数乘法", "count": 32},
                    {"name": "代数方程", "count": 28}
                ],
                "knowledge_clusters": [
                    {
                        "name": "分数运算",
                        "knowledge_points": ["分数加法", "分数乘法", "分数除法"]
                    },
                    {
                        "name": "代数基础",
                        "knowledge_points": ["代数方程", "变量概念", "函数基础"]
                    }
                ]
            }'''
            
            records = [
                {
                    "type": "course_record",
                    "data": {
                        "content": "分数加法是数学中的重要知识点，学生需要掌握分数加法运算。"
                    }
                },
                {
                    "type": "error_record",
                    "data": {
                        "content": "学生在分数乘法中犯了错误，需要加强练习。"
                    }
                }
            ]
            
            result = await llm_service.analyze_knowledge_statistics(records)
            assert isinstance(result, dict)
            assert "knowledge_point_counts" in result
            assert "hot_topics" in result
            assert "knowledge_clusters" in result
            assert len(result["knowledge_point_counts"]) > 0
            assert len(result["hot_topics"]) > 0
            assert len(result["knowledge_clusters"]) > 0
    
    @pytest.mark.asyncio
    async def test_analyze_student_attention(self, llm_service):
        """测试学生群体关注度统计"""
        # 使用mock替换实际API调用
        with patch.object(llm_service, '_call_llm_with_retry') as mock_call:
            mock_call.return_value = '''{
                "student_attention_scores": {
                    "张三": 85,
                    "李四": 72,
                    "王五": 65
                },
                "attention_rankings": [
                    {"name": "张三", "rank": 1},
                    {"name": "李四", "rank": 2},
                    {"name": "王五", "rank": 3}
                ],
                "social_influence": {
                    "张三": "在群体中非常活跃，经常帮助其他学生",
                    "李四": "参与度较高，主要讨论数学问题",
                    "王五": "参与度一般，主要是接收信息"
                }
            }'''
            
            records = [
                {
                    "type": "student_interaction",
                    "data": {
                        "from_user": "张三",
                        "to_user": "李四",
                        "content": "你好，我能帮你解答这个问题吗？"
                    }
                },
                {
                    "type": "student_interaction",
                    "data": {
                        "from_user": "李四",
                        "to_user": "张三",
                        "content": "谢谢你的帮助！"
                    }
                },
                {
                    "type": "teacher_interaction",
                    "data": {
                        "from_user": "老师",
                        "to_user": "张三",
                        "content": "张三同学表现很好，经常帮助其他同学。"
                    }
                }
            ]
            
            result = await llm_service.analyze_student_attention(records)
            assert isinstance(result, dict)
            assert "student_attention_scores" in result
            assert "attention_rankings" in result
            assert "social_influence" in result
            assert len(result["student_attention_scores"]) > 0
            assert len(result["attention_rankings"]) > 0
            assert len(result["social_influence"]) > 0
    
    def test_circuit_breaker(self, llm_service):
        """测试断路器模式"""
        # 获取断路器实例
        circuit_breaker = llm_service.circuit_breaker
        
        # 初始状态应该是关闭的
        assert circuit_breaker.is_open is False
        
        # 测试成功调用
        circuit_breaker.after_success()
        assert circuit_breaker.is_open is False
        
        # 测试失败调用，未达到阈值
        for _ in range(4):
            circuit_breaker.after_failure()
        assert circuit_breaker.is_open is False
        
        # 测试失败调用，达到阈值，断路器打开
        circuit_breaker.after_failure()
        assert circuit_breaker.is_open is True
        
        # 测试断路器打开时的请求检查
        assert circuit_breaker.before_request() is False
        
        # 模拟超时，断路器半开
        circuit_breaker.last_failure_time = time.time() - 31  # 超过30秒恢复时间
        assert circuit_breaker.before_request() is True
        assert circuit_breaker.is_open is False
