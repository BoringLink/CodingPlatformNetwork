# 分析报告服务 API 参考

## 快速开始

```python
from app.services import report_service, ReportFormat

# 生成完整报告
report = await report_service.generate_report()

# 导出为 JSON
json_bytes = await report_service.export_report(report, ReportFormat.JSON)
```

## API 方法

### 1. generate_graph_statistics()

生成图谱统计信息。

**返回**: `GraphStatistics`

**示例**:
```python
stats = await report_service.generate_graph_statistics()
print(f"节点总数: {stats.total_nodes}")
print(f"学生节点数: {stats.node_type_distribution['Student']}")
```

**返回字段**:
- `total_nodes` (int): 节点总数
- `node_type_distribution` (dict): 节点类型分布
- `total_relationships` (int): 关系总数
- `relationship_type_distribution` (dict): 关系类型分布
- `timestamp` (datetime): 统计时间

---

### 2. analyze_student_performance(top_n=10)

分析学生表现，识别高频错误和需要关注的学生。

**参数**:
- `top_n` (int, 可选): 返回前 N 个结果，默认 10

**返回**: `StudentPerformanceAnalysis`

**示例**:
```python
analysis = await report_service.analyze_student_performance(top_n=5)

# 高频错误
for error in analysis.high_frequency_errors:
    print(f"{error['knowledge_point_name']}: {error['total_occurrences']} 次")

# 需要关注的学生
for student in analysis.students_needing_attention:
    print(f"{student['student_name']}: {student['total_errors']} 个错误")
```

**返回字段**:
- `high_frequency_errors` (list): 高频错误列表
  - `knowledge_point_id`: 知识点 ID
  - `knowledge_point_name`: 知识点名称
  - `error_type_id`: 错误类型 ID
  - `error_type_name`: 错误类型名称
  - `total_occurrences`: 总发生次数
  - `student_count`: 涉及学生数
- `students_needing_attention` (list): 需要关注的学生列表
  - `student_id`: 学生 ID
  - `student_name`: 学生姓名
  - `total_errors`: 总错误数
  - `error_types_count`: 错误类型数
- `error_distribution` (dict): 错误分布统计

---

### 3. analyze_course_effectiveness()

分析课程效果，计算参与度和错误率。

**返回**: `CourseEffectivenessAnalysis`

**示例**:
```python
analysis = await report_service.analyze_course_effectiveness()

for course in analysis.course_metrics:
    print(f"{course['course_name']}:")
    print(f"  参与人数: {course['participation']}")
    print(f"  错误率: {course['error_rate']:.2%}")
```

**返回字段**:
- `course_metrics` (list): 课程指标列表
  - `course_id`: 课程 ID
  - `course_name`: 课程名称
  - `participation`: 参与人数
  - `students_with_errors`: 有错误的学生数
  - `total_errors`: 总错误数
  - `error_rate`: 错误率（0.0-1.0）

---

### 4. analyze_interaction_patterns(min_network_size=3)

分析互动模式，识别社交网络和孤立学生。

**参数**:
- `min_network_size` (int, 可选): 最小网络规模，默认 3

**返回**: `InteractionPatternAnalysis`

**示例**:
```python
analysis = await report_service.analyze_interaction_patterns(min_network_size=2)

# 社交网络
for network in analysis.social_networks:
    print(f"{network['student_name']}: {network['connection_count']} 个连接")

# 孤立学生
print(f"孤立学生数: {len(analysis.isolated_students)}")

# 互动统计
stats = analysis.interaction_statistics
print(f"互动率: {stats['interaction_rate']:.2%}")
```

**返回字段**:
- `social_networks` (list): 社交网络列表
  - `student_id`: 学生 ID
  - `student_name`: 学生姓名
  - `connection_count`: 连接数
  - `connected_students`: 连接的学生 ID 列表
- `isolated_students` (list): 孤立学生列表
  - `student_id`: 学生 ID
  - `student_name`: 学生姓名
  - `grade`: 年级
- `interaction_statistics` (dict): 互动统计
  - `total_students`: 总学生数
  - `students_with_interactions`: 有互动的学生数
  - `total_interactions`: 总互动数
  - `interaction_rate`: 互动率（0.0-1.0）

---

### 5. generate_report(...)

生成完整的分析报告。

**参数**:
- `include_graph_stats` (bool, 可选): 是否包含图谱统计，默认 True
- `include_student_performance` (bool, 可选): 是否包含学生表现分析，默认 True
- `include_course_effectiveness` (bool, 可选): 是否包含课程效果分析，默认 True
- `include_interaction_patterns` (bool, 可选): 是否包含互动模式分析，默认 True

**返回**: `AnalysisReport`

**示例**:
```python
# 完整报告
report = await report_service.generate_report()

# 部分报告
report = await report_service.generate_report(
    include_graph_stats=True,
    include_student_performance=True,
    include_course_effectiveness=False,
    include_interaction_patterns=False,
)

# 访问报告内容
print(f"节点总数: {report.graph_statistics.total_nodes}")
print(f"高频错误数: {len(report.student_performance.high_frequency_errors)}")
```

**返回字段**:
- `graph_statistics` (GraphStatistics): 图谱统计
- `student_performance` (StudentPerformanceAnalysis): 学生表现分析
- `course_effectiveness` (CourseEffectivenessAnalysis): 课程效果分析
- `interaction_patterns` (InteractionPatternAnalysis): 互动模式分析
- `generated_at` (datetime): 报告生成时间

---

### 6. export_report(report, format)

导出报告为指定格式。

**参数**:
- `report` (AnalysisReport): 分析报告对象
- `format` (str): 导出格式，可选值：
  - `ReportFormat.JSON` 或 `"json"`: JSON 格式
  - `ReportFormat.PDF` 或 `"pdf"`: PDF 格式

**返回**: `bytes` - 报告内容（字节）

**示例**:
```python
report = await report_service.generate_report()

# 导出为 JSON
json_bytes = await report_service.export_report(report, ReportFormat.JSON)
with open("report.json", "wb") as f:
    f.write(json_bytes)

# 导出为 PDF（需要安装 reportlab）
try:
    pdf_bytes = await report_service.export_report(report, ReportFormat.PDF)
    with open("report.pdf", "wb") as f:
        f.write(pdf_bytes)
except RuntimeError as e:
    print(f"PDF 导出失败: {e}")
```

**注意**:
- JSON 格式总是可用
- PDF 格式需要安装 `reportlab` 库：`pip install reportlab`

---

## 报告对象方法

### AnalysisReport.to_dict()

将报告转换为字典。

**返回**: `dict`

**示例**:
```python
report = await report_service.generate_report()
report_dict = report.to_dict()
```

---

### AnalysisReport.to_json()

将报告转换为 JSON 字符串。

**返回**: `str`

**示例**:
```python
report = await report_service.generate_report()
json_str = report.to_json()
print(json_str)
```

---

## 错误处理

所有方法都可能抛出以下异常：

- `RuntimeError`: 数据库操作失败或报告生成失败
- `ValueError`: 参数验证失败

**示例**:
```python
try:
    report = await report_service.generate_report()
except RuntimeError as e:
    print(f"报告生成失败: {e}")
except ValueError as e:
    print(f"参数错误: {e}")
```

---

## 完整示例

```python
import asyncio
from app.database import init_database, close_database
from app.services import report_service, ReportFormat


async def main():
    # 初始化数据库
    await init_database()
    
    try:
        # 1. 生成图谱统计
        stats = await report_service.generate_graph_statistics()
        print(f"节点总数: {stats.total_nodes}")
        
        # 2. 分析学生表现
        performance = await report_service.analyze_student_performance(top_n=5)
        print(f"高频错误数: {len(performance.high_frequency_errors)}")
        
        # 3. 分析课程效果
        effectiveness = await report_service.analyze_course_effectiveness()
        print(f"课程数: {len(effectiveness.course_metrics)}")
        
        # 4. 分析互动模式
        patterns = await report_service.analyze_interaction_patterns()
        print(f"孤立学生数: {len(patterns.isolated_students)}")
        
        # 5. 生成完整报告
        report = await report_service.generate_report()
        
        # 6. 导出报告
        json_bytes = await report_service.export_report(report, ReportFormat.JSON)
        with open("report.json", "wb") as f:
            f.write(json_bytes)
        print("报告已导出到 report.json")
        
    finally:
        # 关闭数据库连接
        await close_database()


if __name__ == "__main__":
    asyncio.run(main())
```

---

## 性能提示

1. **批量查询**: 所有分析方法都使用优化的 Cypher 查询，一次性获取所需数据
2. **结果限制**: 使用 `top_n` 参数限制返回结果数量，提高性能
3. **部分报告**: 只生成需要的分析部分，避免不必要的计算
4. **缓存**: 对于频繁查询的统计数据，考虑添加缓存层

---

## 常见问题

### Q: PDF 导出失败怎么办？

A: 确保已安装 reportlab 库：
```bash
pip install reportlab
```

### Q: 如何自定义报告内容？

A: 使用 `generate_report()` 的参数选择需要的分析部分：
```python
report = await report_service.generate_report(
    include_graph_stats=True,
    include_student_performance=True,
    include_course_effectiveness=False,
    include_interaction_patterns=False,
)
```

### Q: 如何处理大规模数据？

A: 
1. 使用 `top_n` 参数限制结果数量
2. 考虑添加日期范围过滤
3. 使用分页查询
4. 添加缓存层

### Q: 报告生成需要多长时间？

A: 取决于图谱规模：
- 小规模（< 1000 节点）: < 1 秒
- 中规模（1000-10000 节点）: 1-5 秒
- 大规模（> 10000 节点）: 5-30 秒

---

## 相关文档

- [实现总结](REPORT_SERVICE_IMPLEMENTATION.md)
- [演示脚本](demo_report_service.py)
- [测试用例](tests/test_report_service.py)
