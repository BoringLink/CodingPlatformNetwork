# 后端核心架构文档

## 概述

本文档描述教育知识图谱系统后端的核心架构实现。

## 技术栈

- **Python**: 3.12+
- **Web 框架**: FastAPI 0.110+
- **数据验证**: Pydantic v2
- **配置管理**: pydantic-settings
- **日志**: structlog 24.x
- **ASGI 服务器**: Uvicorn

## 项目结构

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI 应用入口
│   ├── config.py            # 配置管理
│   ├── models/              # 数据模型
│   │   ├── __init__.py
│   │   ├── base.py          # 基础模型
│   │   ├── nodes.py         # 节点模型
│   │   └── relationships.py # 关系模型
│   ├── routers/             # API 路由（待实现）
│   │   └── __init__.py
│   ├── services/            # 业务逻辑服务（待实现）
│   │   └── __init__.py
│   └── utils/               # 工具函数
│       ├── __init__.py
│       └── logging.py       # 日志配置
├── tests/                   # 测试
├── .env.example             # 环境变量示例
├── pyproject.toml           # 项目配置
└── test_setup.py            # 架构测试脚本

```

## 核心组件

### 1. FastAPI 应用 (app/main.py)

FastAPI 应用入口，包含：

- **生命周期管理**: 使用 `lifespan` 管理应用启动和关闭
- **CORS 中间件**: 配置跨域资源共享
- **日志中间件**: 记录所有 HTTP 请求和响应
- **全局异常处理**: 统一处理未捕获的异常
- **健康检查端点**: `/` 和 `/health`

### 2. 配置管理 (app/config.py)

使用 `pydantic-settings` 管理应用配置：

- **环境变量加载**: 从 `.env` 文件和环境变量加载配置
- **类型验证**: 使用 Pydantic 进行类型检查和验证
- **字段验证器**: 自定义验证逻辑（如日志级别、CORS 来源）
- **计算属性**: 动态生成连接 URL（Redis、PostgreSQL）

#### 主要配置项

- **应用配置**: app_name, debug, environment
- **CORS 配置**: cors_origins
- **Neo4j 配置**: neo4j_uri, neo4j_user, neo4j_password
- **Redis 配置**: redis_host, redis_port, redis_db
- **OpenAI 配置**: openai_api_key, openai_model_simple, openai_model_complex
- **数据处理配置**: batch_size, llm_rate_limit, llm_retry_max
- **日志配置**: log_level, log_format

### 3. 数据模型 (app/models/)

使用 Pydantic v2 定义数据模型：

#### 基础模型 (base.py)

- `BaseNodeProperties`: 节点属性基类
- `BaseRelationshipProperties`: 关系属性基类
- `TimestampMixin`: 时间戳混入类
- `ResponseModel`: API 响应基类
- `ErrorResponse`: 错误响应模型

#### 节点模型 (nodes.py)

- `NodeType`: 节点类型枚举（Student, Teacher, KnowledgePoint）
- `StudentNodeProperties`: 学生节点属性
- `TeacherNodeProperties`: 教师节点属性
- `KnowledgePointNodeProperties`: 知识点节点属性
- `Node`: 通用节点模型

#### 关系模型 (relationships.py)

- `RelationshipType`: 关系类型枚举
- `ChatWithProperties`: 聊天互动关系
- `LikesProperties`: 点赞互动关系
- `TeachesProperties`: 教学互动关系
- `LearnsProperties`: 学习关系
- `ContainsProperties`: 包含关系
- `RelatesToProperties`: 关联关系
- `Relationship`: 通用关系模型

### 4. 结构化日志 (app/utils/logging.py)

使用 `structlog` 实现结构化日志：

- **JSON 格式**: 生产环境使用，便于日志聚合和分析
- **Console 格式**: 开发环境使用，带颜色高亮
- **日志级别过滤**: 根据配置过滤日志
- **上下文变量**: 支持在日志中添加上下文信息

## 中间件

### 日志中间件

记录每个 HTTP 请求的详细信息：

- 请求方法和路径
- 客户端 IP
- 响应状态码
- 处理时间
- 错误信息（如果有）

### CORS 中间件

配置跨域资源共享：

- 允许的来源（从配置读取）
- 允许凭证
- 允许所有方法和头部

## 错误处理

### 全局异常处理器

捕获所有未处理的异常：

- 记录详细的错误日志
- 返回统一的错误响应格式
- 在调试模式下显示详细错误信息

## 环境变量

所有配置都可以通过环境变量设置。参见 `.env.example` 文件。

### 示例

```bash
# 应用配置
APP_NAME=教育知识图谱系统
DEBUG=true
ENVIRONMENT=development

# CORS 配置
CORS_ORIGINS=http://localhost:3000,http://localhost:3001

# Neo4j 配置
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password

# 日志配置
LOG_LEVEL=INFO
LOG_FORMAT=console
```

## 运行应用

### 开发模式

```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows

# 安装依赖
pip install -e .[dev]

# 运行应用
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 测试架构

```bash
python test_setup.py
```

## API 文档

FastAPI 自动生成 API 文档：

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## 下一步

后续任务将实现：

1. Neo4j 图数据库集成
2. LLM 分析服务
3. 数据导入服务
4. 查询服务
5. 可视化服务
6. REST API 端点

## 验证清单

- [x] FastAPI 应用结构创建
- [x] Pydantic v2 数据模型和验证
- [x] 配置管理（pydantic-settings）
- [x] CORS 和中间件设置
- [x] structlog 结构化日志配置
- [x] 全局异常处理
- [x] 健康检查端点
- [x] 环境变量配置
- [x] 项目结构组织
- [x] 测试脚本验证
