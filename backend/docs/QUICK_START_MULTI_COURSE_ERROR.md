# 多课程多错误处理 - 快速开始指南

## 5 分钟快速上手

### 1. 创建学生在课程中的错误记录

```python
from app.services.graph_service import graph_service
from datetime import datetime

# 学生在数学课程中犯了错误
result = await graph_service.create_student_multi_course_error(
    student_id="S001",              # 学生 ID
    error_type_id="E001",           # 错误类型 ID
    course_id="C_MATH",             # 课程 ID
    occurrence_time=datetime.now(), # 发生时间
    knowledge_point_ids=["KP001", "KP002"],  # 相关知识点（可选）
)

print(f"创建成功！发生次数: {result['relationship'].properties['occurrence_count']}")
```

### 2. 查看学生的所有错误统计

```python
# 获取学生的完整错误统计
stats = await graph_service.aggregate_student_errors("S001")

print(f"总错误次数: {stats['total_errors']}")
print(f"涉及课程: {list(stats['errors_by_course'].keys())}")
print(f"涉及知识点: {list(stats['errors_by_knowledge_point'].keys())}")
```

### 3. 查找两个课程的共同知识点

```python
# 查找数学和物理课程的共同知识点
paths = await graph_service.find_cross_course_knowledge_point_paths(
    course_id_1="C_MATH",
    course_id_2="C_PHYSICS",
)

for path in paths:
    print(f"共享知识点: {path['knowledge_point_name']}")
```

## 常见使用场景

### 场景 1: 学生重复犯错

```python
# 第一次错误
await graph_service.create_student_multi_course_error(
    student_id="S001",
    error_type_id="E001",
    course_id="C001",
    occurrence_time=datetime(2024, 1, 10),
)

# 第二次相同错误（自动更新权重）
await graph_service.create_student_multi_course_error(
    student_id="S001",
    error_type_id="E001",
    course_id="C001",
    occurrence_time=datetime(2024, 1, 20),
)

# 权重会自动从 1.0 增加到 2.0
```

### 场景 2: 分析高频错误知识点

```python
stats = await graph_service.aggregate_student_errors("S001")

# 找出错误次数最多的知识点
high_frequency_kps = sorted(
    stats['errors_by_knowledge_point'].items(),
    key=lambda x: x[1]['count'],
    reverse=True
)[:5]  # 前 5 个

for kp_id, kp_stats in high_frequency_kps:
    print(f"{kp_id}: {kp_stats['count']} 次错误")
```

### 场景 3: 关联错误类型和知识点

```python
# 将一个错误类型关联到多个知识点
relationships = await graph_service.associate_error_with_knowledge_points(
    error_type_id="E001",
    knowledge_point_ids=["KP001", "KP002", "KP003"],
    strength=0.9,      # 关联强度
    confidence=0.95,   # 置信度
)

print(f"创建了 {len(relationships)} 个关联关系")
```

## API 参考

### create_student_multi_course_error()

创建学生多课程错误记录。

**参数**:
- `student_id` (str): 学生 ID
- `error_type_id` (str): 错误类型 ID
- `course_id` (str): 课程 ID
- `occurrence_time` (datetime): 错误发生时间
- `knowledge_point_ids` (List[str], 可选): 相关知识点 ID 列表

**返回**:
```python
{
    "relationship": Relationship,           # HAS_ERROR 关系
    "relates_to_relationships": List[Relationship],  # RELATES_TO 关系列表
    "is_new": bool,                        # 是否为新记录
}
```

### aggregate_student_errors()

聚合学生的所有错误统计。

**参数**:
- `student_id` (str): 学生 ID

**返回**:
```python
{
    "student_id": str,
    "total_errors": int,
    "errors_by_course": Dict[str, Dict],
    "errors_by_knowledge_point": Dict[str, Dict],
    "errors_by_type": Dict[str, Dict],
    "error_details": List[Dict],
}
```

### find_cross_course_knowledge_point_paths()

查找跨课程知识点路径。

**参数**:
- `course_id_1` (str): 第一个课程 ID
- `course_id_2` (str): 第二个课程 ID
- `max_depth` (int, 可选): 最大路径深度，默认 3

**返回**:
```python
[
    {
        "knowledge_point_id": str,
        "knowledge_point_name": str,
        "path_length": int,
        "nodes": List[Dict],
        "relationship_types": List[str],
    },
    ...
]
```

## 运行演示

```bash
# 1. 启动 Neo4j 数据库
docker-compose up neo4j -d

# 2. 运行演示脚本
cd backend
python demo_multi_course_error.py
```

## 运行测试

```bash
# 运行所有多课程多错误处理测试
cd backend
pytest tests/test_graph_service.py -k "multi_course" -v

# 运行特定测试
pytest tests/test_graph_service.py::test_create_student_multi_course_error -v
```

## 故障排除

### 问题 1: 节点不存在

**错误**: `ValueError: Student or ErrorType not found`

**解决**: 确保在创建错误记录之前，学生和错误类型节点已经存在。

```python
# 先创建节点
student = await graph_service.create_node(
    NodeType.STUDENT,
    {"student_id": "S001", "name": "张三"}
)

error_type = await graph_service.create_node(
    NodeType.ERROR_TYPE,
    {
        "error_type_id": "E001",
        "name": "概念理解错误",
        "description": "对基本概念理解不正确",
    }
)

# 再创建错误记录
result = await graph_service.create_student_multi_course_error(...)
```

### 问题 2: 数据库连接失败

**错误**: `neo4j.exceptions.ServiceUnavailable`

**解决**: 确保 Neo4j 数据库正在运行。

```bash
# 检查 Neo4j 状态
docker-compose ps neo4j

# 启动 Neo4j
docker-compose up neo4j -d

# 查看日志
docker-compose logs neo4j
```

### 问题 3: 权重未更新

**问题**: 重复错误的权重没有增加

**解决**: 确保使用相同的 `student_id`、`error_type_id` 和 `course_id`。系统会自动检测重复并更新权重。

```python
# 正确：相同的三个 ID
await graph_service.create_student_multi_course_error(
    student_id="S001",
    error_type_id="E001",
    course_id="C001",
    occurrence_time=datetime(2024, 1, 10),
)

await graph_service.create_student_multi_course_error(
    student_id="S001",      # 相同
    error_type_id="E001",   # 相同
    course_id="C001",       # 相同
    occurrence_time=datetime(2024, 1, 20),
)
# 权重会从 1.0 增加到 2.0
```

## 更多信息

- 完整文档: `MULTI_COURSE_ERROR_HANDLING.md`
- 实施总结: `TASK_9_IMPLEMENTATION_SUMMARY.md`
- 测试文件: `tests/test_graph_service.py`
- 演示脚本: `demo_multi_course_error.py`
