# API接口设计

## 1. 设计概述

基于Nest.js框架设计的RESTful API接口，用于支持交互网络可视化系统。接口设计遵循RESTful规范，提供完整的CRUD操作和业务逻辑处理。

## 1.1 节点类型规范

网络可视化系统仅包含以下三种类型的节点：

| 节点类型 | 类型标识 | 描述 |
|---------|---------|------|
| 学生 | STUDENT | 系统中的学生用户 |
| 教师 | TEACHER | 系统中的教师用户 |
| 知识点 | KNOWLEDGE | 系统中的知识点内容 |

**注意**：系统严格限制节点类型，不允许其他类型的节点混入网络中。所有API接口在处理节点类型时，必须验证类型值是否符合上述规范。

## 1.2 教师观察数据说明

**设计决策**：删除了教师观察数据（TeacherObservation）实体及其相关接口。

**删除原因**：
- 经评估，教师观察数据在当前系统中没有明确的业务用途
- 该实体与核心网络可视化功能无直接关联
- 删除后可简化系统架构，减少不必要的复杂性
- 教师的教学班级信息已通过教师-班级关联表（teacher_class_mappings）进行管理

## 2. 技术栈

- **框架**：Nest.js
- **语言**：TypeScript
- **ORM**：Prisma (v7.0+)
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
│   │   ├── student.module.ts
│   │   └── student.dto.ts
│   ├── teacher/
│   ├── knowledge/
│   ├── interaction/
│   ├── teacher-observation/
│   └── data-migration/
├── prisma/
│   └── schema.prisma
├── shared/
│   ├── config/
│   ├── utils/
│   └── decorators/
└── main.ts
```

## 3.1 Prisma 数据模型定义

使用Prisma Schema定义数据模型，替代传统的TypeORM实体类：

```prisma
// prisma/schema.prisma
generator client {
  provider = "prisma-client-js"
}

datasource db {
  provider = "sqlserver"
  url      = env("DATABASE_URL")
}

model Student {
  id                  String   @id @default(cuid())
  name                String
  gender              String
  school              String
  grade               String
  classId             String
  knowledgeReserve    Float
  learningEngagement  Float
  cognitiveLoad       Float
  learningMotivation  Float
  computationalThinking Float
  humanAiTrust        Float
  learningMethod      Float
  learningAttitude    Float
  createdAt           DateTime @default(now())
  updatedAt           DateTime @updatedAt

  @@map("students")
}

model Teacher {
  id            String   @id @default(cuid())
  name          String
  school        String
  teachingGrade String
  teachingClass String
  createdAt     DateTime @default(now())
  updatedAt     DateTime @updatedAt

  @@map("teachers")
}

model TeacherClassMapping {
  id        String   @id @default(cuid())
  teacherId String
  grade     String
  classId   String
  createdAt DateTime @default(now())
  updatedAt DateTime @updatedAt

  @@map("teacher_class_mappings")
}

model Knowledge {
  id                    String   @id @default(cuid())
  content               String
  knowledgePoint        String
  grade                 String
  type                  String
  parentId              String?
  parentName            String?
  relatedKnowledgeIds   String[]?
  relatedKnowledgeNames String[]?
  createdAt             DateTime @default(now())
  updatedAt             DateTime @updatedAt

  @@map("knowledge_points")
}

model Interaction {
  id            String   @id @default(cuid())
  sourceId      String
  targetId      String
  sourceType    String
  targetType    String
  value         Float
  type          String
  interactionType String?
  createdAt     DateTime @default(now())
  updatedAt     DateTime @updatedAt

  @@map("interactions")
}


```

## 4. 接口设计

### 4.1 学生接口

#### 4.1.1 获取学生列表

- **路径**：`GET /api/v1/students`
- **参数**：
  - `school`：学校名称（可选）
  - `grade`：年级（可选）
  - `class-id`：班级（可选）
- **响应**：
  ```json
  [
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
  ]
  ```

#### 4.1.2 获取学生详情

- **路径**：`GET /api/v1/students/:id`
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

- **路径**：`POST /api/v1/students`
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

- **路径**：`PUT /api/v1/students/:id`
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

- **路径**：`DELETE /api/v1/students/:id`
- **响应**：
  ```json
  {
    "message": "学生删除成功"
  }
  ```

### 4.2 教师接口

#### 4.2.1 获取教师列表

- **路径**：`GET /api/v1/teachers`
- **参数**：
  - `school`：学校名称（可选）
- **响应**：
  ```json
  [
    {
      "id": "T001",
      "name": "杨逸",
      "school": "浙江小虫科技有限公司",
      "teachingGrade": "5年级",
      "teachingClass": "2班",
      "createdAt": "2026-02-06T10:00:00Z",
      "updatedAt": "2026-02-06T10:00:00Z"
    }
  ]
  ```

#### 4.2.2 获取教师详情

- **路径**：`GET /api/v1/teachers/:id`
- **响应**：
  ```json
  {
    "id": "T001",
    "name": "杨逸",
    "school": "浙江小虫科技有限公司",
    "teachingGrade": "5年级",
    "teachingClass": "2班",
    "createdAt": "2026-02-06T10:00:00Z",
    "updatedAt": "2026-02-06T10:00:00Z"
  }
  ```

#### 4.2.3 创建教师

- **路径**：`POST /api/v1/teachers`
- **请求体**：
  ```json
  {
    "name": "张三",
    "school": "杭州市文澜实验学校",
    "teachingGrade": "4年级",
    "teachingClass": "1班"
  }
  ```
- **响应**：
  ```json
  {
    "id": "T002",
    "name": "张三",
    "school": "杭州市文澜实验学校",
    "teachingGrade": "4年级",
    "teachingClass": "1班",
    "createdAt": "2026-02-06T10:00:00Z",
    "updatedAt": "2026-02-06T10:00:00Z"
  }
  ```

#### 4.2.4 更新教师

- **路径**：`PUT /api/v1/teachers/:id`
- **请求体**：
  ```json
  {
    "name": "李四",
    "school": "杭州市文澜实验学校",
    "teachingGrade": "4年级",
    "teachingClass": "1班"
  }
  ```
- **响应**：
  ```json
  {
    "id": "T001",
    "name": "李四",
    "school": "杭州市文澜实验学校",
    "teachingGrade": "4年级",
    "teachingClass": "1班",
    "createdAt": "2026-02-06T10:00:00Z",
    "updatedAt": "2026-02-06T10:30:00Z"
  }
  ```

#### 4.2.5 删除教师

- **路径**：`DELETE /api/v1/teachers/:id`
- **响应**：
  ```json
  {
    "message": "教师删除成功"
  }
  ```

### 4.3 教师-班级关联接口

#### 4.3.1 获取教师的班级关联

- **路径**：`GET /api/v1/teacher-class-mappings`
- **参数**：
  - `teacher-id`：教师ID（可选）
  - `grade`：年级（可选）
  - `class-id`：班级（可选）
- **响应**：
  ```json
  {
    "data": [
      {
        "id": "TC001",
        "teacherId": "T001",
        "grade": "5年级",
        "classId": "新五年级2班",
        "createdAt": "2026-02-06T10:00:00Z",
        "updatedAt": "2026-02-06T10:00:00Z"
      }
    ]
  }
  ```

#### 4.3.2 创建教师-班级关联

- **路径**：`POST /api/v1/teacher-class-mappings`
- **请求体**：
  ```json
  {
    "teacherId": "T001",
    "grade": "5年级",
    "classId": "新五年级2班"
  }
  ```
- **响应**：
  ```json
  {
    "id": "TC002",
    "teacherId": "T001",
    "grade": "5年级",
    "classId": "新五年级2班",
    "createdAt": "2026-02-06T10:00:00Z",
    "updatedAt": "2026-02-06T10:00:00Z"
  }
  ```

#### 4.3.3 删除教师-班级关联

- **路径**：`DELETE /api/v1/teacher-class-mappings/:id`
- **响应**：
  ```json
  {
    "message": "教师-班级关联删除成功"
  }
  ```

### 4.4 知识点接口

#### 4.4.1 获取知识点列表

- **路径**：`GET /api/v1/knowledge-points`
- **参数**：
  - `grade`：年级（可选）
  - `type`：知识点类型（可选）
  - `parent-id`：上级知识点ID（可选）
- **响应**：
  ```json
  [
    {
      "id": "K001",
      "content": "将光标定位到要插入图片的位置，点击\"插入\"选项卡，点击\"图片\"按钮，选择本地图片上传。",
      "knowledgePoint": "insert_image",
      "grade": "5年级",
      "type": "知识点",
      "parentId": "K002",
      "parentName": "Word操作基础",
      "relatedKnowledgeIds": ["K003", "K004"],
      "relatedKnowledgeNames": ["设置字体", "设置段落"],
      "createdAt": "2026-02-06T10:00:00Z",
      "updatedAt": "2026-02-06T10:00:00Z"
    }
  ]
  ```

#### 4.4.2 获取知识点详情

- **路径**：`GET /api/v1/knowledge-points/:id`
- **响应**：
  ```json
  {
    "id": "K001",
    "content": "将光标定位到要插入图片的位置，点击\"插入\"选项卡，点击\"图片\"按钮，选择本地图片上传。",
    "knowledgePoint": "insert_image",
    "grade": "5年级",
    "type": "知识点",
    "parentId": "K002",
    "parentName": "Word操作基础",
    "relatedKnowledgeIds": ["K003", "K004"],
    "relatedKnowledgeNames": ["设置字体", "设置段落"],
    "createdAt": "2026-02-06T10:00:00Z",
    "updatedAt": "2026-02-06T10:00:00Z"
  }
  ```

#### 4.4.3 创建知识点

- **路径**：`POST /api/v1/knowledge-points`
- **请求体**：
  ```json
  {
    "content": "设置文档页面大小为A4，页边距为上下2.54cm，左右3.17cm。",
    "knowledgePoint": "page_setup",
    "grade": "5年级",
    "category": "Word操作",
    "type": "知识点",
    "parentId": "K002",
    "parentName": "Word操作基础",
    "relatedKnowledgeIds": ["K003", "K004"],
    "relatedKnowledgeNames": ["设置字体", "设置段落"]
  }
  ```
- **响应**：
  ```json
  {
    "id": "K002",
    "content": "设置文档页面大小为A4，页边距为上下2.54cm，左右3.17cm。",
    "knowledgePoint": "page_setup",
    "grade": "5年级",
    "category": "Word操作",
    "type": "知识点",
    "parentId": "K002",
    "parentName": "Word操作基础",
    "relatedKnowledgeIds": ["K003", "K004"],
    "relatedKnowledgeNames": ["设置字体", "设置段落"],
    "createdAt": "2026-02-06T10:00:00Z",
    "updatedAt": "2026-02-06T10:00:00Z"
  }
  ```

#### 4.4.4 更新知识点

- **路径**：`PUT /api/v1/knowledge-points/:id`
- **请求体**：
  ```json
  {
    "content": "设置文档页面大小为A4，页边距为上下2.54cm，左右3.17cm。可通过\"页面布局\"选项卡进行设置。",
    "knowledgePoint": "page_setup",
    "grade": "5年级",
    "type": "知识点",
    "parentId": "K002",
    "parentName": "Word操作基础",
    "relatedKnowledgeIds": ["K003", "K004"],
    "relatedKnowledgeNames": ["设置字体", "设置段落"]
  }
  ```
- **响应**：
  ```json
  {
    "id": "K001",
    "content": "设置文档页面大小为A4，页边距为上下2.54cm，左右3.17cm。可通过\"页面布局\"选项卡进行设置。",
    "knowledgePoint": "page_setup",
    "grade": "5年级",
    "type": "知识点",
    "parentId": "K002",
    "parentName": "Word操作基础",
    "relatedKnowledgeIds": ["K003", "K004"],
    "relatedKnowledgeNames": ["设置字体", "设置段落"],
    "createdAt": "2026-02-06T10:00:00Z",
    "updatedAt": "2026-02-06T10:30:00Z"
  }
  ```

#### 4.4.5 删除知识点

- **路径**：`DELETE /api/v1/knowledge-points/:id`
- **响应**：
  ```json
  {
    "message": "知识点删除成功"
  }
  ```

### 4.5 交互接口

#### 4.5.1 获取交互列表

- **路径**：`GET /api/v1/interactions`
- **参数**：
  - `source-id`：源节点ID（可选）
  - `target-id`：目标节点ID（可选）
  - `source-type`：源节点类型（可选）
  - `target-type`：目标节点类型（可选）
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

#### 4.5.2 创建交互

- **路径**：`POST /api/v1/interactions`
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

### 4.6 数据迁移接口

#### 4.6.1 导入Excel数据

- **路径**：`POST /api/v1/data-migration/import`
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

### 4.7 AI分析接口

#### 4.7.1 分析网络

- **路径**：`POST /api/v1/ai/analyze-network`
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

#### 4.7.2 推断属性

- **路径**：`POST /api/v1/ai/infer-attributes`
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

### 4.8 图谱数据接口

#### 4.8.1 获取完整图谱数据

- **路径**：`GET /api/v1/graph-data`
- **参数**：
  - `scenario`：场景类型（可选）
  - `school`：学校名称（可选）
  - `grade`：年级（可选）
  - `class-id`：班级（可选）
- **响应**：
  ```json
  {
    "nodes": [
      {
        "id": "S001",
        "type": "STUDENT",
        "name": "陆雨欣",
        "group": 3,
        "val": 8,
        "studentProfile": {
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
          "learningAttitude": 5
        }
      },
      {
        "id": "T001",
        "type": "TEACHER",
        "name": "教师 A",
        "group": 1,
        "val": 25,
        "teacherProfile": {
          "school": "湖州市爱山小学教育集团常溪小学",
          "teachingGrade": "5年级",
          "teachingClass": "新五年级2班"
        }
      },
      {
        "id": "K001",
        "type": "KNOWLEDGE",
        "name": "插入图片",
        "group": 2,
        "val": 15,
        "knowledgeProfile": {
          "content": "将光标定位到要插入图片的位置，点击\"插入\"选项卡，点击\"图片\"按钮，选择本地图片上传。",
          "type": "知识点",
          "parentId": "K002",
          "parentName": "Word操作基础",
          "relatedKnowledgeIds": ["K003", "K004"],
          "relatedKnowledgeNames": ["设置字体", "设置段落"]
        }
      }
    ],
    "links": [
      {
        "source": "S001",
        "target": "T001",
        "value": 2,
        "type": "PHYSICAL"
      },
      {
        "source": "S001",
        "target": "K001",
        "value": 1.5,
        "type": "PLATFORM"
      }
    ]
  }
  ```

## 5. Prisma 客户端使用示例

在Service层使用Prisma客户端进行数据库操作：

```typescript
// student.service.ts
import { Injectable } from '@nestjs/common';
import { PrismaClient } from '@prisma/client';
import { CreateStudentDto } from './student.dto';

@Injectable()
export class StudentService {
  private prisma = new PrismaClient();

  async findAll(params: {
    school?: string;
    grade?: string;
    classId?: string;
  }) {
    const {
      school,
      grade,
      classId,
    } = params;

    const where = {
      ...(school && { school }),
      ...(grade && { grade }),
      ...(classId && { classId }),
    };

    return this.prisma.student.findMany({
      where,
      orderBy: { createdAt: 'desc' },
    });
  }

  async findOne(id: string) {
    return this.prisma.student.findUnique({ where: { id } });
  }

  async create(data: CreateStudentDto) {
    return this.prisma.student.create({ data });
  }

  async update(id: string, data: Partial<CreateStudentDto>) {
    return this.prisma.student.update({
      where: { id },
      data,
    });
  }

  async delete(id: string) {
    await this.prisma.student.delete({ where: { id } });
    return { message: '学生删除成功' };
  }
}
```

```typescript
// teacher.service.ts
import { Injectable } from '@nestjs/common';
import { PrismaClient } from '@prisma/client';
import { CreateTeacherDto } from './teacher.dto';

@Injectable()
export class TeacherService {
  private prisma = new PrismaClient();

  async findAll(params: {
    school?: string;
  }) {
    const {
      school,
    } = params;

    const where = {
      ...(school && { school }),
    };

    return this.prisma.teacher.findMany({
      where,
      orderBy: { createdAt: 'desc' },
    });
  }

  async findOne(id: string) {
    return this.prisma.teacher.findUnique({ where: { id } });
  }

  async create(data: CreateTeacherDto) {
    return this.prisma.teacher.create({ data });
  }

  async update(id: string, data: Partial<CreateTeacherDto>) {
    return this.prisma.teacher.update({
      where: { id },
      data,
    });
  }

  async delete(id: string) {
    await this.prisma.teacher.delete({ where: { id } });
    return { message: '教师删除成功' };
  }
}
```

```typescript
// knowledge.service.ts
import { Injectable } from '@nestjs/common';
import { PrismaClient } from '@prisma/client';
import { CreateKnowledgeDto } from './knowledge.dto';

@Injectable()
export class KnowledgeService {
  private prisma = new PrismaClient();

  async findAll(params: {
    grade?: string;
    type?: string;
    parentId?: string;
  }) {
    const {
      grade,
      type,
      parentId,
    } = params;

    const where = {
      ...(grade && { grade }),
      ...(type && { type }),
      ...(parentId && { parentId }),
    };

    return this.prisma.knowledge.findMany({
      where,
      orderBy: { createdAt: 'desc' },
    });
  }

  async findOne(id: string) {
    return this.prisma.knowledge.findUnique({ where: { id } });
  }

  async create(data: CreateKnowledgeDto) {
    return this.prisma.knowledge.create({ data });
  }

  async update(id: string, data: Partial<CreateKnowledgeDto>) {
    return this.prisma.knowledge.update({
      where: { id },
      data,
    });
  }

  async delete(id: string) {
    await this.prisma.knowledge.delete({ where: { id } });
    return { message: '知识点删除成功' };
  }
}
```

```typescript
// graph.service.ts
import { Injectable } from '@nestjs/common';
import { PrismaClient } from '@prisma/client';
import { GraphData } from '../types';

@Injectable()
export class GraphService {
  private prisma = new PrismaClient();

  async getGraphData(params: {
    scenario?: string;
    school?: string;
    grade?: string;
    classId?: string;
  }) {
    const {
      school,
      grade,
      classId,
    } = params;

    // 构建学生查询条件
    const studentWhere = {
      ...(school && { school }),
      ...(grade && { grade }),
      ...(classId && { classId }),
    };

    // 构建教师查询条件
    const teacherWhere = {
      ...(school && { school }),
    };

    // 构建知识点查询条件
    const knowledgeWhere = {
      ...(grade && { grade }),
    };

    // 并行查询所有数据
    const [students, teachers, knowledge, interactions] = await Promise.all([
      this.prisma.student.findMany({ where: studentWhere }),
      this.prisma.teacher.findMany({ where: teacherWhere }),
      this.prisma.knowledge.findMany({ where: knowledgeWhere }),
      this.prisma.interaction.findMany(),
    ]);

    // 构建节点数据
    const nodes = [
      // 学生节点
      ...students.map(student => ({
        id: student.id,
        type: 'STUDENT' as const,
        name: student.name,
        group: 3,
        val: 8,
        studentProfile: {
          gender: student.gender,
          school: student.school,
          grade: student.grade,
          classId: student.classId,
          knowledgeReserve: student.knowledgeReserve,
          learningEngagement: student.learningEngagement,
          cognitiveLoad: student.cognitiveLoad,
          learningMotivation: student.learningMotivation,
          computationalThinking: student.computationalThinking,
          humanAiTrust: student.humanAiTrust,
          learningMethod: student.learningMethod,
          learningAttitude: student.learningAttitude,
        },
      })),
      // 教师节点
      ...teachers.map(teacher => ({
        id: teacher.id,
        type: 'TEACHER' as const,
        name: teacher.name,
        group: 1,
        val: 25,
        teacherProfile: {
          school: teacher.school,
          teachingGrade: teacher.teachingGrade,
          teachingClass: teacher.teachingClass,
        },
      })),
      // 知识点节点
      ...knowledge.map(k => ({
        id: k.id,
        type: 'KNOWLEDGE' as const,
        name: k.knowledgePoint,
        group: 2,
        val: 15,
        knowledgeProfile: {
          content: k.content,
          type: k.type,
          parentId: k.parentId,
          parentName: k.parentName,
          relatedKnowledgeIds: k.relatedKnowledgeIds,
          relatedKnowledgeNames: k.relatedKnowledgeNames,
        },
      })),
    ];

    // 构建链接数据
    const links = interactions.map(interaction => ({
      source: interaction.sourceId,
      target: interaction.targetId,
      value: interaction.value,
      type: interaction.type,
    }));

    return { nodes, links } as GraphData;
  }
}
```

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

```typescript
// teacher.dto.ts
import { z } from 'zod';

export const createTeacherSchema = z.object({
  name: z.string().min(1, '姓名不能为空'),
  school: z.string().min(1, '学校名称不能为空'),
  teachingGrade: z.string().min(1, '教学年级不能为空'),
  teachingClass: z.string().min(1, '教学班级不能为空'),
});

export type CreateTeacherDto = z.infer<typeof createTeacherSchema>;
```

```typescript
// knowledge.dto.ts
import { z } from 'zod';

export const createKnowledgeSchema = z.object({
  content: z.string().min(1, '知识点内容不能为空'),
  knowledgePoint: z.string().min(1, '知识点标识不能为空'),
  grade: z.string().min(1, '年级不能为空'),
  type: z.enum(['知识单元', '知识点'], { required_error: '知识点类型必须是知识单元或知识点' }),
  parentId: z.string().optional(),
  parentName: z.string().optional(),
  relatedKnowledgeIds: z.array(z.string()).optional(),
  relatedKnowledgeNames: z.array(z.string()).optional(),
});

export type CreateKnowledgeDto = z.infer<typeof createKnowledgeSchema>;
```

```typescript
// interaction.dto.ts
import { z } from 'zod';

export const createInteractionSchema = z.object({
  sourceId: z.string().min(1, '源节点ID不能为空'),
  targetId: z.string().min(1, '目标节点ID不能为空'),
  sourceType: z.enum(['STUDENT', 'TEACHER', 'KNOWLEDGE'], { required_error: '源节点类型必须是STUDENT、TEACHER或KNOWLEDGE' }),
  targetType: z.enum(['STUDENT', 'TEACHER', 'KNOWLEDGE'], { required_error: '目标节点类型必须是STUDENT、TEACHER或KNOWLEDGE' }),
  value: z.number().min(0.1).max(5, '交互值必须在0.1-5之间'),
  type: z.enum(['PHYSICAL', 'PLATFORM'], { required_error: '交互类型必须是PHYSICAL或PLATFORM' }),
  interactionType: z.string().optional(),
});

export type CreateInteractionDto = z.infer<typeof createInteractionSchema>;
```

## 7. 错误处理

### 7.1 标准错误响应

```json
{
  "statusCode": 404,
  "message": "学生不存在",
  "error": "Not Found"
}
```

### 7.2 错误代码

| 状态码 | 描述 |
|-------|------|
| 400 | 请求参数错误 |
| 401 | 未授权 |
| 403 | 禁止访问 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

## 8. 安全设计

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

## 9. 性能优化

1. **缓存策略**：
   - 使用Redis缓存频繁查询的数据
   - 缓存AI分析结果

2. **Prisma 性能优化**：
   - 使用 `findMany` 时合理设置 `take` 和 `skip` 限制
   - 利用 Prisma 的批量操作 API 减少数据库往返
   - 启用 Prisma 的查询缓存（v7.0+ 支持）
   - 使用 `include` 和 `select` 优化关联查询，避免过度获取数据

3. **数据库优化**：
   - 使用索引加速查询
   - 实现数据库连接池
   - 优化复杂查询

4. **异步处理**：
   - 使用异步函数处理IO操作
   - 实现队列处理大量数据导入

## 10. 部署策略

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

## 11. 总结

本API设计基于RESTful规范和Nest.js框架最佳实践，采用Prisma v7.0+作为ORM框架，提供了完整的接口集来支持交互网络可视化系统的所有功能。

### 主要更新内容：

1. **ORM框架升级**：从TypeORM迁移到Prisma v7.0+，享受其类型安全、自动生成查询API和声明式迁移等优势
2. **数据模型定义**：使用Prisma Schema替代传统实体类，简化数据模型管理
3. **教师模型增强**：添加了gender、age、employeeId、title、teachingGrade、teachingClass、subject、slogan等字段，以满足前端教师详细信息展示需求
4. **知识点模型调整**：添加了category字段，以匹配前端知识点分类展示需求
5. **移除分页逻辑**：根据前端实现分析，移除了所有列表接口中的分页逻辑，确保返回完整的数据以满足力导向图布局计算需求
6. **新增图谱数据接口**：添加了`GET /api/graph-data`接口，提供完整的图谱数据（nodes + links），满足前端力导向图可视化需求
7. **完善服务层实现**：添加了完整的Prisma客户端使用示例，包括StudentService、TeacherService、KnowledgeService和GraphService
8. **增强数据验证**：添加了完整的数据验证模式，包括教师、知识点和交互的验证
9. **性能优化**：利用Prisma 7.0+的性能特性，包括查询缓存、批量操作等
10. **架构调整**：优化目录结构，添加prisma目录统一管理数据模型

### 决策依据：

1. **移除分页逻辑**：基于前端代码分析，发现前端实现中不存在列表呈现节点数据的功能，主要依赖力导向图和统计图表展示数据。力导向图需要完整数据集进行布局计算，因此分页逻辑对当前前端实现没有意义。

2. **新增图谱数据接口**：基于前端d3.js力导向图的需求，添加了专门的图谱数据接口，返回完整的节点和链接数据，确保前端能够正确计算节点布局和展示网络关系。

3. **教师模型增强**：根据前端`TeacherProfile`接口定义，添加了相应的字段，确保教师节点能够展示完整的详细信息。

4. **知识点模型调整**：根据前端`KnowledgeProfile`接口定义，添加了category字段，确保知识点节点能够展示分类信息。

5. **完善服务层实现**：添加了完整的Prisma客户端使用示例，确保服务层代码与更新后的API设计保持一致，并且能够正确构建前端所需的图谱数据结构。

### 与前端数据需求的对应关系：

| 前端需求 | API支持 | 对应文件/接口 |
|---------|---------|-------------|
| 力导向图可视化 | 完整图谱数据 | `GET /api/graph-data` |
| 学生认知属性展示 | 学生详情接口 | `GET /api/students/:id` |
| 教师详细信息展示 | 教师详情接口 | `GET /api/teachers/:id` |
| 知识点分类展示 | 知识点详情接口 | `GET /api/knowledge-points/:id` |
| 交互类型区分 | 交互接口 | `GET /api/interactions` |
| 场景化数据筛选 | 图谱数据接口参数 | `GET /api/graph-data?scenario=COLLABORATIVE` |
| 班级数据筛选 | 学生、教师-班级关联接口 | `GET /api/students?school=xxx&grade=xxx&classId=xxx` |

### 技术优势：

1. **Prisma优势**：
   - **类型安全**：自动生成TypeScript类型，提供编译时类型检查
   - **性能提升**：Prisma 7.0+放弃Rust回归TypeScript，性能提升3倍
   - **开发效率**：简洁的查询语法和自动生成的API，减少开发时间
   - **声明式迁移**：支持数据库架构的声明式管理和版本控制
   - **可视化工具**：配套Prisma Studio提供直观的数据管理界面

2. **RESTful最佳实践**：
   - 清晰的资源命名和路径设计
   - 适当的HTTP方法使用
   - 一致的响应格式
   - 完整的错误处理

3. **安全性要求**：
   - 使用Zod进行请求数据验证，防止无效数据
   - 防止SQL注入和XSS攻击
   - 合理的错误处理，避免暴露敏感信息

## 7. 命名规范说明

为了确保API设计的一致性和可维护性，本接口设计采用以下命名规范：

### 7.1 API路径命名规范
- 使用小写字母和连字符（kebab-case）：单词之间使用连字符分隔
- 资源名称使用复数形式
- 包含版本号：`/api/v1/[资源]`
- 避免使用下划线和大写字母

### 7.2 参数命名规范
- 查询参数使用小写字母和连字符（kebab-case）：如`teacher-id`
- 路径参数使用小写字母和连字符（kebab-case）：如`/api/v1/students/:id`
- 请求体参数使用驼峰命名法（camelCase）：如`teacherId`

### 7.3 响应字段命名规范
- 使用驼峰命名法（camelCase）：首字母小写，后续每个单词首字母大写
- 字段名应简洁明了，能够清晰表达字段的含义
- 保持与数据库字段名的映射关系，但使用不同的命名风格以区分前后端

### 7.4 代码命名规范
- 类名和接口名使用帕斯卡命名法（PascalCase）
- 方法名和变量名使用驼峰命名法（camelCase）
- 常量使用大写字母和下划线（SNAKE_CASE）

### 系统架构：

- **前端**：React + TypeScript + D3.js，负责数据可视化和用户交互
- **后端**：Nest.js + TypeScript + Prisma，负责API接口和数据处理
- **数据库**：MSSQL，存储系统数据
- **通信**：RESTful API，提供数据交换

本设计考虑了性能、安全性和可扩展性，确保系统能够高效、安全地运行，为交互网络可视化系统提供可靠的后端支持。通过移除不必要的分页逻辑，简化了API设计，同时通过增强数据模型和添加专门的图谱数据接口，确保了前端能够正确呈现可视化网络交互流程。

同时，严格遵循RESTful API命名规范，使用kebab-case统一API路径和参数命名，使用camelCase统一响应字段命名，提高了API的可读性和可维护性，便于前后端团队协作和后续开发。