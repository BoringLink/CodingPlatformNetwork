# 阿里云模型API调用功能实现计划（最终版）

## 1. 核心需求分析

根据用户反馈，LLM模型需要完成以下核心任务：

1. **节点联系的辨别与分类**：识别和分类知识图谱中节点之间的关系
2. **知识点的统计与知识热点产出**：统计知识点出现频率，识别知识热点
3. **个体学生的群体关注度的统计**：分析学生在群体中的互动和关注度

## 2. 实现步骤

### 2.1 配置更新

1. **更新.env文件**：确保`DASHSCOPE_API_KEY`已正确配置
2. **验证配置加载**：检查配置是否正确加载到应用中
3. **模型配置检查**：确保使用适合复杂任务的模型（如qwen-2.5-72b-instruct）

### 2.2 核心功能实现

#### 2.2.1 节点联系的辨别与分类

1. **设计专门的提示词**：
   - 明确要求模型识别节点之间的关系类型
   - 提供关系类型的示例和定义
   - 要求返回结构化的关系数据

2. **实现关系提取功能**：
   - 添加`extract_relationships`方法到LLMAnalysisService
   - 支持从文本中提取多种关系类型
   - 实现关系置信度评估

3. **关系分类逻辑**：
   - 支持CHAT_WITH、LIKES、TEACHES、LEARNS、CONTAINS、HAS_ERROR、RELATES_TO等关系类型
   - 实现关系强度评估
   - 添加关系权重计算

#### 2.2.2 知识点的统计与知识热点产出

1. **设计统计分析提示词**：
   - 要求模型统计知识点出现频率
   - 识别高频知识点和知识热点
   - 分析知识点之间的关联强度

2. **实现知识点统计功能**：
   - 添加`analyze_knowledge_statistics`方法
   - 支持知识点频率统计
   - 实现知识热点识别算法

3. **知识热点产出**：
   - 生成知识点热度排名
   - 识别知识点集群和关联网络
   - 生成知识点趋势分析

#### 2.2.3 个体学生的群体关注度统计

1. **设计关注度分析提示词**：
   - 要求模型分析学生在群体中的互动情况
   - 识别学生的关注度指标
   - 分析学生的社交影响力

2. **实现关注度统计功能**：
   - 添加`analyze_student_attention`方法
   - 支持统计学生的互动次数和质量
   - 实现学生关注度排名

3. **关注度指标设计**：
   - 互动频率（聊天、点赞次数）
   - 互动质量（情感分析结果）
   - 社交影响力（被提及次数）

### 2.3 代码优化

1. **模型调用优化**：
   - 针对不同任务选择合适的模型
   - 实现高效的批量处理
   - 添加详细的调用日志

2. **错误处理增强**：
   - 实现指数退避重试机制
   - 添加断路器模式
   - 完善错误日志记录

3. **日志记录增强**：
   - 添加详细的API调用日志
   - 记录token使用情况和成本
   - 添加性能监控指标

### 2.4 测试完善

1. **单元测试**：
   - 测试节点联系辨别与分类功能
   - 测试知识点统计与知识热点功能
   - 测试学生关注度统计功能

2. **集成测试**：
   - 测试完整的知识图谱构建流程
   - 测试大规模数据处理能力
   - 测试性能和可靠性

3. **属性测试**：
   - 测试节点关系提取的准确性
   - 测试知识点统计的一致性
   - 测试学生关注度统计的合理性

## 3. 核心功能实现细节

### 3.1 节点联系的辨别与分类

```python
async def extract_relationships(self, text: str, entities: List[ExtractedEntity]) -> List[Dict[str, Any]]:
    """从文本中提取并分类节点关系
    
    Args:
        text: 包含节点关系的文本
        entities: 已识别的实体列表
    
    Returns:
        提取的关系列表，每个关系包含：
        - from_entity: 起始实体
        - to_entity: 目标实体
        - relationship_type: 关系类型
        - confidence: 置信度
        - properties: 关系属性
    """
    # 检查缓存
    cache_key = self._generate_cache_key("relationship_extraction", text, entities=[e.text for e in entities])
    cached_result = await self._get_from_cache(cache_key)
    
    if cached_result:
        return cached_result
    
    # 构建实体列表字符串
    entity_list = "\n".join([f"- {e.text} ({e.type})" for e in entities])
    
    # 设计提示词
    prompt = f"""请从以下文本中识别并分类实体之间的关系。

已知实体：
{entity_list}

文本内容：
{text}

请识别实体之间的关系，可能的关系类型包括：
1. CHAT_WITH：学生之间的聊天互动
2. LIKES：学生之间的点赞互动
3. TEACHES：教师对学生的教学关系
4. LEARNS：学生对课程的学习关系
5. CONTAINS：课程包含知识点的关系
6. HAS_ERROR：学生犯错误的关系
7. RELATES_TO：错误类型与知识点的关联关系

请以JSON格式返回关系列表，每个关系包含：
- from_entity: 起始实体文本
- to_entity: 目标实体文本
- relationship_type: 关系类型
- confidence: 置信度（0-1之间的浮点数）
- properties: 关系属性（可选，如互动次数、情感等）

示例输出：
{{
  "relationships": [
    {{
      "from_entity": "张三",
      "to_entity": "李四",
      "relationship_type": "CHAT_WITH",
      "confidence": 0.95,
      "properties": {{
        "message_count": 5,
        "sentiment": "positive"
      }}
    }},
    {{
      "from_entity": "数学101",
      "to_entity": "分数加法",
      "relationship_type": "CONTAINS",
      "confidence": 0.98
    }}
  ]
}}

请只返回JSON，不要包含其他文字。"""
    
    # 调用模型
    response_text = self._call_llm_with_retry(
        model=settings.qwen_model_complex,
        prompt=prompt,
        max_tokens=1000,
    )
    
    # 解析结果
    result = json.loads(response_text)
    relationships = result.get("relationships", [])
    
    # 缓存结果
    await self._set_to_cache(cache_key, relationships)
    
    return relationships
```

### 3.2 知识点的统计与知识热点产出

```python
async def analyze_knowledge_statistics(self, records: List[RawRecord]) -> Dict[str, Any]:
    """分析知识点统计数据和知识热点
    
    Args:
        records: 包含知识点的记录列表
    
    Returns:
        知识点统计结果，包含：
        - knowledge_point_counts: 知识点出现次数统计
        - hot_topics: 知识热点列表
        - knowledge_clusters: 知识点集群
    """
    # 提取所有文本内容
    text_content = "\n".join([record.data.get("content", "") for record in records if record.data.get("content")])
    
    # 检查缓存
    cache_key = self._generate_cache_key("knowledge_statistics", text_content)
    cached_result = await self._get_from_cache(cache_key)
    
    if cached_result:
        return cached_result
    
    # 设计提示词
    prompt = f"""请分析以下教育数据中的知识点统计信息和知识热点。

数据内容：
{text_content}

请完成以下任务：
1. 统计每个知识点出现的频率
2. 识别前10个高频知识点（知识热点）
3. 分析知识点之间的关联，识别知识点集群

请以JSON格式返回结果，包含：
- knowledge_point_counts: 知识点出现次数统计（对象，键为知识点名称，值为出现次数）
- hot_topics: 知识热点列表（数组，包含知识点名称和出现次数）
- knowledge_clusters: 知识点集群（数组，每个集群包含集群名称和相关知识点列表）

示例输出：
{{
  "knowledge_point_counts": {{
    "分数加法": 45,
    "分数乘法": 32,
    "代数方程": 28
  }},
  "hot_topics": [
    {{"name": "分数加法", "count": 45}},
    {{"name": "分数乘法", "count": 32}},
    {{"name": "代数方程", "count": 28}}
  ],
  "knowledge_clusters": [
    {{
      "name": "分数运算",
      "knowledge_points": ["分数加法", "分数乘法", "分数除法"]
    }},
    {{
      "name": "代数基础",
      "knowledge_points": ["代数方程", "变量概念", "函数基础"]
    }}
  ]
}}

请只返回JSON，不要包含其他文字。"""
    
    # 调用模型
    response_text = self._call_llm_with_retry(
        model=settings.qwen_model_complex,
        prompt=prompt,
        max_tokens=1500,
    )
    
    # 解析结果
    result = json.loads(response_text)
    
    # 缓存结果
    await self._set_to_cache(cache_key, result)
    
    return result
```

### 3.3 个体学生的群体关注度统计

```python
async def analyze_student_attention(self, records: List[RawRecord]) -> Dict[str, Any]:
    """分析个体学生的群体关注度
    
    Args:
        records: 包含学生互动的记录列表
    
    Returns:
        学生关注度统计结果，包含：
        - student_attention_scores: 学生关注度分数
        - attention_rankings: 学生关注度排名
        - social_influence: 学生社交影响力分析
    """
    # 提取学生互动文本
    interaction_texts = []
    for record in records:
        if record.type in ["student_interaction", "teacher_interaction"]:
            interaction_texts.append(str(record.data))
    
    interaction_content = "\n".join(interaction_texts)
    
    # 检查缓存
    cache_key = self._generate_cache_key("student_attention", interaction_content)
    cached_result = await self._get_from_cache(cache_key)
    
    if cached_result:
        return cached_result
    
    # 设计提示词
    prompt = f"""请分析以下学生互动数据，统计个体学生的群体关注度。

互动数据：
{interaction_content}

请完成以下任务：
1. 识别所有学生个体
2. 统计每个学生的互动次数和质量
3. 计算每个学生的群体关注度分数（0-100）
4. 生成学生关注度排名
5. 分析学生的社交影响力

请以JSON格式返回结果，包含：
- student_attention_scores: 学生关注度分数（对象，键为学生名称，值为关注度分数）
- attention_rankings: 学生关注度排名（数组，包含学生名称和排名）
- social_influence: 学生社交影响力分析（对象，键为学生名称，值为影响力描述）

示例输出：
{{
  "student_attention_scores": {{
    "张三": 85,
    "李四": 72,
    "王五": 65
  }},
  "attention_rankings": [
    {{"name": "张三", "rank": 1}},
    {{"name": "李四", "rank": 2}},
    {{"name": "王五", "rank": 3}}
  ],
  "social_influence": {{
    "张三": "在群体中非常活跃，经常帮助其他学生",
    "李四": "参与度较高，主要讨论数学问题",
    "王五": "参与度一般，主要是接收信息"
  }}
}}

请只返回JSON，不要包含其他文字。"""
    
    # 调用模型
    response_text = self._call_llm_with_retry(
        model=settings.qwen_model_complex,
        prompt=prompt,
        max_tokens=1500,
    )
    
    # 解析结果
    result = json.loads(response_text)
    
    # 缓存结果
    await self._set_to_cache(cache_key, result)
    
    return result
```

## 4. 测试策略

### 4.1 单元测试

```python
@pytest.mark.asyncio
async def test_extract_relationships(self, llm_service):
    """测试节点关系提取功能"""
    text = "张三和李四经常一起讨论数学问题，张三喜欢数学101这门课。"
    entities = [
        {"text": "张三", "type": "Student"},
        {"text": "李四", "type": "Student"},
        {"text": "数学101", "type": "Course"}
    ]
    
    with patch.object(llm_service, '_call_llm_with_retry') as mock_call:
        mock_call.return_value = '''{
            "relationships": [
                {
                    "from_entity": "张三",
                    "to_entity": "李四",
                    "relationship_type": "CHAT_WITH",
                    "confidence": 0.95
                },
                {
                    "from_entity": "张三",
                    "to_entity": "数学101",
                    "relationship_type": "LEARNS",
                    "confidence": 0.9
                }
            ]
        }'''
        
        result = await llm_service.extract_relationships(text, entities)
        assert len(result) == 2
        assert result[0]["relationship_type"] == "CHAT_WITH"
        assert result[1]["relationship_type"] == "LEARNS"
```

### 4.2 集成测试

```python
@pytest.mark.asyncio
async def test_knowledge_graph_building_pipeline(self):
    """测试完整的知识图谱构建流程"""
    # 创建测试数据
    records = [
        {
            "type": "student_interaction",
            "timestamp": "2024-01-01T00:00:00Z",
            "data": {
                "content": "张三和李四讨论分数加法问题",
                "from_user": "张三",
                "to_user": "李四"
            }
        },
        {
            "type": "error_record",
            "timestamp": "2024-01-01T00:00:00Z",
            "data": {
                "student": "张三",
                "error": "分数加法计算错误",
                "course": "数学101"
            }
        }
    ]
    
    # 初始化服务
    from app.services.llm_service import LLMAnalysisService
    from app.services.cache_service import CacheService
    
    cache_service = CacheService()
    llm_service = LLMAnalysisService(cache_service=cache_service)
    
    # 测试完整流程
    # 1. 提取知识点
    knowledge_points = await llm_service.extract_knowledge_points(records[0]["data"]["content"])
    assert len(knowledge_points) > 0
    
    # 2. 提取关系
    entities = [
        {"text": "张三", "type": "Student"},
        {"text": "李四", "type": "Student"},
        {"text": "分数加法", "type": "KnowledgePoint"}
    ]
    relationships = await llm_service.extract_relationships(records[0]["data"]["content"], entities)
    assert len(relationships) > 0
    
    # 3. 分析知识点统计
    knowledge_stats = await llm_service.analyze_knowledge_statistics(records)
    assert "knowledge_point_counts" in knowledge_stats
    
    # 4. 分析学生关注度
    attention_stats = await llm_service.analyze_student_attention(records)
    assert "student_attention_scores" in attention_stats
```

## 5. 预期成果

- 实现了节点联系的辨别与分类功能
- 实现了知识点的统计与知识热点产出功能
- 实现了个体学生的群体关注度统计功能
- 优化了提示词设计，提高模型准确性
- 完善了错误处理和日志记录
- 完成了全面的测试覆盖

## 6. 风险和缓解措施

- **模型准确性**：优化提示词设计，添加详细的任务说明和示例
- **性能问题**：实现批量处理和缓存机制，提高处理效率
- **成本控制**：优化模型选择，对简单任务使用轻量级模型
- **可靠性问题**：实现重试机制和断路器模式，提高系统可靠性
- **数据质量**：添加数据验证和清洗步骤，确保输入数据质量

通过以上计划，我们将确保LLM服务能够完成用户要求的三个核心任务，实现高质量的知识图谱构建和分析功能。