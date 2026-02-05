# API接口设计

## 1. 设计概述

基于Nest.js框架设计的RESTful API接口，用于支持交互网络可视化系统。接口设计遵循RESTful规范，提供完整的CRUD操作和业务逻辑处理。

## 2. 技术栈

- **框架**：Nest.js
- **语言**：TypeScript
- **ORM**：TypeORM
- **数据库**：MSSQL
- **验证**：Zod

## 3. 目录结构

```
backend/
src/
├── modules/
│   ├── student/
│   │   ├── student.controller.ts
│   │   ├── student.service.ts
│   │   ├── student.entity.ts
│   │   ├── student.module.ts
│   │   └── student.dto.ts
│   ├── teacher/
│   ├── knowledge/
│   ├── interaction/
│   ├── teacher-observation/
│   └── data-migration/
├── shared/
│   ├── config/
│   ├── utils/
│   └── decorators/
└── main.ts
```

## 4. 接口设计

### 4.1 学生接口

#### 4.1.1 获取学生列表

- **路径**：`GET /api/students`
- **参数**：
  - `school`：学校名称（可选）
  - `grade`：年级（可选）
  - `classId`：班级（可选）
  - `page`：页码（默认1）
  - `limit`：每页数量（默认10）
- **响应**：
  ```json
  {
    "data": [
      {
        "id": "S001",
        "name": "陆雨欣",
        "gender": "女",
        "school": "湖州市爱山小学教育集团常溪小学",
        "grade": "5年级",
        "classId": "新五年级2班",
        "knowledgeReserve": 5,
        "learningEngagement": 5,
        "cognitiveLoad": 3,
        "learningMotivation": 5,
        "computationalThinking": 4,
        "humanAiTrust": 3,
        "learningMethod": 5,
        "learningAttitude": 5,
        "createdAt": "2026-02-06T10:00:00Z",
        "updatedAt": "2026-02-06T10:00:00Z"
      }
    ],
    "total": 30,
    "page": 1,
    "limit": 10
  }
  ```

#### 4.1.2 获取学生详情

- **路径**：`GET /api/students/:id`
- **响应**：
  ```json
  {
    "id": "S001",
    "name": "陆雨欣",
    "gender": "女",
    "school": "湖州市爱山小学教育集团常溪小学",
    "grade": "5年级",
    "classId": "新五年级2班",
    "knowledgeReserve": 5,
    "learningEngagement": 5,
    "cognitiveLoad": 3,
    "learningMotivation": 5,
    "computationalThinking": 4,
    "humanAiTrust": 3,
    "learningMethod": 5,
    "learningAttitude": 5,
    "createdAt": "2026-02-06T10:00:00Z",
    "updatedAt": "2026-02-06T10:00:00Z"
  }
  ```

#### 4.1.3 创建学生

- **路径**：`POST /api/students`
- **请求体**：
  ```json
  {
    "name": "张三",
    "gender": "男",
    "school": "杭州市文澜实验学校",
    "grade": "4年级",
    "classId": "四年级10班",
    "knowledgeReserve": 4,
    "learningEngagement": 4,
    "cognitiveLoad": 3,
    "learningMotivation": 4,
    "computationalThinking": 3,
    "humanAiTrust": 4,
    "learningMethod": 3,
    "learningAttitude": 4
  }
  ```
- **响应**：
  ```json
  {
    "id": "S002",
    "name": "张三",
    "gender": "男",
    "school": "杭州市文澜实验学校",
    "grade": "4年级",
    "classId": "四年级10班",
    "knowledgeReserve": 4,
    "learningEngagement": 4,
    "cognitiveLoad": 3,
    "learningMotivation": 4,
    "computationalThinking": 3,
    "humanAiTrust": 4,
    "learningMethod": 3,
    "learningAttitude": 4,
    "createdAt": "2026-02-06T10:00:00Z",
    "updatedAt": "2026-02-06T10:00:00Z"
  }
  ```

#### 4.1.4 更新学生

- **路径**：`PUT /api/students/:id`
- **请求体**：
  ```json
  {
    "knowledgeReserve": 5,
    "learningEngagement": 5
  }
  ```
- **响应**：
  ```json
  {
    "id": "S001",
    "name": "陆雨欣",
    "gender": "女",
    "school": "湖州市爱山小学教育集团常溪小学",
    "grade": "5年级",
    "classId": "新五年级2班",
    "knowledgeReserve": 5,
    "learningEngagement": 5,
    "cognitiveLoad": 3,
    "learningMotivation": 5,
    "computationalThinking": 4,
    "humanAiTrust": 3,
    "learningMethod": 5,
    "learningAttitude": 5,
    "createdAt": "2026-02-06T10:00:00Z",
    "updatedAt": "2026-02-06T10:30:00Z"
  }
  ```

#### 4.1.5 删除学生

- **路径**：`DELETE /api/students/:id`
- **响应**：
  ```json
  {
    "message": "学生删除成功"
  }
  ```

### 4.2 教师接口

#### 4.2.1 获取教师列表

- **路径**：`GET /api/teachers`
- **参数**：
  - `school`：学校名称（可选）
  - `subject`：学科（可选）
  - `page`：页码（默认1）
  - `limit`：每页数量（默认10）
- **响应**：
  ```json
  {
    "data": [
      {
        "id": "T001",
        "name": "杨逸",
        "gender": "女",
        "age": 30,
        "school": "浙江小虫科技有限公司",
        "employeeId": "T2024001",
        "title": "高级教师",
        "teachingGrade": "5年级",
        "teachingClass": "新五年级2班",
        "subject": "信息技术",
        "slogan": "因材施教，寓教于乐。",
        "createdAt": "2026-02-06T10:00:00Z",
        "updatedAt": "2026-02-06T10:00:00Z"
      }
    ],
    "total": 5,
    "page": 1,
    "limit": 10
  }
  ```

#### 4.2.2 获取教师详情

- **路径**：`GET /api/teachers/:id`
- **响应**：
  ```json
  {
    "id": "T001",
    "name": "杨逸",
    "gender": "女",
    "age": 30,
    "school": "浙江小虫科技有限公司",
    "employeeId": "T2024001",
    "title": "高级教师",
    "teachingGrade": "5年级",
    "teachingClass": "新五年级2班",
    "subject": "信息技术",
    "slogan": "因材施教，寓教于乐。",
    "createdAt": "2026-02-06T10:00:00Z",
    "updatedAt": "2026-02-06T10:00:00Z"
  }
  ```

### 4.3 知识点接口

#### 4.3.1 获取知识点列表

- **路径**：`GET /api/knowledge`
- **参数**：
  - `category`：分类（可选）
  - `page`：页码（默认1）
  - `limit`：每页数量（默认10）
- **响应**：
  ```json
  {
    "data": [
      {
        "id": "K001",
        "name": "插入图片",
        "content": "将光标定位到要插入图片的位置，点击\"插入\"选项卡，点击\"图片\"按钮，选择本地图片上传。",
        "category": "Word操作",
        "createdAt": "2026-02-06T10:00:00Z",
        "updatedAt": "2026-02-06T10:00:00Z"
      }
    ],
    "total": 10,
    "page": 1,
    "limit": 10
  }
  ```

### 4.4 交互接口

#### 4.4.1 获取交互列表

- **路径**：`GET /api/interactions`
- **参数**：
  - `sourceId`：源节点ID（可选）
  - `targetId`：目标节点ID（可选）
  - `sourceType`：源节点类型（可选）
  - `targetType`：目标节点类型（可选）
  - `type`：交互类型（可选）
- **响应**：
  ```json
  {
    "data": [
      {
        "id": "I001",
        "sourceId": "S001",
        "targetId": "S002",
        "sourceType": "STUDENT",
        "targetType": "STUDENT",
        "value": 1,
        "type": "PLATFORM",
        "interactionType": "like",
        "createdAt": "2026-02-06T10:00:00Z",
        "updatedAt": "2026-02-06T10:00:00Z"
      }
    ]
  }
  ```

#### 4.4.2 创建交互

- **路径**：`POST /api/interactions`
- **请求体**：
  ```json
  {
    "sourceId": "S001",
    "targetId": "K001",
    "sourceType": "STUDENT",
    "targetType": "KNOWLEDGE",
    "value": 1.5,
    "type": "PLATFORM"
  }
  ```
- **响应**：
  ```json
  {
    "id": "I002",
    "sourceId": "S001",
    "targetId": "K001",
    "sourceType": "STUDENT",
    "targetType": "KNOWLEDGE",
    "value": 1.5,
    "type": "PLATFORM",
    "createdAt": "2026-02-06T10:00:00Z",
    "updatedAt": "2026-02-06T10:00:00Z"
  }
  ```

### 4.5 教师观察数据接口

#### 4.5.1 获取教师观察数据列表

- **路径**：`GET /api/teacher-observations`
- **参数**：
  - `school`：学校名称（可选）
  - `grade`：年级（可选）
  - `class`：班级（可选）
  - `page`：页码（默认1）
  - `limit`：每页数量（默认10）
- **响应**：
  ```json
  {
    "data": [
      {
        "id": "TO001",
        "teacherId": "T001",
        "name": "杨逸",
        "school": "浙江小虫科技有限公司",
        "grades": [5],
        "class": 2,
        "createdAt": "2026-02-06T10:00:00Z",
        "updatedAt": "2026-02-06T10:00:00Z"
      }
    ],
    "total": 5,
    "page": 1,
    "limit": 10
  }
  ```

#### 4.5.2 获取教师观察数据详情

- **路径**：`GET /api/teacher-observations/:id`
- **响应**：
  ```json
  {
    "id": "TO001",
    "teacherId": "T001",
    "name": "杨逸",
    "school": "浙江小虫科技有限公司",
    "grades": [5],
    "class": 2,
    "createdAt": "2026-02-06T10:00:00Z",
    "updatedAt": "2026-02-06T10:00:00Z"
  }
  ```

#### 4.5.3 创建教师观察数据

- **路径**：`POST /api/teacher-observations`
- **请求体**：
  ```json
  {
    "teacherId": "T001",
    "name": "杨逸",
    "school": "浙江小虫科技有限公司",
    "grades": [5],
    "class": 2
  }
  ```
- **响应**：
  ```json
  {
    "id": "TO002",
    "teacherId": "T001",
    "name": "杨逸",
    "school": "浙江小虫科技有限公司",
    "grades": [5],
    "class": 2,
    "createdAt": "2026-02-06T10:00:00Z",
    "updatedAt": "2026-02-06T10:00:00Z"
  }
  ```

#### 4.5.4 更新教师观察数据

- **路径**：`PUT /api/teacher-observations/:id`
- **请求体**：
  ```json
  {
    "grades": [5, 6],
    "class": 3
  }
  ```
- **响应**：
  ```json
  {
    "id": "TO001",
    "teacherId": "T001",
    "name": "杨逸",
    "school": "浙江小虫科技有限公司",
    "grades": [5, 6],
    "class": 3,
    "createdAt": "2026-02-06T10:00:00Z",
    "updatedAt": "2026-02-06T10:30:00Z"
  }
  ```

#### 4.5.5 删除教师观察数据

- **路径**：`DELETE /api/teacher-observations/:id`
- **响应**：
  ```json
  {
    "message": "教师观察数据删除成功"
  }
  ```

### 4.7 数据迁移接口

#### 4.7.1 导入Excel数据

- **路径**：`POST /api/data-migration/import`
- **请求体**：
  ```json
  {
    "fileType": "survey",
    "fileUrl": "https://example.com/survey.xls"
  }
  ```
- **响应**：
  ```json
  {
    "message": "数据导入成功",
    "importedCount": 100,
    "updatedCount": 20,
    "errors": []
  }
  ```

### 4.8 AI分析接口

#### 4.8.1 分析网络

- **路径**：`POST /api/ai/analyze-network`
- **请求体**：
  ```json
  {
    "scenario": "COLLABORATIVE",
    "studentCount": 30,
    "teacherCount": 2,
    "avgAccuracy": 85
  }
  ```
- **响应**：
  ```json
  {
    "analysis": "当前网络显示学生之间的协作互动频繁，教师在网络中起到了良好的引导作用。建议加强知识点与学生之间的连接，提高学习资源的利用率。"
  }
  ```

#### 4.8.2 推断属性

- **路径**：`POST /api/ai/infer-attributes`
- **请求体**：
  ```json
  {
    "nodeId": "S001",
    "nodeType": "STUDENT",
    "observations": [
      {
        "attribute": "knowledgeReserve",
        "value": 4,
        "confidence": 0.8
      }
    ]
  }
  ```
- **响应**：
  ```json
  {
    "inferredAttributes": [
      {
        "attribute": "learningEngagement",
        "value": 4.5,
        "confidence": 0.85
      },
      {
        "attribute": "computationalThinking",
        "value": 4,
        "confidence": 0.8
      }
    ]
  }
  ```

## 5. 错误处理

### 5.1 标准错误响应

```json
{
  "statusCode": 404,
  "message": "学生不存在",
  "error": "Not Found"
}
```

### 5.2 错误代码

| 状态码 | 描述 |
|-------|------|
| 400 | 请求参数错误 |
| 401 | 未授权 |
| 403 | 禁止访问 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

## 6. 数据验证

使用Zod进行请求数据验证：

```typescript
// student.dto.ts
import { z } from 'zod';

export const createStudentSchema = z.object({
  name: z.string().min(1, '姓名不能为空'),
  gender: z.enum(['男', '女'], { required_error: '性别必须是男或女' }),
  school: z.string().min(1, '学校名称不能为空'),
  grade: z.string().min(1, '年级不能为空'),
  classId: z.string().min(1, '班级不能为空'),
  knowledgeReserve: z.number().min(1).max(5),
  learningEngagement: z.number().min(1).max(5),
  cognitiveLoad: z.number().min(1).max(5),
  learningMotivation: z.number().min(1).max(5),
  computationalThinking: z.number().min(1).max(5),
  humanAiTrust: z.number().min(1).max(5),
  learningMethod: z.number().min(1).max(5),
  learningAttitude: z.number().min(1).max(5),
});

export type CreateStudentDto = z.infer<typeof createStudentSchema>;
```

## 7. 安全设计

1. **CORS配置**：
   ```typescript
   // main.ts
   app.enableCors({
     origin: '*',
     methods: 'GET,HEAD,PUT,PATCH,POST,DELETE',
     credentials: true,
   });
   ```

2. **请求验证**：
   - 使用Zod验证所有请求数据
   - 防止SQL注入和XSS攻击

3. **日志记录**：
   - 记录所有API请求和响应
   - 记录错误和异常

## 8. 性能优化

1. **缓存策略**：
   - 使用Redis缓存频繁查询的数据
   - 缓存AI分析结果

2. **数据库优化**：
   - 使用索引加速查询
   - 实现数据库连接池
   - 优化复杂查询

3. **异步处理**：
   - 使用异步函数处理IO操作
   - 实现队列处理大量数据导入

## 9. 部署策略

1. **环境变量**：
   ```env
   # .env
   DATABASE_HOST=rm-bp10v29fkj305q3smfo.sqlserver.rds.aliyuncs.com
   DATABASE_PORT=3433
   DATABASE_USERNAME=coding_data
   DATABASE_PASSWORD=root
   DATABASE_NAME=interaction_network_db
   
   AI_API_KEY=your_aliyun_ai_key
   ```

2. **容器化**：
   - 使用Docker容器化部署
   - 提供Dockerfile和docker-compose.yml

3. **CI/CD**：
   - 实现GitHub Actions CI/CD pipeline
   - 自动测试和部署

## 10. 总结

本API设计基于RESTful规范和Nest.js框架最佳实践，提供了完整的接口集来支持交互网络可视化系统的所有功能。接口设计考虑了性能、安全性和可扩展性，确保系统能够高效、安全地运行。