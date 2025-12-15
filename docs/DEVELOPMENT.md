# 开发指南

本文档提供详细的开发环境设置和开发流程说明。

## 环境要求

### 必需
- Docker 27.x+
- Docker Compose v2
- Git

### 本地开发（可选）
- Python 3.12+
- Node.js 20+
- npm 或 yarn

## 快速开始

### 1. 克隆项目

```bash
git clone <repository-url>
cd education-knowledge-graph
```

### 2. 配置环境变量

```bash
cp .env.example .env
```

编辑 `.env` 文件，设置必要的环境变量，特别是：
- `OPENAI_API_KEY`: 你的 OpenAI API 密钥

### 3. 启动开发环境

使用快速启动脚本：
```bash
./start.sh
```

或手动启动：
```bash
docker-compose up -d
```

### 4. 验证服务

访问以下地址确认服务正常运行：
- 前端: http://localhost:3000
- 后端 API: http://localhost:8000
- API 文档: http://localhost:8000/docs
- Neo4j Browser: http://localhost:7474

## 本地开发设置

### 后端开发

1. 创建虚拟环境：
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

2. 安装依赖：
```bash
pip install -e ".[dev]"
```

3. 配置环境变量：
```bash
cp .env.example .env
# 编辑 .env 文件
```

4. 启动开发服务器：
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

5. 运行测试：
```bash
# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/test_example.py

# 运行带覆盖率的测试
pytest --cov=app --cov-report=html
```

6. 代码检查：
```bash
# 使用 Ruff 检查代码
ruff check .

# 自动修复问题
ruff check --fix .

# 格式化代码
ruff format .

# 类型检查
mypy app
```

### 前端开发

1. 安装依赖：
```bash
cd frontend
npm install
```

2. 配置环境变量：
```bash
cp .env.example .env.local
# 编辑 .env.local 文件
```

3. 启动开发服务器：
```bash
npm run dev
```

4. 构建生产版本：
```bash
npm run build
```

5. 运行测试：
```bash
npm test
```

6. 代码检查：
```bash
npm run lint
```

## 开发工作流

### 1. 创建新功能

1. 创建新分支：
```bash
git checkout -b feature/your-feature-name
```

2. 实现功能
3. 编写测试
4. 运行测试确保通过
5. 提交代码

### 2. 后端 API 开发

1. 在 `backend/app/models/` 创建数据模型
2. 在 `backend/app/services/` 实现业务逻辑
3. 在 `backend/app/routers/` 创建 API 端点
4. 在 `backend/tests/` 编写测试

示例：
```python
# backend/app/routers/example.py
from fastapi import APIRouter

router = APIRouter(prefix="/api/example", tags=["example"])

@router.get("/")
async def get_example():
    return {"message": "Hello World"}
```

### 3. 前端组件开发

1. 在 `frontend/components/` 创建组件
2. 在 `frontend/app/` 创建页面
3. 使用 TanStack Query 获取数据
4. 使用 Zustand 管理状态

示例：
```typescript
// frontend/components/Example.tsx
export function Example() {
  return <div>Hello World</div>
}
```

### 4. 图数据库操作

使用 Neo4j Browser (http://localhost:7474) 进行查询和调试：

```cypher
// 查看所有节点
MATCH (n) RETURN n LIMIT 25

// 创建测试节点
CREATE (s:Student {studentId: "S001", name: "张三"})

// 查询特定类型节点
MATCH (s:Student) RETURN s
```

## 测试策略

### 单元测试

测试单个函数或类的行为：

```python
# backend/tests/test_example.py
def test_example():
    assert 1 + 1 == 2
```

### 基于属性的测试 (PBT)

使用 Hypothesis 测试通用属性：

```python
from hypothesis import given
import hypothesis.strategies as st

@given(st.integers(), st.integers())
def test_addition_commutative(a, b):
    assert a + b == b + a
```

### 集成测试

测试多个组件的交互：

```python
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_api_endpoint():
    response = client.get("/")
    assert response.status_code == 200
```

## 调试技巧

### 后端调试

1. 使用 Python 调试器：
```python
import pdb; pdb.set_trace()
```

2. 查看日志：
```bash
docker-compose logs -f backend
```

3. 进入容器：
```bash
docker-compose exec backend bash
```

### 前端调试

1. 使用浏览器开发者工具
2. 查看 Next.js 日志：
```bash
docker-compose logs -f frontend
```

### 数据库调试

1. 使用 Neo4j Browser: http://localhost:7474
2. 查看 Redis 数据：
```bash
docker-compose exec redis redis-cli
```

## 常见问题

### 端口冲突

如果端口被占用，修改 `docker-compose.yml` 中的端口映射。

### 依赖安装失败

清理缓存后重试：
```bash
# Python
pip cache purge

# Node.js
npm cache clean --force
```

### Docker 容器无法启动

查看日志：
```bash
docker-compose logs <service-name>
```

重建容器：
```bash
docker-compose down
docker-compose up --build
```

## 代码规范

### Python

- 遵循 PEP 8
- 使用类型提示
- 编写文档字符串
- 最大行长度: 100

### TypeScript

- 使用 ESLint 规则
- 使用严格模式
- 编写 JSDoc 注释

### Git 提交

使用语义化提交消息：
```
feat: 添加新功能
fix: 修复 bug
docs: 更新文档
test: 添加测试
refactor: 重构代码
style: 代码格式化
chore: 构建配置
```

## 性能优化

### 后端

- 使用 Redis 缓存
- 批量处理数据
- 异步处理耗时任务
- 优化数据库查询

### 前端

- 使用 Next.js 图片优化
- 懒加载组件
- 使用 React.memo
- 优化图可视化渲染

## 部署

参考 README.md 中的部署章节。

## 获取帮助

- 查看 API 文档: http://localhost:8000/docs
- 查看项目 README
- 提交 Issue

## 贡献

欢迎贡献！请遵循以下流程：

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request
