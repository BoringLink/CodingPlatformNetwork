# Celery任务队列使用指南

本文档介绍如何使用Celery任务队列进行异步数据处理和LLM分析。

## 概述

系统使用Celery实现异步任务处理，主要包括：

1. **数据导入任务** - 批量导入教育数据到图数据库
2. **LLM分析任务** - 异步调用大语言模型进行智能分析
3. **任务监控** - 使用Flower实时监控任务状态

## 架构

```
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│   FastAPI   │─────▶│   Celery    │─────▶│   Worker    │
│   应用      │      │   Broker    │      │   进程      │
└─────────────┘      │  (Redis)    │      └─────────────┘
                     └─────────────┘             │
                            │                    │
                            ▼                    ▼
                     ┌─────────────┐      ┌─────────────┐
                     │   Result    │      │   Graph DB  │
                     │   Backend   │      │   / LLM     │
                     │  (Redis)    │      └─────────────┘
                     └─────────────┘
```

## 配置

### 环境变量

在 `.env` 文件中配置：

```bash
# Celery配置
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Flower监控配置
FLOWER_USER=admin
FLOWER_PASSWORD=admin
```

### Celery配置说明

在 `app/celery_app.py` 中配置了以下特性：

- **任务序列化**: JSON格式
- **结果过期**: 1小时
- **任务确认**: 延迟确认（任务完成后才确认）
- **重试机制**: 默认最多重试3次，指数退避
- **速率限制**: 默认每分钟100个任务
- **任务路由**: 
  - `data_import` 队列：数据导入任务
  - `llm_analysis` 队列：LLM分析任务

## 启动服务

### 1. 启动Redis

```bash
# 使用Docker启动Redis
docker run -d -p 6379:6379 redis:7.2

# 或使用docker-compose
docker-compose up -d redis
```

### 2. 启动Celery Worker

```bash
# 方式1: 使用启动脚本
cd backend
./start_celery_worker.sh

# 方式2: 直接使用celery命令
celery -A app.celery_app worker \
    --loglevel=info \
    --queues=data_import,llm_analysis \
    --concurrency=4
```

Worker参数说明：
- `--loglevel`: 日志级别（debug, info, warning, error）
- `--queues`: 监听的队列列表
- `--concurrency`: 并发worker数量
- `--max-tasks-per-child`: 每个worker子进程最多处理的任务数
- `--time-limit`: 任务硬超时时间（秒）
- `--soft-time-limit`: 任务软超时时间（秒）

### 3. 启动Flower监控

```bash
# 使用启动脚本
cd backend
./start_flower.sh

# 访问监控界面
# http://localhost:5555
# 用户名: admin
# 密码: admin
```

## 使用示例

### 1. 数据导入任务

#### 同步导入（阻塞）

```python
from app.services.data_import_service import DataImportService, RawRecord, RecordType
from datetime import datetime

# 创建服务实例
import_service = DataImportService()

# 准备数据
records = [
    RawRecord(
        type=RecordType.STUDENT_INTERACTION,
        timestamp=datetime.utcnow(),
        data={
            "student_id_from": "S001",
            "student_id_to": "S002",
            "interaction_type": "chat",
            "message_count": 5,
        }
    ),
    # ... 更多记录
]

# 执行导入
result = await import_service.import_batch(records, batch_size=1000)
print(f"成功: {result.success_count}, 失败: {result.failure_count}")
```

#### 异步导入（非阻塞）

```python
from app.tasks.data_import import import_batch_task, import_records_async

# 准备数据（字典格式）
records_data = [
    {
        "type": "student_interaction",
        "timestamp": "2024-01-01T10:00:00",
        "data": {
            "student_id_from": "S001",
            "student_id_to": "S002",
            "interaction_type": "chat",
            "message_count": 5,
        }
    },
    # ... 更多记录
]

# 方式1: 单批次异步导入
task = import_batch_task.delay(records_data, batch_size=1000)
print(f"任务ID: {task.id}")

# 检查任务状态
print(f"状态: {task.state}")

# 获取结果（阻塞直到完成）
result = task.get(timeout=300)
print(f"成功: {result['success_count']}, 失败: {result['failure_count']}")

# 方式2: 多批次并行导入
group_id = import_records_async.delay(records_data, batch_size=1000, parallel_batches=4)
print(f"任务组ID: {group_id}")
```

#### 使用Chord模式（并行+聚合）

```python
from app.tasks.data_import import import_records_with_callback

# 并行处理所有批次，然后聚合结果
chord_id = import_records_with_callback.delay(records_data, batch_size=1000)
print(f"Chord任务ID: {chord_id}")

# 获取聚合结果
from celery.result import AsyncResult
result = AsyncResult(chord_id)
aggregated = result.get(timeout=600)
print(f"总成功: {aggregated['total_success']}")
print(f"总失败: {aggregated['total_failure']}")
```

### 2. LLM分析任务

#### 分析互动内容

```python
from app.tasks.llm_analysis import analyze_interaction_task

# 异步分析
task = analyze_interaction_task.delay(
    text="小明和小红讨论了数学作业中的分数加法问题",
    interaction_id="INT001"
)

# 获取结果
result = task.get(timeout=60)
print(f"情感: {result['sentiment']}")
print(f"主题: {result['topics']}")
print(f"置信度: {result['confidence']}")
```

#### 分析错误记录

```python
from app.tasks.llm_analysis import analyze_error_task

# 异步分析
task = analyze_error_task.delay(
    error_text="学生在计算 1/2 + 1/3 时，直接将分子分母相加得到 2/5",
    error_id="ERR001",
    course_id="C001",
    course_name="小学数学",
    course_description="小学三年级数学课程"
)

# 获取结果
result = task.get(timeout=60)
print(f"错误类型: {result['error_type']}")
print(f"相关知识点: {result['related_knowledge_points']}")
print(f"难度: {result['difficulty']}")
```

#### 提取知识点

```python
from app.tasks.llm_analysis import extract_knowledge_points_task

# 异步提取
task = extract_knowledge_points_task.delay(
    course_content="""
    本课程介绍分数的基本概念和运算。
    主要内容包括：
    1. 分数的定义和表示
    2. 分数的比较
    3. 分数的加减法
    4. 分数的乘除法
    """,
    course_id="C001"
)

# 获取结果
result = task.get(timeout=60)
for kp in result['knowledge_points']:
    print(f"知识点: {kp['name']}")
    print(f"描述: {kp['description']}")
    print(f"依赖: {kp['dependencies']}")
```

#### 批量分析

```python
from app.tasks.llm_analysis import batch_analyze_interactions_task, batch_analyze_errors_task

# 批量分析互动
interactions = [
    {"text": "互动内容1", "interaction_id": "INT001"},
    {"text": "互动内容2", "interaction_id": "INT002"},
    # ... 更多互动
]
group_id = batch_analyze_interactions_task.delay(interactions)

# 批量分析错误
errors = [
    {
        "error_text": "错误内容1",
        "error_id": "ERR001",
        "course_id": "C001",
        "course_name": "数学",
    },
    # ... 更多错误
]
group_id = batch_analyze_errors_task.delay(errors)
```

### 3. 任务状态查询

```python
from celery.result import AsyncResult

# 通过任务ID查询状态
task_id = "abc123..."
result = AsyncResult(task_id)

# 检查状态
print(f"状态: {result.state}")
# 可能的状态: PENDING, STARTED, SUCCESS, FAILURE, RETRY, REVOKED

# 检查是否完成
if result.ready():
    print("任务已完成")
    
    # 检查是否成功
    if result.successful():
        print(f"结果: {result.result}")
    else:
        print(f"错误: {result.info}")
else:
    print("任务进行中...")

# 等待完成（带超时）
try:
    result_data = result.get(timeout=300)
    print(f"结果: {result_data}")
except TimeoutError:
    print("任务超时")
```

### 4. 任务撤销

```python
from celery.result import AsyncResult

# 撤销任务
task_id = "abc123..."
AsyncResult(task_id).revoke(terminate=True)
```

## 错误处理

### 自动重试

所有任务都配置了自动重试机制：

- **最大重试次数**: 3次
- **重试策略**: 指数退避（1秒、2秒、4秒...）
- **最大退避时间**: 10分钟
- **随机抖动**: 启用（避免重试风暴）

### 错误日志

任务失败时会自动记录详细日志：

```python
# 查看日志
tail -f celery_worker.log

# 日志包含：
# - 任务ID
# - 任务名称
# - 错误类型
# - 错误消息
# - 重试次数
```

### 死信队列

失败的任务会被记录到结果后端，可以通过Flower查看：

1. 访问 http://localhost:5555
2. 点击 "Tasks" 标签
3. 筛选状态为 "FAILURE" 的任务
4. 查看错误详情和堆栈跟踪

## 性能优化

### 1. 速率限制

LLM分析任务配置了速率限制（每分钟100个请求），符合需求7.2：

```python
# 在任务类中配置
class LLMAnalysisTask(Task):
    rate_limit = "100/m"  # 每分钟100个请求
```

### 2. 并发控制

通过调整worker并发数控制资源使用：

```bash
# 低并发（节省资源）
celery -A app.celery_app worker --concurrency=2

# 高并发（提高吞吐量）
celery -A app.celery_app worker --concurrency=8
```

### 3. 队列优先级

为重要任务设置更高优先级：

```python
# 高优先级任务
task.apply_async(args=[...], priority=9)

# 低优先级任务
task.apply_async(args=[...], priority=1)
```

### 4. 任务预取

控制worker预取任务数量：

```bash
# 每次只预取1个任务（避免阻塞）
celery -A app.celery_app worker --prefetch-multiplier=1

# 预取多个任务（提高吞吐量）
celery -A app.celery_app worker --prefetch-multiplier=4
```

## 监控和调试

### Flower监控界面

访问 http://localhost:5555 查看：

1. **Dashboard**: 任务统计、成功率、失败率
2. **Tasks**: 任务列表、状态、执行时间
3. **Workers**: Worker状态、负载、内存使用
4. **Monitor**: 实时任务流
5. **Broker**: 队列状态、消息数量

### 命令行工具

```bash
# 查看活跃任务
celery -A app.celery_app inspect active

# 查看已注册任务
celery -A app.celery_app inspect registered

# 查看统计信息
celery -A app.celery_app inspect stats

# 查看队列状态
celery -A app.celery_app inspect active_queues

# 清空队列
celery -A app.celery_app purge
```

## 生产环境部署

### 使用Supervisor管理进程

创建 `/etc/supervisor/conf.d/celery.conf`:

```ini
[program:celery_worker]
command=/path/to/venv/bin/celery -A app.celery_app worker --loglevel=info --queues=data_import,llm_analysis --concurrency=4
directory=/path/to/backend
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/celery/worker.log

[program:celery_flower]
command=/path/to/venv/bin/celery -A app.celery_app flower --port=5555
directory=/path/to/backend
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/celery/flower.log
```

### 使用Docker

参考 `docker-compose.yml` 中的配置：

```yaml
services:
  celery_worker:
    build: ./backend
    command: celery -A app.celery_app worker --loglevel=info --queues=data_import,llm_analysis
    depends_on:
      - redis
      - neo4j
    environment:
      - CELERY_BROKER_URL=redis://redis:6379/0
      - CELERY_RESULT_BACKEND=redis://redis:6379/0
  
  flower:
    build: ./backend
    command: celery -A app.celery_app flower --port=5555
    ports:
      - "5555:5555"
    depends_on:
      - redis
      - celery_worker
```

## 故障排查

### 问题1: 任务一直处于PENDING状态

**原因**: Worker未启动或未监听正确的队列

**解决**:
```bash
# 检查worker是否运行
ps aux | grep celery

# 检查队列配置
celery -A app.celery_app inspect active_queues

# 重启worker
./start_celery_worker.sh
```

### 问题2: 任务执行失败

**原因**: 依赖服务不可用（Redis、Neo4j、LLM API）

**解决**:
```bash
# 检查Redis连接
redis-cli ping

# 检查Neo4j连接
curl http://localhost:7474

# 查看任务错误日志
celery -A app.celery_app inspect stats
```

### 问题3: 内存占用过高

**原因**: Worker并发数过高或任务泄漏

**解决**:
```bash
# 降低并发数
celery -A app.celery_app worker --concurrency=2

# 设置任务数量限制
celery -A app.celery_app worker --max-tasks-per-child=100

# 重启worker释放内存
supervisorctl restart celery_worker
```

## 最佳实践

1. **任务幂等性**: 确保任务可以安全重试
2. **任务超时**: 为长时间运行的任务设置超时
3. **结果清理**: 定期清理过期的任务结果
4. **监控告警**: 配置Flower告警通知
5. **日志记录**: 记录详细的任务执行日志
6. **错误处理**: 优雅处理异常，避免任务失败
7. **资源限制**: 合理配置并发数和内存限制

## 参考资料

- [Celery官方文档](https://docs.celeryq.dev/)
- [Flower文档](https://flower.readthedocs.io/)
- [Redis文档](https://redis.io/docs/)
