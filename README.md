# 教育知识图谱系统

## 1. 应用架构

教育知识图谱系统是一个基于微服务架构的智能教育平台，主要包含以下组件：

| 组件 | 技术栈 | 功能描述 |
|------|--------|----------|
| 后端 API | FastAPI | 提供 RESTful API 服务，处理业务逻辑 |
| 前端应用 | Next.js | 提供用户交互界面 |
| 图数据库 | Neo4j | 存储和管理知识图谱数据 |
| 关系数据库 | PostgreSQL | 存储非图结构化数据 |
| 缓存 & 消息队列 | Redis | 提供缓存服务和 Celery 消息代理 |
| 异步任务处理 | Celery | 处理异步任务，如数据导入、模型训练 |
| 任务监控 | Flower | 监控 Celery 任务执行状态 |

## 2. 依赖要求

- Docker 20.10+ 
- Docker Compose 2.0+

## 3. 快速启动

### 3.1 环境配置

1. 复制环境变量示例文件：
```bash
cp .env.example .env
```

2. 根据实际情况修改 `.env` 文件中的配置，特别是：
   - `DASHSCOPE_API_KEY`：阿里云通义千问 API 密钥
   - 数据库连接参数（如果需要自定义）

### 3.2 启动服务

使用 Docker Compose 一键启动所有服务：

```bash
# 构建镜像（首次启动或代码更新后执行）
docker-compose build

# 启动服务
docker-compose up -d
```

### 3.3 停止服务

```bash
docker-compose down
```

## 4. 服务访问地址

| 服务 | 访问地址 | 说明 |
|------|----------|------|
| 后端 API 文档 | http://localhost:8000/docs | Swagger UI 接口文档 |
| 前端应用 | http://localhost:3000 | 主应用界面 |
| Neo4j 控制台 | http://localhost:7474 | 图数据库管理界面 |
| Flower 监控 | http://localhost:5555 | Celery 任务监控 |
| PostgreSQL | localhost:5432 | 关系数据库（需客户端连接） |
| Redis | localhost:6379 | 缓存服务（需客户端连接） |

## 5. 环境变量说明

### 5.1 核心配置

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `DEBUG` | 调试模式开关 | `true` |
| `APP_NAME` | 应用名称 | `教育知识图谱系统` |

### 5.2 数据库配置

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `NEO4J_URI` | Neo4j 连接 URI | `bolt://localhost:7687` |
| `NEO4J_USER` | Neo4j 用户名 | `neo4j` |
| `NEO4J_PASSWORD` | Neo4j 密码 | `password` |
| `POSTGRES_HOST` | PostgreSQL 主机 | `localhost` |
| `POSTGRES_PORT` | PostgreSQL 端口 | `5432` |
| `POSTGRES_USER` | PostgreSQL 用户名 | `postgres` |
| `POSTGRES_PASSWORD` | PostgreSQL 密码 | `password` |
| `POSTGRES_DB` | PostgreSQL 数据库名 | `education_kg` |
| `REDIS_HOST` | Redis 主机 | `localhost` |
| `REDIS_PORT` | Redis 端口 | `6379` |

### 5.3 AI 服务配置

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `DASHSCOPE_API_KEY` | 阿里云通义千问 API 密钥 | - |
| `QWEN_MODEL_SIMPLE` | 简单任务模型 | `qwen-turbo` |
| `QWEN_MODEL_MEDIUM` | 中等任务模型 | `qwen-plus` |
| `QWEN_MODEL_COMPLEX` | 复杂任务模型 | `qwen-max` |

## 6. 开发说明

### 6.1 后端开发

后端服务使用 FastAPI 框架，代码位于 `./backend` 目录：

```bash
# 进入后端目录
cd backend

# 安装依赖
pip install -e "[dev]"

# 启动开发服务器
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 6.2 前端开发

前端服务使用 Next.js 框架，代码位于 `./frontend` 目录：

```bash
# 进入前端目录
cd frontend

# 安装依赖
pnpm install

# 启动开发服务器
pnpm run dev
```

## 7. 日志管理

查看服务日志：

```bash
# 查看所有服务日志
docker-compose logs

# 查看特定服务日志
docker-compose logs backend

# 实时查看日志
docker-compose logs -f backend
```

## 8. 常见问题

### 8.1 端口冲突

如果遇到端口冲突，可以在 `docker-compose.yml` 文件中修改对应服务的端口映射，例如：

```yaml
frontend:
  ports:
    - "3001:3000"  # 将主机端口改为 3001
```

### 8.2 服务启动失败

查看详细日志定位问题：
```bash
docker-compose logs -f <service_name>
```

### 8.3 数据库连接问题

确保 `.env` 文件中的数据库连接参数与实际配置一致，尤其是用户名、密码和端口。

## 9. 版本信息

- Docker 镜像版本：
  - Neo4j: 5.15-community
  - Redis: 7.2-alpine
  - PostgreSQL: 17-alpine
  - Python: 3.12-slim
  - Node.js: 20-alpine

## 10. 联系方式

如有问题或建议，请联系开发团队。
