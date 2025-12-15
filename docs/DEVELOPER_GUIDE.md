# 开发者指南

## 1. 项目架构概述

教育知识图谱系统采用前后端分离的架构设计，基于图数据库和大语言模型构建。系统通过FastAPI后端提供API服务，Next.js前端实现可视化交互，Neo4j作为图数据库存储实体和关系，Redis用于缓存和消息队列。

### 1.1 技术栈

| 分类 | 技术 | 版本 | 用途 |
|------|------|------|------|
| **后端** | Python | 3.14+ | 后端开发语言 |
| | FastAPI | 0.100+ | API框架 |
| | Neo4j | 5.0+ | 图数据库 |
| | Redis | 7.0+ | 缓存和消息队列 |
| | Celery | 5.3+ | 异步任务队列 |
| | Pydantic | 2.0+ | 数据验证和序列化 |
| | structlog | 23.0+ | 结构化日志 |
| **前端** | Next.js | 15.0+ | React框架 |
| | TypeScript | 5.0+ | 类型安全 |
| | Tailwind CSS | 3.0+ | 样式框架 |
| | Cytoscape.js | 3.20+ | 图可视化库 |
| | TanStack Query | 5.0+ | 数据获取和缓存 |
| | Zustand | 4.0+ | 状态管理 |
| **开发工具** | Docker | 20.10+ | 容器化 |
| | Docker Compose | 2.0+ | 服务编排 |
| | pytest | 7.0+ | 后端测试框架 |
| | Playwright | 1.30+ | 端到端测试 |
| | Ruff | 0.0.250+ | Python代码检查 |
| | ESLint | 8.0+ | JavaScript/TypeScript代码检查 |

### 1.2 架构图

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │     │                 │
│   前端应用      │────▶│   后端API       │────▶│   图数据库      │
│   (Next.js)     │     │   (FastAPI)     │     │   (Neo4j)       │
│                 │     │                 │     │                 │
└─────────────────┘     └─────────┬───────┘     └─────────────────┘
                                   │
                                   ▼
                             ┌─────────────────┐
                             │                 │
                             │   大语言模型    │
                             │   (DashScope)   │
                             │                 │
                             └─────────────────┘
                                   ▲
                                   │
                             ┌─────────────────┐
                             │                 │
                             │   缓存系统      │
                             │   (Redis)       │
                             │                 │
                             └─────────────────┘
                                   ▲
                                   │
                             ┌─────────────────┐
                             │                 │
                             │   任务队列      │
                             │   (Celery)      │
                             │                 │
                             └─────────────────┘
```

## 2. 代码结构

### 2.1 后端代码结构

```
backend/
├── app/                          # 主应用目录
│   ├── main.py                   # FastAPI应用入口
│   ├── config.py                 # 配置管理
│   ├── database.py               # 数据库连接管理
│   ├── dependencies.py           # 依赖注入
│   ├── celery_app.py             # Celery应用配置
│   ├── models/                   # 数据模型
│   │   ├── base.py               # 基础模型
│   │   ├── nodes.py              # 节点模型
│   │   └── relationships.py      # 关系模型
│   ├── routers/                  # API路由
│   │   ├── __init__.py
│   │   └── visualization.py      # 可视化相关路由
│   ├── services/                 # 业务逻辑服务
│   │   ├── __init__.py
│   │   ├── graph_service.py      # 图管理服务
│   │   ├── llm_service.py        # LLM分析服务
│   │   ├── data_import_service.py # 数据导入服务
│   │   ├── visualization_service.py # 可视化服务
│   │   ├── report_service.py     # 报告服务
│   │   └── cache_service.py      # 缓存服务
│   ├── tasks/                    # Celery任务
│   │   ├── __init__.py
│   │   ├── data_import.py        # 数据导入任务
│   │   └── llm_analysis.py       # LLM分析任务
│   └── utils/                    # 工具函数
│       ├── __init__.py
│       ├── logging.py            # 日志配置
│       ├── exceptions.py         # 自定义异常
│       ├── error_handlers.py     # 错误处理
│       └── audit_log.py          # 审计日志
├── tests/                        # 测试目录
│   ├── __init__.py
│   ├── test_graph_service.py     # 图服务测试
│   ├── test_llm_service.py       # LLM服务测试
│   └── ...
├── .env.example                  # 环境变量示例
├── pyproject.toml                # Python项目配置
└── README.md                     # 后端项目说明
```

### 2.2 前端代码结构

```
frontend/
├── app/                          # Next.js应用目录
│   ├── graph/                    # 图谱可视化页面
│   ├── import/                   # 数据导入页面
│   ├── reports/                  # 报告页面
│   ├── layout.tsx                # 应用布局
│   └── page.tsx                  # 首页
├── components/                   # React组件
│   ├── ui/                       # 基础UI组件
│   ├── graph-visualization.tsx   # 图谱可视化组件
│   ├── filter-panel.tsx          # 筛选面板组件
│   └── ...
├── hooks/                        # 自定义Hooks
│   ├── use-api.ts                # API调用Hook
│   └── use-graph-data.ts         # 图谱数据Hook
├── lib/                          # 工具库
│   ├── api-client.ts             # API客户端
│   ├── store/                    # 状态管理
│   └── visualization-utils.ts    # 可视化工具
├── store/                        # Zustand状态存储
│   ├── graph-store.ts            # 图谱状态
│   └── ui-store.ts               # UI状态
├── types/                        # TypeScript类型定义
│   └── api.ts                    # API类型
├── .env.example                  # 环境变量示例
├── next.config.ts                # Next.js配置
├── package.json                  # 前端项目配置
└── README.md                     # 前端项目说明
```

## 3. 核心服务介绍

### 3.1 GraphManagementService

**职责**: 负责图数据库的核心操作，包括节点和关系的创建、查询、更新和删除。

**主要方法**:
- `create_node`: 创建新节点
- `merge_nodes`: 合并重复节点
- `create_relationship`: 创建关系
- `query_nodes`: 查询节点
- `query_relationships`: 查询关系
- `query_subgraph`: 查询子图

**使用示例**:
```python
from app.services.graph_service import graph_service

# 创建学生节点
student_node = await graph_service.create_node(
    node_type="Student",
    properties={"id": "student_001", "name": "张三", "age": 15}
)
```

### 3.2 LLMAnalysisService

**职责**: 负责与大语言模型交互，进行文本分析、错误类型识别和知识点提取。

**主要方法**:
- `analyze_interaction`: 分析互动内容
- `analyze_error`: 分析错误记录
- `extract_knowledge_points`: 提取知识点

**使用示例**:
```python
from app.services.llm_service import llm_service

# 分析错误记录
analysis_result = await llm_service.analyze_error(
    content="计算错误: 2+3=6",
    course_context={"course_id": "math", "unit": "addition"}
)
```

### 3.3 DataImportService

**职责**: 负责批量导入数据，包括数据验证、处理和存储。

**主要方法**:
- `validate_data`: 验证导入数据
- `import_data`: 执行数据导入
- `get_import_progress`: 获取导入进度

**使用示例**:
```python
from app.services.data_import_service import data_import_service

# 导入学生数据
import_result = await data_import_service.import_data(
    data=student_data_list,
    record_type="student"
)
```

### 3.4 VisualizationService

**职责**: 负责将图数据转换为可视化格式，支持子视图管理和节点详情获取。

**主要方法**:
- `generate_visualization`: 生成可视化数据
- `create_subview`: 创建子视图
- `get_node_details`: 获取节点详情

**使用示例**:
```python
from app.services.visualization_service import visualization_service

# 生成可视化数据
viz_data = visualization_service.generate_visualization(
    subgraph=subgraph_data,
    options={"layout": "force-directed", "show_labels": True}
)
```

### 3.5 ReportService

**职责**: 负责生成各种分析报告，包括学生表现、课程效果和互动模式。

**主要方法**:
- `generate_student_performance_report`: 生成学生表现报告
- `generate_course_effectiveness_report`: 生成课程效果报告
- `generate_interaction_pattern_report`: 生成互动模式报告

**使用示例**:
```python
from app.services.report_service import report_service

# 生成学生表现报告
report = await report_service.generate_student_performance_report(
    student_id="student_001",
    time_range={"start": "2024-01-01", "end": "2024-12-31"}
)
```

## 4. 开发环境搭建

### 4.1 后端开发环境

1. **克隆代码仓库**:
   ```bash
   git clone <repository-url>
   cd CodingPlatformNetwork
   ```

2. **创建虚拟环境**:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   # 或在Windows上使用
   # venv\Scripts\activate
   ```

3. **安装依赖**:
   ```bash
   pip install -e .
   ```

4. **配置环境变量**:
   ```bash
   cp .env.example .env
   ```

5. **启动开发服务器**:
   ```bash
   uvicorn app.main:app --reload
   ```

6. **启动Celery worker** (可选):
   ```bash
   celery -A app.celery_app worker --loglevel=info
   ```

### 4.2 前端开发环境

1. **进入前端目录**:
   ```bash
   cd frontend
   ```

2. **安装依赖**:
   ```bash
   npm install
   ```

3. **配置环境变量**:
   ```bash
   cp .env.example .env.local
   ```

4. **启动开发服务器**:
   ```bash
   npm run dev
   ```

### 4.3 IDE配置建议

#### 4.3.1 VS Code配置

1. **安装推荐插件**:
   - Python
   - Pylance
   - TypeScript Vue Plugin
   - ESLint
   - Prettier
   - Docker

2. **配置Python环境**:
   - 在VS Code中选择后端虚拟环境
   - 配置Python路径为`backend/venv/bin/python`

3. **配置调试**:
   - 后端调试配置: 配置`launch.json`启动FastAPI应用
   - 前端调试配置: 使用Next.js内置的调试功能

## 5. 测试策略和运行方法

### 5.1 测试类型

| 测试类型 | 描述 | 框架 | 运行命令 |
|----------|------|------|----------|
| 单元测试 | 测试单个函数或类 | pytest | `pytest tests/` |
| 集成测试 | 测试多个组件之间的交互 | pytest | `pytest tests/integration/` |
| API测试 | 测试API端点 | pytest | `pytest tests/api/` |
| 组件测试 | 测试React组件 | Jest | `npm test` |
| 端到端测试 | 测试完整的用户流程 | Playwright | `npx playwright test` |

### 5.2 运行后端测试

1. **运行所有测试**:
   ```bash
   cd backend
   pytest
   ```

2. **运行特定测试文件**:
   ```bash
   pytest tests/test_graph_service.py
   ```

3. **运行特定测试函数**:
   ```bash
   pytest tests/test_graph_service.py::test_create_node
   ```

4. **查看测试覆盖率**:
   ```bash
   pytest --cov=app tests/
   ```

### 5.3 运行前端测试

1. **运行组件测试**:
   ```bash
   cd frontend
   npm test
   ```

2. **运行端到端测试**:
   ```bash
   npx playwright test
   ```

3. **查看测试报告**:
   ```bash
   npx playwright show-report
   ```

## 6. API扩展指南

### 6.1 添加新的API端点

1. **在`app/routers/`目录下创建或修改路由文件**:
   ```python
   # app/routers/new_router.py
   from fastapi import APIRouter
   
   router = APIRouter(prefix="/api/v1/new-endpoint", tags=["new-tag"])
   
   @router.get("/items")
   async def get_items():
       return {"items": []}
   ```

2. **在`app/main.py`中注册路由**:
   ```python
   from app.routers import new_router
   app.include_router(new_router.router)
   ```

3. **添加依赖注入（如果需要）**:
   ```python
   # app/dependencies.py
   def get_new_service():
       return NewService()
   ```

4. **更新API文档**:
   - 添加适当的`summary`和`description`
   - 定义`responses`模型

### 6.2 扩展数据模型

1. **添加新的节点类型**:
   ```python
   # app/models/nodes.py
   class NewNodeType(str, Enum):
       NEW_TYPE = "NEW_TYPE"
   ```

2. **添加新的关系类型**:
   ```python
   # app/models/relationships.py
   class NewRelationshipType(str, Enum):
       NEW_RELATIONSHIP = "NEW_RELATIONSHIP"
   ```

3. **更新GraphManagementService**:
   - 添加对新节点类型的支持
   - 添加对新关系类型的支持

### 6.3 添加新的服务

1. **创建服务类**:
   ```python
   # app/services/new_service.py
   class NewService:
       def __init__(self):
           pass
       
       async def new_method(self):
           return {"result": "success"}
   ```

2. **在`app/services/__init__.py`中导出服务**:
   ```python
   from app.services.new_service import NewService, new_service
   ```

3. **添加依赖注入**:
   ```python
   # app/dependencies.py
   def get_new_service():
       return NewService()
   ```

## 7. 贡献代码流程

### 7.1 分支管理

- **main**: 主分支，用于生产环境
- **develop**: 开发分支，用于集成新功能
- **feature/xxx**: 功能分支，用于开发新功能
- **bugfix/xxx**: 修复分支，用于修复bug
- **release/xxx**: 发布分支，用于准备发布

### 7.2 代码审查流程

1. 创建功能分支
2. 实现功能或修复bug
3. 运行测试确保通过
4. 提交代码并创建Pull Request
5. 等待代码审查
6. 解决审查意见
7. 合并到develop分支

### 7.3 提交规范

提交信息应遵循以下格式：

```
<type>(<scope>): <subject>

<body>

<footer>
```

**类型**:
- feat: 新功能
- fix: 修复bug
- docs: 文档更新
- style: 代码风格调整
- refactor: 代码重构
- test: 测试更新
- chore: 构建或依赖更新

**示例**:
```
feat(graph): 添加子视图创建功能

- 实现create_subview方法
- 添加子视图管理API
- 更新可视化服务

Closes #123
```

## 8. 性能优化建议

### 8.1 后端性能优化

1. **使用缓存**:
   - 缓存频繁访问的查询结果
   - 缓存LLM调用结果
   - 使用Redis作为缓存存储

2. **优化数据库查询**:
   - 使用索引加速查询
   - 避免全图扫描
   - 限制查询深度
   - 使用批处理操作

3. **异步编程**:
   - 使用async/await处理I/O操作
   - 使用Celery处理耗时任务
   - 避免阻塞调用

4. **代码优化**:
   - 减少不必要的计算
   - 优化数据结构
   - 避免内存泄漏

### 8.2 前端性能优化

1. **优化渲染**:
   - 使用React.memo优化组件渲染
   - 虚拟滚动处理大量数据
   - 懒加载非关键组件

2. **优化网络请求**:
   - 使用缓存减少请求
   - 合并API请求
   - 使用分页加载数据
   - 压缩响应数据

3. **优化图可视化**:
   - 限制显示的节点数量
   - 使用高效的布局算法
   - 延迟加载节点和关系
   - 优化渲染性能

## 9. 常见问题排查

### 9.1 后端问题

1. **数据库连接失败**:
   - 检查Neo4j服务是否运行
   - 验证连接URI和凭据
   - 检查网络连接

2. **LLM调用失败**:
   - 检查API密钥是否正确
   - 验证网络连接
   - 查看LLM服务状态
   - 检查调用频率限制

3. **Celery任务失败**:
   - 查看Celery日志
   - 检查Redis连接
   - 验证任务参数

### 9.2 前端问题

1. **API调用失败**:
   - 检查API地址配置
   - 验证CORS配置
   - 查看浏览器控制台错误
   - 检查后端服务状态

2. **图可视化性能问题**:
   - 减少显示的节点数量
   - 降低查询深度
   - 选择更高效的布局算法
   - 优化浏览器性能

3. **组件渲染错误**:
   - 查看浏览器控制台错误
   - 检查组件代码
   - 验证数据格式

## 10. 技术文档

### 10.1 API文档

- **自动生成文档**: http://localhost:8000/docs
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### 10.2 项目文档

- **项目需求**: `.kiro/specs/education-knowledge-graph/requirements.md`
- **设计文档**: `.kiro/specs/education-knowledge-graph/design.md`
- **任务列表**: `.kiro/specs/education-knowledge-graph/tasks.md`

## 11. 联系信息

如有任何问题或建议，请联系技术团队或在项目仓库中创建Issue。