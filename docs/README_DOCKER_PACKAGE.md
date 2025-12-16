# Docker 打包与部署指南

## 项目概览

本项目是一个教育知识图谱神经网络系统，包含以下服务：

- **neo4j**: 图数据库
- **redis**: 缓存和消息队列
- **postgres**: 关系型数据库（可选）
- **backend**: FastAPI 后端服务
- **celery-worker**: 异步任务处理
- **flower**: Celery 监控
- **frontend**: Next.js 前端服务

## 打包方案

### 方案一：提供完整项目源码（推荐）

#### 步骤 1：准备项目文件

将以下文件和目录打包发送给对方：

```
CodingPlatformNetwork/
├── backend/          # 后端源码
├── docker/           # Docker 配置文件
│   ├── Dockerfile.backend
│   └── Dockerfile.frontend
├── frontend/         # 前端源码
└── docker-compose.yml # Docker Compose 配置
```

#### 步骤 2：接收方部署

接收方需要安装 Docker 和 Docker Compose，然后执行以下命令：

```bash
# 1. 进入项目目录
cd CodingPlatformNetwork

# 2. 构建并启动所有服务
docker-compose up -d
```

### 方案二：预先构建镜像并导出

如果接收方网络环境较差，可以预先构建镜像并导出。

#### 步骤 1：构建镜像

```bash
# 进入项目目录
cd CodingPlatformNetwork

# 构建所有镜像
docker-compose build
```

#### 步骤 2：导出镜像

```bash
# 保存镜像到文件
docker save -o education-kg-images.tar \
    educationknowledgegraph_backend \
    educationknowledgegraph_frontend \
    neo4j:5.15-community \
    redis:7.2-alpine \
    postgres:17-alpine
```

#### 步骤 3：发送文件

将以下文件发送给对方：

```
- education-kg-images.tar    # 预构建的镜像文件
- docker-compose.yml         # Docker Compose 配置
- docker/                    # Docker 配置目录
```

#### 步骤 4：接收方导入并启动

```bash
# 1. 导入镜像
docker load -i education-kg-images.tar

# 2. 启动服务
docker-compose up -d
```

## 环境变量配置

### 必要环境变量

- **DASHSCOPE_API_KEY**: 阿里云通义千问 API 密钥
  - 用于 LLM 服务功能
  - 如果不需要 LLM 功能，可以留空

### 可选环境变量

- **DEBUG**: 是否开启调试模式（默认：true）
- **NEXT_PUBLIC_API_URL**: 前端调用后端 API 的 URL（默认：http://localhost:8000）

## 访问服务

服务启动后，可以通过以下地址访问：

| 服务          | 访问地址                    |
| ------------- | --------------------------- |
| 前端          | http://localhost:3000       |
| 后端 API      | http://localhost:8000       |
| 后端文档      | http://localhost:8000/docs  |
| Neo4j 控制台  | http://localhost:7474       |
| Redis         | redis://localhost:6379      |
| PostgreSQL    | postgresql://localhost:5432 |
| Celery Flower | http://localhost:5555       |

## 常用命令

### 启动/停止服务

```bash
# 启动所有服务
docker-compose up -d

# 停止所有服务
docker-compose down

# 重启所有服务
docker-compose restart
```

### 查看日志

```bash
# 查看所有服务日志
docker-compose logs

# 查看特定服务日志
docker-compose logs -f backend

# 查看最近 100 行日志
docker-compose logs --tail=100
```

### 进入容器

```bash
# 进入
```
后端容器
docker-compose exec backend bash

# 进入前端容器
docker-compose exec frontend bash

# 进入 Neo4j 容器
docker-compose exec neo4j bash
```

## 注意事项

1. **首次启动时间较长**：首次启动时，Docker 会下载所有依赖并构建镜像，可能需要 5-10 分钟。

2. **端口占用问题**：确保本地 3000、8000、7474、7687、6379、5432、5555 端口未被占用。

3. **数据持久化**：所有服务的数据都会持久化到 Docker 卷中，删除容器不会丢失数据。

4. **环境变量安全**：敏感信息（如 API 密钥）通过环境变量传递，不要硬编码到代码中。

5. **生产环境建议**：
   - 关闭 DEBUG 模式
   - 使用 HTTPS
   - 配置适当的防火墙规则
   - 定期备份数据

## 故障排查

### 服务启动失败

```bash
# 查看服务状态
docker-compose ps

# 查看失败服务的日志
docker-compose logs -f <服务名>
```

### 数据库连接问题

- 确保数据库服务已正常启动
- 检查环境变量配置是否正确
- 查看数据库日志

### 前端无法访问后端

- 检查 `NEXT_PUBLIC_API_URL` 环境变量是否正确
- 确保后端服务已正常启动
- 检查网络配置

## 版本信息

- Docker 版本：>= 20.10.0
- Docker Compose 版本：>= 2.0.0
- Python 版本：3.12
- Node.js 版本：24
- Next.js 版本：16

## 联系方式

如果遇到问题，请联系项目负责人获取帮助。