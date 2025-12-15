# LLM服务配置指南

本项目使用阿里云通义千问API作为主要的LLM服务提供商，提供免费额度和低成本的中文智能分析能力。

## 为什么选择阿里云通义千问？

1. **免费额度充足**: qwen-turbo提供100万tokens/月的免费额度
2. **中文能力强**: 专为中文优化，特别适合教育内容分析
3. **成本低**: 价格远低于国际模型（OpenAI、Claude等）
4. **响应快**: 国内访问速度快，无需科学上网

## 价格对比

### 阿里云通义千问
- **qwen-turbo**: 免费100万tokens/月，超出后¥0.0008/千tokens（输入）
- **qwen-plus**: ¥0.004/千tokens（输入）
- **qwen-max**: ¥0.04/千tokens（输入）

### OpenAI（对比参考）
- **GPT-4o-mini**: $0.15/百万tokens（输入）≈ ¥1.05/百万tokens
- **GPT-4o**: $2.50/百万tokens（输入）≈ ¥17.5/百万tokens

**结论**: qwen-turbo的免费额度可以满足大部分中小规模应用，即使超出免费额度，成本也远低于OpenAI。

## 获取API密钥

### 步骤1: 注册阿里云账号

1. 访问 [阿里云官网](https://www.aliyun.com/)
2. 点击右上角"免费注册"
3. 完成手机号验证和实名认证

### 步骤2: 开通DashScope服务

1. 访问 [DashScope控制台](https://dashscope.console.aliyun.com/)
2. 首次访问会提示开通服务，点击"立即开通"
3. 阅读并同意服务协议

### 步骤3: 创建API密钥

1. 在DashScope控制台，点击右上角头像
2. 选择"API-KEY管理"
3. 点击"创建新的API-KEY"
4. 复制生成的API密钥（只显示一次，请妥善保存）

### 步骤4: 配置到项目

将API密钥配置到环境变量：

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑.env文件，填入你的API密钥
DASHSCOPE_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

## 模型选择策略

本项目根据任务复杂度自动选择合适的模型：

### qwen-turbo（默认）
**适用场景**:
- 学生互动内容的情感分析
- 简单的文本分类
- 错误类型的初步识别

**特点**:
- 免费额度：100万tokens/月
- 响应速度快
- 适合高频调用的简单任务

### qwen-plus（推荐）
**适用场景**:
- 知识点提取
- 错误详细分析
- 知识点依赖关系推断

**特点**:
- 性价比高
- 中文理解能力强
- 适合中等复杂度任务

### qwen-max（按需使用）
**适用场景**:
- 复杂的知识点依赖关系推理
- 需要最高准确度的场景

**特点**:
- 最强的推理能力
- 价格较高
- 仅在必要时使用

## 成本控制策略

本项目实现了多种成本控制机制：

### 1. 智能缓存
- 基于输入内容哈希的缓存机制
- 相同输入直接返回缓存结果
- 大幅减少重复API调用

### 2. Token限制
- 输入限制：2000 tokens
- 输出限制：1000 tokens
- 避免超长文本导致的高成本

### 3. 批量处理
- 将相似请求合并处理
- 减少API调用次数

### 4. 模型降级
- 优先使用免费的qwen-turbo
- 仅在必要时升级到qwen-plus或qwen-max

## 备选方案：本地部署

如果对数据隐私要求高，或希望完全免费，可以使用Ollama本地部署：

### 安装Ollama

```bash
# macOS
brew install ollama

# Linux
curl -fsSL https://ollama.com/install.sh | sh

# Windows
# 下载安装包：https://ollama.com/download
```

### 下载Qwen模型

```bash
# 下载Qwen2.5 7B模型（推荐）
ollama pull qwen2.5:7b

# 或下载更小的模型（4GB显存即可）
ollama pull qwen2.5:3b
```

### 配置项目使用本地模型

修改`backend/app/services/llm_service.py`，添加Ollama支持：

```python
# 使用Ollama本地模型
import requests

def call_ollama(prompt: str, model: str = "qwen2.5:7b"):
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": model,
            "prompt": prompt,
            "stream": False,
        }
    )
    return response.json()["response"]
```

### 本地部署优势
- ✅ 完全免费
- ✅ 数据不出本地
- ✅ 无网络依赖
- ✅ 无API调用限制

### 本地部署劣势
- ❌ 需要GPU资源（建议至少8GB显存）
- ❌ 推理速度较慢
- ❌ 模型能力略低于云端版本

## 使用示例

```python
from app.services.llm_service import llm_service, QwenModel

# 分析学生互动（使用免费的qwen-turbo）
analysis = await llm_service.analyze_interaction(
    text="今天的数学作业好难啊，导数那部分完全不懂",
)
print(f"情感: {analysis.sentiment}")
print(f"主题: {analysis.topics}")

# 分析错误记录（使用qwen-plus）
error_analysis = await llm_service.analyze_error(
    error_text="学生在计算导数时，将 (x^2)' 错误地计算为 x",
    course_context={"course_name": "高等数学", "description": "微积分基础"},
    model=QwenModel.PLUS,  # 显式指定使用qwen-plus
)
print(f"错误类型: {error_analysis.error_type}")
print(f"相关知识点: {error_analysis.related_knowledge_points}")

# 提取知识点（使用qwen-plus）
knowledge_points = await llm_service.extract_knowledge_points(
    course_content="本章介绍导数的定义、几何意义和基本求导法则...",
)
for kp in knowledge_points:
    print(f"知识点: {kp.name}")
    print(f"依赖: {kp.dependencies}")
```

## 监控和调试

### 查看API使用情况

访问 [DashScope控制台](https://dashscope.console.aliyun.com/) 查看：
- API调用次数
- Token使用量
- 费用统计
- 错误日志

### 日志查看

项目使用structlog记录所有LLM调用：

```bash
# 查看LLM调用日志
grep "qwen_api_called" logs/app.log

# 查看缓存命中情况
grep "cache_hit" logs/app.log
```

## 常见问题

### Q: 免费额度用完了怎么办？
A: 
1. 检查是否有重复调用（应该被缓存的请求）
2. 考虑升级到付费版本（成本仍然很低）
3. 或切换到本地Ollama部署

### Q: API调用失败怎么办？
A:
1. 检查API密钥是否正确
2. 检查网络连接
3. 查看DashScope控制台的错误日志
4. 检查是否超出速率限制

### Q: 如何提高分析准确度？
A:
1. 使用更高级的模型（qwen-plus或qwen-max）
2. 优化提示词（prompt）
3. 提供更多上下文信息

### Q: 可以同时使用多个LLM服务吗？
A: 可以。项目设计支持多个LLM服务，可以配置主服务和备用服务，实现自动降级。

## 技术支持

- 阿里云DashScope文档: https://help.aliyun.com/zh/dashscope/
- 通义千问API文档: https://help.aliyun.com/zh/dashscope/developer-reference/api-details
- 项目Issues: [GitHub Issues链接]

## 更新日志

- 2024-12: 初始版本，使用阿里云通义千问API
- 支持qwen-turbo、qwen-plus、qwen-max三个模型
- 实现智能缓存和成本控制
