# 多课程多错误处理功能文档

## 概述

本模块实现了教育知识图谱系统中的多课程多错误处理功能，支持学生在多个课程中产生错误的场景，并提供错误统计、聚合和跨课程分析能力。

## 功能特性

### 1. 学生多课程错误记录创建

**方法**: `create_student_multi_course_error()`

为学生在特定课程中的错误创建独立的 `HAS_ERROR` 关系，并自动关联到相关知识点。

**特点**:
- 同一学生在不同课程中的相同错误类型会创建独立的关系
- 自动检测重复错误并更新发生次数和权重
- 支持关联多个知识点
- 自动创建错误类型到知识点的 `RELATES_TO` 关系

**示例**:
```python
result = await graph_service.create_student_multi_course_error(
    student_id="S001",
    error_type_id="E001",
    course_id="C001",
    occurrence_time=datetime(2024, 1, 10),
    knowledge_point_ids=["KP001", "KP002"],
)

# 返回结果包含:
# - relationship: 创建的 HAS_ERROR 关系
# - relates_to_relationships: 创建的 RELATES_TO 关系列表
# - is_new: 是否为新创建的记录
```

### 2. 错误类型多知识点关联

**方法**: `associate_error_with_knowledge_points()`

将一个错误类型关联到多个知识点，创建 `RELATES_TO` 关系。

**特点**:
- 支持批量关联多个知识点
- 可配置关联强度和置信度
- 自动跳过已存在的关系
- 返回所有创建的关系

**示例**:
```python
relationships = await graph_service.associate_error_with_knowledge_points(
    error_type_id="E001",
    knowledge_point_ids=["KP001", "KP002", "KP003"],
    strength=0.9,
    confidence=0.95,
)

# 返回创建的 RELATES_TO 关系列表
```

### 3. 错误统计聚合

**方法**: `aggregate_student_errors()`

聚合学生的所有错误关系，生成多维度的错误分布统计。

**统计维度**:
- 总错误次数
- 按课程统计（每个课程的错误次数和错误类型）
- 按知识点统计（每个知识点的错误次数和错误类型）
- 按错误类型统计（每种错误的次数和涉及的课程）
- 详细错误列表（包含时间、课程、知识点等信息）

**示例**:
```python
stats = await graph_service.aggregate_student_errors("S001")

# 返回结果结构:
{
    "student_id": "S001",
    "total_errors": 5,
    "errors_by_course": {
        "C001": {
            "count": 3,
            "error_types": [...]
        },
        "C002": {
            "count": 2,
            "error_types": [...]
        }
    },
    "errors_by_knowledge_point": {
        "KP001": {
            "count": 4,
            "error_types": [...]
        }
    },
    "errors_by_type": {
        "E001": {
            "name": "概念理解错误",
            "count": 3,
            "courses": ["C001", "C002"]
        }
    },
    "error_details": [...]
}
```

### 4. 跨课程知识点路径查询

**方法**: `find_cross_course_knowledge_point_paths()`

查找通过共同知识点连接两个课程的路径。

**特点**:
- 识别两个课程共享的知识点
- 返回完整的路径信息（节点和关系）
- 按路径长度排序
- 限制返回最多 100 条路径

**示例**:
```python
paths = await graph_service.find_cross_course_knowledge_point_paths(
    course_id_1="C001",
    course_id_2="C002",
    max_depth=3,
)

# 返回路径列表，每个路径包含:
# - knowledge_point_id: 共享知识点 ID
# - knowledge_point_name: 共享知识点名称
# - path_length: 路径长度
# - nodes: 路径中的所有节点
# - relationship_types: 路径中的关系类型
```

### 5. 重复错误权重更新

**方法**: `update_repeated_error_weight()`

当学生在同一知识点上重复出错时，增加对应 `HAS_ERROR` 关系的权重值。

**特点**:
- 自动增加发生次数
- 更新最后发生时间
- 权重值等于发生次数
- 支持错误趋势分析

**示例**:
```python
updated_rel = await graph_service.update_repeated_error_weight(
    student_id="S001",
    error_type_id="E001",
    course_id="C001",
)

# 返回更新后的关系，包含新的权重和发生次数
```

## 数据模型

### HAS_ERROR 关系属性

```python
{
    "occurrence_count": int,      # 发生次数
    "first_occurrence": datetime, # 首次发生时间
    "last_occurrence": datetime,  # 最后发生时间
    "course_id": str,            # 课程 ID
    "resolved": bool,            # 是否已解决
    "weight": float,             # 权重（等于发生次数）
}
```

### RELATES_TO 关系属性

```python
{
    "strength": float,    # 关联强度（0-1）
    "confidence": float,  # 置信度（0-1）
    "weight": float,      # 权重（等于关联强度）
}
```

## 使用场景

### 场景 1: 学生在多个课程中犯相同错误

```python
# 学生在数学课程中犯了"概念理解错误"
await graph_service.create_student_multi_course_error(
    student_id="S001",
    error_type_id="E_CONCEPT_ERROR",
    course_id="C_MATH",
    occurrence_time=datetime.now(),
    knowledge_point_ids=["KP_CALCULUS"],
)

# 同一学生在物理课程中也犯了"概念理解错误"
await graph_service.create_student_multi_course_error(
    student_id="S001",
    error_type_id="E_CONCEPT_ERROR",
    course_id="C_PHYSICS",
    occurrence_time=datetime.now(),
    knowledge_point_ids=["KP_MECHANICS"],
)

# 系统会创建两个独立的 HAS_ERROR 关系
```

### 场景 2: 分析学生的错误模式

```python
# 获取学生的完整错误统计
stats = await graph_service.aggregate_student_errors("S001")

# 识别高频错误知识点
high_frequency_kps = [
    kp_id for kp_id, kp_stats in stats["errors_by_knowledge_point"].items()
    if kp_stats["count"] >= 3
]

# 识别需要重点关注的课程
problematic_courses = [
    course_id for course_id, course_stats in stats["errors_by_course"].items()
    if course_stats["count"] >= 5
]
```

### 场景 3: 发现跨课程的知识关联

```python
# 查找两个课程的共同知识点
paths = await graph_service.find_cross_course_knowledge_point_paths(
    course_id_1="C_MATH",
    course_id_2="C_PHYSICS",
)

# 分析共享知识点
shared_kps = [path["knowledge_point_id"] for path in paths]

# 这可以帮助:
# - 发现跨学科的知识依赖
# - 优化课程设计
# - 提供个性化学习建议
```

## 性能考虑

### 批量操作

对于大量错误记录的创建，建议使用批量操作：

```python
# 批量创建错误记录
for error_data in error_records:
    await graph_service.create_student_multi_course_error(
        student_id=error_data["student_id"],
        error_type_id=error_data["error_type_id"],
        course_id=error_data["course_id"],
        occurrence_time=error_data["occurrence_time"],
        knowledge_point_ids=error_data["knowledge_point_ids"],
    )
```

### 缓存策略

对于频繁查询的统计数据，建议使用 Redis 缓存：

```python
# 缓存学生错误统计（有效期 1 小时）
cache_key = f"student_errors:{student_id}"
cached_stats = await redis_client.get(cache_key)

if cached_stats:
    stats = json.loads(cached_stats)
else:
    stats = await graph_service.aggregate_student_errors(student_id)
    await redis_client.setex(cache_key, 3600, json.dumps(stats))
```

## 测试

运行测试套件：

```bash
# 启动 Neo4j 数据库
docker-compose up neo4j -d

# 运行所有多课程多错误处理测试
pytest tests/test_graph_service.py -k "multi_course" -v

# 运行演示脚本
python demo_multi_course_error.py
```

## 日志记录

所有操作都会记录结构化日志，包括：

- `student_multi_course_error_created`: 创建新错误记录
- `student_error_updated`: 更新现有错误记录
- `error_knowledge_points_associated`: 关联错误类型和知识点
- `student_errors_aggregated`: 聚合学生错误统计
- `cross_course_paths_found`: 查找跨课程路径
- `repeated_error_weight_updated`: 更新重复错误权重

## 错误处理

所有方法都包含完善的错误处理：

- `ValueError`: 节点不存在或参数无效
- `RuntimeError`: 数据库操作失败

建议在调用时使用 try-except 块：

```python
try:
    result = await graph_service.create_student_multi_course_error(...)
except ValueError as e:
    logger.error("Invalid parameters", error=str(e))
except RuntimeError as e:
    logger.error("Database operation failed", error=str(e))
```

## 相关需求

本功能实现了以下需求：

- **需求 4.1**: 一个学生在多个课程中产生错误时，为每个错误创建独立的关系
- **需求 4.2**: 一个错误类型关联多个知识点时，创建到所有相关知识点的关系
- **需求 4.3**: 聚合同一学生的所有错误关系，生成错误分布统计
- **需求 4.4**: 建立不同课程节点通过共同知识点的间接关系
- **需求 4.5**: 学生在同一知识点上重复出错时，增加该错误关系的权重值

## 未来改进

- [ ] 支持错误严重程度的动态调整
- [ ] 添加错误趋势分析（时间序列）
- [ ] 实现错误预测模型
- [ ] 支持错误关联规则挖掘
- [ ] 添加错误解决建议生成
