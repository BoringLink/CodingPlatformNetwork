# 部署文档

## 1. 环境要求

### 1.1 基本环境
- **操作系统**: Linux/macOS/Windows
- **Docker**: 20.10+（推荐使用Docker Compose部署）
- **Python**: 3.14+（仅在本地开发时需要）
- **Node.js**: 18+（仅在前端开发时需要）

### 1.2 硬件要求
- **CPU**: 4核以上
- **内存**: 8GB以上
- **磁盘**: 50GB以上可用空间

## 2. 部署方式

### 2.1 Docker Compose部署（推荐）

#### 2.1.1 准备工作
1. 克隆代码仓库：
   ```bash
   git clone <repository-url>
   cd CodingPlatformNetwork
   ```

2. 复制环境变量示例文件并配置：
   ```bash
   cp .env.example .env
   ```

3. 编辑`.env`文件，配置必要的环境变量（详见3. 环境变量配置）。

#### 2.1.2 启动服务
1. 使用Docker Compose启动所有服务：
   ```bash
   docker-compose up -d
   ```

2. 查看服务状态：
   ```bash
   docker-compose ps
   ```

3. 停止服务：
   ```bash
   docker-compose down
   ```

#### 2.1.3 服务访问地址
- **前端应用**: http://localhost:3000
- **后端API**: http://localhost:8000
- **API文档**: http://localhost:8000/docs
- **Neo4j浏览器**: http://localhost:7474
- **Redis Insight**: http://localhost:8000
- **Celery Flower**: http://localhost:5555

### 2.2 本地开发部署

#### 2.2.1 后端部署
1. 进入后端目录：
   ```bash
   cd backend
   ```

2. 创建虚拟环境并激活：
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   venv\Scripts\activate  # Windows
   ```

3. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```

4. 配置环境变量：
   ```bash
   cp .env.example .env
   ```

5. 启动后端服务：
   ```bash
   uvicorn app.main:app --reload
   ```

6. 启动Celery worker（可选，用于异步任务）：
   ```bash
   celery -A app.celery_app worker --loglevel=info
   ```

7. 启动Flower监控（可选）：
   ```bash
   celery -A app.celery_app flower
   ```

#### 2.2.2 前端部署
1. 进入前端目录：
   ```bash
   cd frontend
   ```

2. 安装依赖：
   ```bash
   npm install
   ```

3. 配置环境变量：
   ```bash
   cp .env.example .env.local
   ```

4. 启动开发服务器：
   ```bash
   npm run dev
   ```

5. 构建生产版本：
   ```bash
   npm run build
   ```

6. 启动生产服务器：
   ```bash
   npm run start
   ```

## 3. 环境变量配置

### 3.1 核心环境变量

#### 3.1.1 后端配置
| 环境变量 | 描述 | 默认值 | 必须 |
|----------|------|--------|------|
| `APP_NAME` | 应用名称 | `education-knowledge-graph` | 否 |
| `ENVIRONMENT` | 运行环境 | `development` | 否 |
| `DEBUG` | 调试模式 | `true` | 否 |
| `CORS_ORIGINS` | 允许的跨域来源 | `["*"]` | 否 |
| `PORT` | 后端服务端口 | `8000` | 否 |

#### 3.1.2 Neo4j配置
| 环境变量 | 描述 | 默认值 | 必须 |
|----------|------|--------|------|
| `NEO4J_URI` | Neo4j连接URI | `bolt://neo4j:7687` | 是 |
| `NEO4J_USER` | Neo4j用户名 | `neo4j` | 是 |
| `NEO4J_PASSWORD` | Neo4j密码 | `password` | 是 |

#### 3.1.3 Redis配置
| 环境变量 | 描述 | 默认值 | 必须 |
|----------|------|--------|------|
| `REDIS_URL` | Redis连接URL | `redis://redis:6379` | 是 |
| `REDIS_PASSWORD` | Redis密码 | 空 | 否 |
| `REDIS_DB` | Redis数据库索引 | `0` | 否 |

#### 3.1.4 LLM配置
| 环境变量 | 描述 | 默认值 | 必须 |
|----------|------|--------|------|
| `DASHSCOPE_API_KEY` | 阿里云通义千问API密钥 | 空 | 是 |
| `LLM_MODEL` | LLM模型名称 | `qwen-turbo` | 否 |
| `LLM_TIMEOUT` | LLM调用超时时间（秒） | `30` | 否 |
| `LLM_RETRY_COUNT` | LLM调用重试次数 | `3` | 否 |

#### 3.1.5 Celery配置
| 环境变量 | 描述 | 默认值 | 必须 |
|----------|------|--------|------|
| `CELERY_BROKER_URL` | Celery消息代理URL | `redis://redis:6379/0` | 是 |
| `CELERY_RESULT_BACKEND` | Celery结果后端URL | `redis://redis:6379/0` | 是 |

### 3.2 前端环境变量
| 环境变量 | 描述 | 默认值 | 必须 |
|----------|------|--------|------|
| `NEXT_PUBLIC_API_URL` | 后端API地址 | `http://localhost:8000` | 是 |
| `NEXT_PUBLIC_ENV` | 运行环境 | `development` | 否 |

## 4. 服务管理

### 4.1 后端服务

#### 4.1.1 启动命令
```bash
# 开发模式
uvicorn app.main:app --reload

# 生产模式
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

#### 4.1.2 Celery服务
```bash
# 启动Celery worker
celery -A app.celery_app worker --loglevel=info

# 启动Celery beat（定时任务）
celery -A app.celery_app beat --loglevel=info

# 启动Flower监控
celery -A app.celery_app flower
```

### 4.2 前端服务

#### 4.2.1 启动命令
```bash
# 开发模式
npm run dev

# 生产构建
npm run build

# 生产模式启动
npm run start
```

## 5. 常见问题排查

### 5.1 服务无法启动
1. 检查环境变量配置是否正确
2. 检查端口是否被占用
3. 查看日志获取详细错误信息：
   ```bash
   docker-compose logs <service-name>
   ```

### 5.2 Neo4j连接失败
1. 检查Neo4j服务是否正常运行
2. 验证Neo4j用户名和密码是否正确
3. 检查网络连接是否正常

### 5.3 LLM调用失败
1. 检查API密钥是否正确配置
2. 验证网络连接是否正常
3. 查看LLM服务是否有调用次数限制

### 5.4 前端无法访问后端API
1. 检查CORS配置是否允许前端域名
2. 验证后端服务是否正常运行
3. 检查API地址是否正确配置

## 6. 监控与日志

### 6.1 日志位置
- **后端日志**: `backend/logs/`
- **前端日志**: 浏览器控制台
- **Docker日志**: 使用`docker-compose logs`命令查看

### 6.2 监控工具
- **API监控**: 访问`/docs`查看API状态
- **Celery监控**: 访问Flower界面（http://localhost:5555）
- **Neo4j监控**: 访问Neo4j浏览器（http://localhost:7474）

## 7. 升级指南

### 7.1 代码更新
1. 拉取最新代码：
   ```bash
   git pull origin main
   ```

2. 重新构建Docker镜像：
   ```bash
   docker-compose build --no-cache
   ```

3. 重启服务：
   ```bash
   docker-compose down
   docker-compose up -d
   ```

### 7.2 数据迁移
- 若涉及数据库结构变更，请按照发布说明执行相应的数据迁移脚本。

## 8. 安全建议

1. **生产环境中禁用DEBUG模式**
2. **使用强密码保护所有服务**
3. **配置合适的防火墙规则**
4. **定期更新依赖包**
5. **启用HTTPS**
6. **限制API访问频率**
7. **定期备份数据**

## 9. 联系支持

若遇到部署问题，请联系技术支持团队或查阅项目文档。