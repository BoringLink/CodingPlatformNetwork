# 学习场景区分技术方案（数据库与API专题详规）

配套主文档：

- [学习场景级联筛选与认知模板完整方案.md](./学习场景级联筛选与认知模板完整方案.md)

## 1. 设计前提

当前数据库历史数据可放弃，因此本方案不做兼容迁移，不保留旧表结构约束，直接采用面向长期演进的重建式最佳实践：

1. 强类型建模，避免弱约束字符串字段。
2. 全量外键约束，保证关系一致性。
3. 场景维度标准化，支持过滤、统计、对比分析。
4. API 统一语义，便于前端和分析任务长期迭代。

同时遵循业务硬约束：

1. 系统仅存储学生最终认知模板结果，不存储问卷原始数据。
2. 系统不提供问卷导入、明细查询、重算接口。
3. 不采集、不存储、不展示性别信息。

---

## 2. 场景体系（标准字典）

采用编码 + 中文名 + 状态的字典表，不把中文名称当主键。

| code            | name_zh              | sort_order |
| --------------- | -------------------- | ---------- |
| ONLINE_COURSE   | 学科课程在线学习     | 1          |
| AFTER_SCHOOL_QA | 课后线上教师授课答疑 | 2          |
| HOME_LEARNING   | 家庭在线学习         | 3          |
| COLLABORATIVE   | 在线协作学习         | 4          |
| INFORMAL_CLUBS  | 社团课等非正式学习   | 5          |

建议：前端只传 `code`，展示时通过字典转换中文。

---

## 3. 数据库最佳实践设计（SQL Server + Prisma）

### 3.1 总体结构

采用统一节点 + 节点扩展属性 + 交互事实表 + 场景维度 + 会话维度五层结构：

1. `learning_scenarios`：学习场景维度。
2. `graph_nodes`：网络统一节点（学生/教师/知识点）。
3. `student_profiles` / `teacher_profiles` / `knowledge_profiles`：节点类型扩展属性（1:1）。
4. `interaction_sessions`：交互会话（一次课/一次答疑/一次协作活动）。
5. `interactions`：交互事实（边）。

该设计优点：

1. 彻底消除 `sourceId + sourceType` 的弱约束问题。
2. 节点之间关系统一，图谱构建天然一致。
3. 场景与时间维度可独立统计，适合后续分析与可视化。

### 3.2 推荐表结构

#### 表 A：`learning_scenarios`

- `id` `String` PK
- `code` `String` UNIQUE
- `nameZh` `String`
- `description` `String?`
- `sortOrder` `Int`
- `isActive` `Boolean`
- `createdAt` `DateTime`
- `updatedAt` `DateTime`

索引：

- `UNIQUE(code)`
- `INDEX(isActive, sortOrder)`

#### 表 B：`graph_nodes`

- `id` `String` PK
- `nodeType` `Enum` (`STUDENT`, `TEACHER`, `KNOWLEDGE`)
- `displayName` `String`
- `school` `String?`
- `grade` `String?`
- `classId` `String?`
- `isActive` `Boolean`
- `createdAt` `DateTime`
- `updatedAt` `DateTime`

索引：

- `INDEX(nodeType)`
- `INDEX(school, grade, classId)`
- `INDEX(nodeType, school, grade)`

说明：

- 把学校/年级/班级沉淀到统一节点层，图谱查询可直接做节点过滤。

#### 表 C1：`student_profiles`（1:1 扩展）

- `nodeId` `String` PK/FK -> `graph_nodes.id`
- `learningStylePreference` `String?`
- `personality` `String?`
- `groupBehavior` `String?`
- `createdAt` `DateTime`
- `updatedAt` `DateTime`

#### 表 C2：`teacher_profiles`（1:1 扩展）

- `nodeId` `String` PK/FK
- `teachingGrade` `String?`
- `teachingClass` `String?`
- `subject` `String?`
- `createdAt` `DateTime`
- `updatedAt` `DateTime`

#### 表 C3：`knowledge_profiles`（1:1 扩展）

- `nodeId` `String` PK/FK
- `content` `String`
- `knowledgeType` `String`
- `category` `String?`
- `parentNodeId` `String?` FK -> `graph_nodes.id`
- `createdAt` `DateTime`
- `updatedAt` `DateTime`

附加关系表（替代 JSON 字符串）：

#### 表 C4：`knowledge_relations`

- `id` `String` PK
- `fromKnowledgeNodeId` `String` FK
- `toKnowledgeNodeId` `String` FK
- `relationType` `String`（`PREREQUISITE`/`RELATED`/`CONTAINS`）
- `weight` `Decimal(5,2)?`

索引：

- `INDEX(fromKnowledgeNodeId, relationType)`
- `INDEX(toKnowledgeNodeId, relationType)`
- `UNIQUE(fromKnowledgeNodeId, toKnowledgeNodeId, relationType)`

#### 表 D：`interaction_sessions`

- `id` `String` PK
- `scenarioId` `String` FK -> `learning_scenarios.id`
- `sessionName` `String`
- `occurredAt` `DateTime`
- `school` `String?`
- `grade` `String?`
- `classId` `String?`
- `meta` `Json?`
- `createdAt` `DateTime`
- `updatedAt` `DateTime`

索引：

- `INDEX(scenarioId, occurredAt)`
- `INDEX(school, grade, classId, occurredAt)`

#### 表 E：`interactions`（核心事实表）

- `id` `String` PK
- `sessionId` `String` FK -> `interaction_sessions.id`
- `sourceNodeId` `String` FK -> `graph_nodes.id`
- `targetNodeId` `String` FK -> `graph_nodes.id`
- `interactionType` `Enum` (`PHYSICAL`, `PLATFORM`)
- `strength` `Decimal(6,3)`（替代旧 `value`）
- `actionType` `String?`（如提问、讲解、协作）
- `durationSec` `Int?`
- `createdAt` `DateTime`

索引：

- `INDEX(sessionId)`
- `INDEX(sourceNodeId, targetNodeId)`
- `INDEX(targetNodeId)`
- `INDEX(interactionType, createdAt)`
- `UNIQUE(sessionId, sourceNodeId, targetNodeId, interactionType, actionType)`（防重复写入）

### 3.3 认知模板结果模型（仅最终结果）

#### 表 F：`cognitive_dimension_defs`

- `id` `String` PK
- `dimensionCode` `String` UNIQUE
- `dimensionNameZh` `String`
- `categoryName` `String?`
- `minScore` `Decimal(5,2)`
- `maxScore` `Decimal(5,2)`
- `sortOrder` `Int`
- `isActive` `Boolean`

#### 表 G：`student_cognitive_profiles`

- `id` `String` PK
- `studentNodeId` `String` FK -> `graph_nodes.id`
- `profileVersion` `String`
- `generatedAt` `DateTime`
- `totalScore` `Decimal(6,2)`
- `createdAt` `DateTime`

索引：

- `INDEX(studentNodeId, generatedAt DESC)`

#### 表 H：`student_cognitive_dimension_scores`

- `id` `String` PK
- `profileId` `String` FK -> `student_cognitive_profiles.id`
- `dimensionCode` `String`
- `scoreValue` `Decimal(5,2)`
- `scoreLevel` `String?`
- `createdAt` `DateTime`

索引：

- `UNIQUE(profileId, dimensionCode)`

说明：

1. 仅保存最终模板结果（总分 + 维度分）。
2. 不保存问卷原始答案、题目映射明细、提交记录。
3. 认知模板由离线流程产出后入库。

### 3.4 关键约束建议

1. 禁止软编码类型：`nodeType`、`interactionType` 必须用 Enum。
2. 全链路外键：事实表不可存在悬挂 ID。
3. 数值类型统一用 Decimal，避免浮点误差。
4. 强制审计字段：`createdAt/updatedAt` 全表必备。
5. 认知模板仅保存最终分值，不落问卷原始数据。

### 3.5 Prisma 模型骨架（示意）

```prisma
enum NodeType {
  STUDENT
  TEACHER
  KNOWLEDGE
}

enum InteractionType {
  PHYSICAL
  PLATFORM
}

model LearningScenario {
  id          String   @id @default(cuid())
  code        String   @unique
  nameZh      String
  description String?
  sortOrder   Int      @default(0)
  isActive    Boolean  @default(true)
  createdAt   DateTime @default(now())
  updatedAt   DateTime @updatedAt

  sessions InteractionSession[]

  @@map("learning_scenarios")
  @@index([isActive, sortOrder])
}

model GraphNode {
  id          String   @id @default(cuid())
  nodeType    NodeType
  displayName String
  school      String?
  grade       String?
  classId     String?
  isActive    Boolean  @default(true)
  createdAt   DateTime @default(now())
  updatedAt   DateTime @updatedAt

  outgoingInteractions Interaction[] @relation("SourceNode")
  incomingInteractions Interaction[] @relation("TargetNode")

  @@map("graph_nodes")
  @@index([nodeType])
  @@index([school, grade, classId])
}

model InteractionSession {
  id          String   @id @default(cuid())
  scenarioId  String
  sessionName String
  occurredAt  DateTime
  school      String?
  grade       String?
  classId     String?
  meta        Json?
  createdAt   DateTime @default(now())
  updatedAt   DateTime @updatedAt

  scenario     LearningScenario @relation(fields: [scenarioId], references: [id])
  interactions Interaction[]

  @@map("interaction_sessions")
  @@index([scenarioId, occurredAt])
  @@index([school, grade, classId, occurredAt])
}

model Interaction {
  id              String          @id @default(cuid())
  sessionId       String
  sourceNodeId    String
  targetNodeId    String
  interactionType InteractionType
  strength        Decimal         @db.Decimal(6, 3)
  actionType      String?
  durationSec     Int?
  createdAt       DateTime        @default(now())

  session    InteractionSession @relation(fields: [sessionId], references: [id])
  sourceNode GraphNode          @relation("SourceNode", fields: [sourceNodeId], references: [id])
  targetNode GraphNode          @relation("TargetNode", fields: [targetNodeId], references: [id])

  @@map("interactions")
  @@index([sessionId])
  @@index([sourceNodeId, targetNodeId])
  @@index([targetNodeId])
  @@index([interactionType, createdAt])
  @@unique([sessionId, sourceNodeId, targetNodeId, interactionType, actionType])
}
```

---

## 4. 后端 API 最佳实践设计

统一前缀：`/api/v1`

### 4.1 场景 API

#### 1) 获取场景列表

- `GET /api/v1/scenarios`

响应：

```json
{
  "data": [
    {
      "code": "ONLINE_COURSE",
      "nameZh": "学科课程在线学习",
      "sortOrder": 1,
      "isActive": true
    }
  ]
}
```

### 4.2 节点 API

#### 1) 节点查询

- `GET /api/v1/nodes?node_type=STUDENT&school=...&grade=...&class_id=...`

#### 2) 节点创建

- `POST /api/v1/nodes`

说明：根据 `nodeType` 分流写入对应 profile 子表。

### 4.3 会话 API（新增，强烈建议）

#### 1) 创建交互会话

- `POST /api/v1/interaction-sessions`

请求示例：

```json
{
  "scenarioCode": "COLLABORATIVE",
  "sessionName": "3年级5班第2次协作任务",
  "occurredAt": "2026-03-19T10:00:00Z",
  "school": "宁波市镇海应行久外语实验学校",
  "grade": "3年级",
  "classId": "三年级5班"
}
```

#### 2) 查询会话

- `GET /api/v1/interaction-sessions?scenario_code=COLLABORATIVE&grade=3年级`

### 4.4 交互 API

#### 1) 批量写入交互（推荐主入口）

- `POST /api/v1/interactions:batchCreate`

请求示例：

```json
{
  "sessionId": "ses_xxx",
  "items": [
    {
      "sourceNodeId": "node_stu_1",
      "targetNodeId": "node_know_3",
      "interactionType": "PLATFORM",
      "strength": 1.85,
      "actionType": "QUESTION"
    }
  ]
}
```

#### 2) 查询交互

- `GET /api/v1/interactions?scenario_code=ONLINE_COURSE&session_id=...&source_node_id=...`

实现要求：

- `scenario_code` 实际通过 `session -> scenario` 进行过滤。
- 默认分页：`page=1&page_size=50`，最大 `page_size=500`。

### 4.5 图谱 API（核心）

#### 1) 拉取图谱

- `GET /api/v1/graph-data?scenario_code=ONLINE_COURSE&school=...&grade=...&class_id=...&from=...&to=...`

返回结构：

```json
{
  "nodes": [
    {
      "id": "node_stu_1",
      "type": "STUDENT",
      "name": "张三"
    }
  ],
  "links": [
    {
      "source": "node_stu_1",
      "target": "node_know_3",
      "type": "PLATFORM",
      "value": 1.85
    }
  ],
  "meta": {
    "scenarioCode": "ONLINE_COURSE",
    "nodeCount": 120,
    "linkCount": 560
  }
}
```

#### 2) 场景对比统计

- `GET /api/v1/graph-data/scenario-stats?school=...&grade=...&class_id=...&from=...&to=...`

返回每个场景的：

- `nodeCount`
- `linkCount`
- `avgStrength`
- `density`
- `studentTeacherRatio`

### 4.6 学生认知模板 API

#### 1) 获取学生最新认知模板

- `GET /api/v1/students/{student_node_id}/cognitive-template`

返回结构建议：

```json
{
  "data": {
    "student": {
      "id": "node_stu_1",
      "name": "张三"
    },
    "profile": {
      "profileVersion": "v2026-03-19",
      "generatedAt": "2026-03-19T10:00:00Z",
      "totalScore": 82.5
    },
    "dimensions": [
      {
        "dimensionCode": "LEARNING_ENGAGEMENT",
        "dimensionNameZh": "学习投入",
        "scoreValue": 84.0,
        "scoreLevel": "HIGH"
      }
    ]
  }
}
```

说明：

1. 仅返回最终模板结果。
2. 不返回问卷题目级明细。
3. 不返回性别字段。

### 4.7 明确不提供的接口

1. 不提供问卷导入接口。
2. 不提供问卷明细查询接口。
3. 不提供问卷重算接口（由离线流程处理）。

---

## 5. API 约束与工程规范

1. 所有写接口使用 DTO + zod 或 class-validator 双重校验。
2. 所有查询接口统一分页与排序参数。
3. 返回体统一 `{ data, meta, error }` 结构。
4. 使用幂等键（`Idempotency-Key`）保护批量写入。
5. 核心接口增加限流（如 `interactions:batchCreate`）。

错误码建议：

- `SCENARIO_CODE_INVALID`
- `NODE_NOT_FOUND`
- `SESSION_NOT_FOUND`
- `INTERACTION_DUPLICATED`
- `COGNITIVE_PROFILE_NOT_FOUND`
- `VALIDATION_ERROR`

---

## 6. 初始化与落地步骤（重建模式）

1. 清空旧 schema，重建 Prisma 模型与迁移。
2. 初始化 5 个场景字典数据（seed）。
3. 接入节点与 profile 写入。
4. 接入会话创建与批量交互写入。
5. 接入图谱查询、场景统计与认知模板查询接口。
6. 补齐测试：
   - 单元测试：DTO 校验、service 过滤逻辑。
   - 集成测试：按场景过滤正确性。
  - 集成测试：学生模板查询与维度完整性。
   - 性能测试：图谱接口大分页/时间窗查询。

---

## 7. 验收标准

1. 5 大场景可独立筛选和统计。
2. 图谱接口按场景返回结果完全隔离。
3. 交互数据不存在无效节点引用（外键保证）。
4. 任意场景可按学校/年级/班级/时间窗组合查询。
5. 核心查询在目标数据规模下满足性能指标（建议 P95 < 500ms）。

---

## 8. 最终结论

在不考虑兼容历史数据的条件下，最佳实践是采用统一节点模型 + 会话事实模型 + 场景维度模型。该方案在数据一致性、扩展性、统计能力和后续维护成本上明显优于在旧结构上打补丁，适合作为三元交互网络系统的长期主干架构。
