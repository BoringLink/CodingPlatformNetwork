# Celery快速入门

## 5分钟快速开始

### 1. 安装依赖

```bash
cd backend
pip install -e ".[dev]"
```

### 2. 配置环境变量

复制 `.env.example` 到 `.env` 并配置：

```bash
cp .env.example .env

# 编辑 .env 文件
# 必需配置：
# - DASHSCOPE_API_KEY（如果使用LLM任务）
# - CELERY_BROKER_URL（默认：redis://localhost:6379/0）
# - CELERY_RESULT_BACKEND（默认：redis://localhost:6379/0）
```

### 3. 启动Redis

```bash
# 使用Docker
docker run -d -p 6379:6379 redis:7.2

# 或使用docker-compose
docker-compose up -d redis
```

### 4. 启动Celery Worker

```bash
# 方式1: 使用Makefile
make celery-worker

# 方式2: 使用启动脚本
./start_celery_worker.sh

# 方式3: 直接使用celery命令
celery -A app.celery_app worker --loglevel=info --queues=data_import,llm_analysis
```

### 5. 启动Flower监控（可选）

```bash
# 使用Makefile
make celery-flower

# 访问 http://localhost:5555
# 用户名: admin
# 密码: admin
```

### 6. 提交第一个任务

```python
from app.tasks.data_import import import_batch_task
from datetime import datetime

# 准备测试数据
records_data = [
    {
        "type": "student_interaction",
        "timestamp": datetime.utcnow().isoformat(),
        "data": {
            "student_id_from": "S001",
            "student_id_to": "S002",
            "interaction_type": "chat",
            "message_count": 5,
        }
    }
]

# 提交任务
task = import_batch_task.delay(records_data, batch_size=100)
print(f"任务ID: {task.id}")

# 等待结果
result = task.get(timeout=30)
print(f"成功: {result['success_count']}")
```

## 常用命令

```bash
# 启动Worker
make celery-worker

# 启动Flower
make celery-flower

# 查看状态
make celery-status

# 清空队列
make celery-purge

# 测试集成
make test-celery
```

## 任务类型

### 数据导入任务

```python
from app.tasks.data_import import import_batch_task

task = import_batch_task.delay(records_data, batch_size=1000)
result = task.get(timeout=300)
```

### LLM分析任务

```python
from app.tasks.llm_analysis import analyze_interaction_task

task = analyze_interaction_task.delay(
    text="互动内容",
    interaction_id="INT001"
)
result = task.get(timeout=60)
```

## 监控

访问 http://localhost:5555 查看：

- 任务状态和历史
- Worker状态
- 队列状态
- 实时任务流

## 故障排查

### 问题: 任务一直PENDING

**解决**: 检查Worker是否启动

```bash
ps aux | grep celery
make celery-status
```

### 问题: Redis连接失败

**解决**: 检查Redis是否运行

```bash
redis-cli ping
# 应该返回: PONG
```

### 问题: 任务失败

**解决**: 查看日志

```bash
# 查看Worker日志
tail -f celery_worker.log

# 或在Flower中查看错误详情
# http://localhost:5555/tasks
```

## 更多信息

详细文档请参考：

- [CELERY_USAGE.md](./CELERY_USAGE.md) - 完整使用指南
- [CELERY_IMPLEMENTATION_SUMMARY.md](./CELERY_IMPLEMENTATION_SUMMARY.md) - 实施总结
