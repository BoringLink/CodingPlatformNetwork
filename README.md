# 教育知识图谱神经网络系统

基于大语言模型和图数据库的教育数据分析平台，用于构建和可视化教育知识图谱。

## 系统概述

本系统通过分析教育项目中的多维度数据（学生互动、师生交流、课程记录、错误记录等），利用大语言模型进行智能判断和分析，生成结构化的知识图谱节点和关系，以支持个性化学习分析和教学优化。

## 技术栈

### 后端
- **Python 3.12+**: 编程语言
- **FastAPI 0.110+**: Web 框架
- **Neo4j 5.15+**: 图数据库
- **Redis 7.2**: 缓存和消息队列
- **PostgreSQL 17**: 关系型数据库（可选）
- **Celery 5.3+**: 异步任务队列
- **阿里云通义千问 API**: 大语言模型服务（免费额度充足，中文能力强）

### 前端
- **Next.js 15**: React 框架
- **TypeScript 5.6**: 类型系统
- **Tailwind CSS**: 样式框架
- **Cytoscape.js**: 图可视化
- **Zustand**: 状态管理
- **TanStack Query**: 数据获取

### 开发工具
- **Docker & Docker Compose**: 容器化
- **pytest**: Python 测试
- **hypothesis**: 基于属性的测试
- **Ruff**: Python 代码检查
- **ESLint**: JavaScript/TypeScript 代码检查

## 项目结构

```
.
├── backend/              # 后端服务
│   ├── app/
│   │   ├── main.py      # FastAPI 应用入口
│   │   ├── config.py    # 配置管理
│   │   ├── models/      # 数据模型
│   │   ├── services/    # 业务逻辑服务
│   │   ├── routers/     # API 路由
│   │   └── utils/       # 工具函数
│   ├── tests/           # 测试文件
│   └── pyproject.toml   # Python 项目配置
├── frontend/            # 前端应用
│   ├── app/            # Next.js App Router
│   ├── components/     # React 组件
│   └── package.json    # Node.js 项目配置
├── docker/             # Docker 配置
│   ├── Dockerfile.backend
│   └── Dockerfile.frontend
├── docker-compose.yml  # Docker Compose 配置
└── .env.example       # 环境变量示例
```

## 快速开始

### 前置要求

- Docker 和 Docker Compose
- Python 3.12+ (本地开发)
- Node.js 20+ (本地开发)
- 阿里云 DashScope API Key（免费注册，100万tokens/月免费额度）

### 使用 Docker Compose（推荐）

1. 克隆项目并进入目录：
```bash
git clone <repository-url>
cd education-knowledge-graph
```

2. 复制环境变量文件并配置：
```bash
cp .env.example .env
# 编辑 .env 文件，设置 DASHSCOPE_API_KEY
# 获取API密钥：https://dashscope.console.aliyun.com/apiKey
```

3. 启动所有服务：
```bash
docker-compose up -d
```

4. 访问服务：
- 前端: http://localhost:3000
- 后端 API: http://localhost:8000
- API 文档: http://localhost:8000/docs
- Neo4j Browser: http://localhost:7474
- Flower (Celery 监控): http://localhost:5555

5. 停止服务：
```bash
docker-compose down
```

### 本地开发

#### 后端开发

1. 进入后端目录：
```bash
cd backend
```

2. 创建虚拟环境并安装依赖：
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -e ".[dev]"
```

3. 复制环境变量文件：
```bash
cp .env.example .env
# 编辑 .env 文件
```

4. 启动开发服务器：
```bash
uvicorn app.main:app --reload
```

5. 运行测试：
```bash
pytest
```

#### 前端开发

1. 进入前端目录：
```bash
cd frontend
```

2. 安装依赖：
```bash
npm install
```

3. 复制环境变量文件：
```bash
cp .env.example .env.local
# 编辑 .env.local 文件
```

4. 启动开发服务器：
```bash
npm run dev
```

5. 运行测试：
```bash
npm test
```

## LLM服务配置

本项目使用阿里云通义千问作为大语言模型服务提供商。

### 为什么选择阿里云通义千问？

- ✅ **免费额度充足**: qwen-turbo提供100万tokens/月免费额度
- ✅ **中文能力强**: 专为中文优化，特别适合教育内容分析
- ✅ **成本低**: 价格远低于国际模型（节省90%以上成本）
- ✅ **响应快**: 国内访问速度快，无需科学上网

### 获取API密钥

1. 访问 [阿里云DashScope控制台](https://dashscope.console.aliyun.com/)
2. 注册/登录阿里云账号
3. 开通DashScope服务（免费）
4. 创建API密钥
5. 将密钥配置到 `.env` 文件中

详细配置指南请参考：[backend/LLM_SETUP.md](backend/LLM_SETUP.md)

### 模型选择

系统根据任务复杂度自动选择合适的模型：

- **qwen-turbo** (免费): 简单任务（情感分析、分类）
- **qwen-plus** (低成本): 中等复杂度（知识点提取、错误分析）
- **qwen-max** (按需): 复杂推理（仅在必要时使用）

### 成本估算

假设每月处理：
- 10,000次互动分析（平均500 tokens/次）= 5M tokens
- 5,000次错误分析（平均800 tokens/次）= 4M tokens
- 1,000次知识点提取（平均1500 tokens/次）= 1.5M tokens

**总计**: 约10.5M tokens/月

使用qwen-turbo免费额度（1M tokens）+ qwen-plus付费部分：
- 免费: 1M tokens
- 付费: 9.5M tokens × ¥0.004/千tokens = **¥38/月**

相比OpenAI GPT-4o-mini（约¥100/月），**节省62%成本**！

## 开发指南

### 后端开发

- 使用 FastAPI 创建 API 端点
- 使用 Pydantic 进行数据验证
- 使用 Neo4j 进行图数据操作
- 使用 Celery 处理异步任务
- 使用 pytest 和 hypothesis 编写测试

### 前端开发

- 使用 Next.js App Router
- 使用 TypeScript 确保类型安全
- 使用 Tailwind CSS 编写样式
- 使用 Cytoscape.js 实现图可视化
- 使用 TanStack Query 管理服务端状态

### 代码规范

- Python: 遵循 PEP 8，使用 Ruff 进行代码检查
- TypeScript: 遵循 ESLint 规则
- 提交前运行测试确保代码质量

## 测试策略

系统采用双重测试方法：

1. **单元测试**: 验证特定示例、边缘情况和错误条件
2. **基于属性的测试 (PBT)**: 验证在所有有效输入下都应该成立的通用属性

每个正确性属性都有对应的 PBT 测试，确保系统行为符合规范。

## 部署

### 生产环境部署

1. 构建生产镜像：
```bash
docker-compose -f docker-compose.prod.yml build
```

2. 启动生产服务：
```bash
docker-compose -f docker-compose.prod.yml up -d
```

3. 配置反向代理（Nginx/Caddy）
4. 配置 SSL 证书
5. 设置监控和日志收集

## 许可证

[待定]

## 贡献

欢迎贡献！请阅读贡献指南。

## 联系方式

[待定]
