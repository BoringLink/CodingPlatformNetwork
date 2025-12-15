# LLM服务使用指南

## 概述

LLM服务集成了阿里云通义千问大语言模型，提供智能分析功能。

## 配置

在 `.env` 文件中配置以下环境变量：

```bash
# 阿里云通义千问配置
DASHSCOPE_API_KEY=your-api-key-here
QWEN_MODEL_SIMPLE=qwen-turbo
QWEN_MODEL_MEDIUM=qwen-plus
QWEN_MODEL_COMPLEX=qwen-max
QWEN_MAX_TOKENS=2000
QWEN_TEMPERATURE=0.7

# 缓存配置
CACHE_ENABLED=true
CACHE_TTL=3600

# 重试配置
LLM_RETRY_MAX=3
LLM_RETRY_DELAY=1.0
```

## 功能

### 1. 互动内容分析

分析学生之间或师生之间的互动内容，提取情感和主题。

```python
from app.services import get_llm_service

llm_service = get_llm_service()

# 分析互动内容
analysis = await llm_service.analyze_interaction(
    text="同学们一起讨论数学作业，互相帮助解决问题"
)

print(f"情感: {analysis.sentiment}")  # positive/neutral/negative
print(f"主题: {analysis.topics}")     # ["数学作业", "互相帮助", ...]
print(f"置信度: {analysis.confidence}")  # 0.0-1.0
```

### 2. 错误记录分析

分析学生的错误记录，识别错误类型并推断相关知识点。

```python
from app.services import get_llm_service, CourseContext

llm_service = get_llm_service()

# 创建课程上下文
context = CourseContext(
    course_id="C001",
    course_name="数学基础",
    description="小学数学基础课程"
)

# 分析错误记录
analysis = await llm_service.analyze_error(
    error_text="学生在计算分数加法时，直接将分子和分母相加",
    context=context
)

print(f"错误类型: {analysis.error_type}")
print(f"相关知识点: {analysis.related_knowledge_points}")
print(f"难度: {analysis.difficulty}")  # easy/medium/hard
print(f"置信度: {analysis.confidence}")
```

### 3. 知识点提取

从课程内容中提取关键知识点，并识别知识点之间的依赖关系。

```python
from app.services import get_llm_service

llm_service = get_llm_service()

# 提取知识点
knowledge_points = await llm_service.extract_knowledge_points(
    course_content="""
    本课程介绍分数的基本概念，包括分子、分母的含义。
    然后学习分数的加法运算，包括同分母和异分母的情况。
    """
)

for kp in knowledge_points:
    print(f"ID: {kp.id}")
    print(f"名称: {kp.name}")
    print(f"描述: {kp.description}")
    print(f"依赖: {kp.dependencies}")
```

### 4. 结果转换

将LLM分析结果转换为图数据库的节点属性和关系数据。

```python
# 转换互动分析结果为节点属性
properties = llm_service.convert_interaction_to_node_properties(
    analysis=interaction_analysis,
    interaction_id="I001",
    from_user_id="U001",
    to_user_id="U002",
    timestamp="2024-01-01T00:00:00Z"
)

# 转换错误分析结果为关系数据
relationships = llm_service.convert_error_to_relationship_data(
    analysis=error_analysis,
    student_node_id="S001",
    error_type_node_id="E001",
    knowledge_point_node_ids=["KP001", "KP002"]
)
```

## 特性

### 智能缓存

- 基于内容哈希的缓存机制
- 自动缓存LLM响应，减少API调用
- 可配置的缓存过期时间

### 重试机制

- 指数退避重试策略
- 最多重试3次（可配置）
- 自动处理临时网络错误

### 错误恢复

- 自动解析JSON响应
- 支持多种JSON格式（纯JSON、代码块、混合文本）
- 验证必需字段

## 成本优化

系统根据任务复杂度选择不同的模型：

- **qwen-turbo**: 简单任务（情感分析、分类）- 免费额度100万tokens/月
- **qwen-plus**: 中等复杂度任务（知识点提取、错误分析）- 性价比高
- **qwen-max**: 复杂任务（复杂推理）- 仅在必要时使用

## 注意事项

1. 确保配置了有效的 `DASHSCOPE_API_KEY`
2. 首次使用时会初始化服务，需要等待连接建立
3. 缓存服务失败不会阻止应用启动，但会影响性能
4. LLM调用失败会抛出异常，需要适当处理
