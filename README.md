# 交互网络可视化系统 - 技术文档

## 1. 目录结构

系统采用模块化架构设计，清晰分离核心功能模块。以下是详细的目录结构说明：

```
交互网络可视化系统/
├── backend/                  # 后端代码目录
│   ├── lib/                  # 编译输出目录
│   ├── prisma/               # Prisma ORM 配置
│   │   ├── migrations/       # 数据库迁移文件
│   │   └── schema.prisma     # 数据模型定义
│   ├── src/                  # 源代码目录
│   │   ├── modules/          # 功能模块目录
│   │   │   ├── graph/        # 图谱模块
│   │   │   ├── interaction/  # 交互分析模块
│   │   │   ├── interaction-session/  # 交互会话模块
│   │   │   ├── node/         # 节点模块
│   │   │   ├── org/          # 组织模块
│   │   │   ├── scenario/     # 场景模块
│   │   │   └── student/      # 学生模块
│   │   ├── shared/           # 共享资源目录
│   │   │   ├── types/        # 类型定义
│   │   │   └── utils/        # 工具函数
│   │   ├── app.module.ts     # 应用模块
│   │   └── main.ts           # 应用入口文件
│   ├── test/                 # 测试目录
│   ├── .env.example          # 环境变量示例
│   ├── package.json          # 后端依赖配置
│   └── tsconfig.json         # TypeScript 配置
├── frontend/                 # 前端代码目录
│   ├── components/           # 前端组件
│   │   ├── AnalysisPanel.tsx # 分析面板组件
│   │   └── NetworkGraph.tsx  # 网络图谱组件
│   ├── services/             # 前端服务
│   │   ├── apiService.ts     # API 服务
│   │   ├── dataConfig.ts     # 数据配置
│   │   ├── dataParser.ts     # 数据解析器
│   │   ├── dataService.ts    # 数据服务
│   │   ├── dataValidator.ts  # 数据验证器
│   │   ├── performanceUtils.ts # 性能工具
│   │   ├── realData.ts       # 真实数据处理
│   │   └── strategies.ts     # 策略处理
│   ├── src/                  # 源代码目录
│   │   └── setupTests.ts     # 测试设置
│   ├── App.tsx               # 应用主组件
│   ├── index.html            # HTML 入口
│   ├── index.tsx             # TypeScript 入口
│   ├── package.json          # 前端依赖配置
│   └── vite.config.ts        # Vite 配置
├── README.md                 # 项目技术文档
└── package.json              # 项目依赖配置
```

### 1.1 目录说明

| 目录/文件 | 功能说明                         | 重要性 |
| --------- | -------------------------------- | ------ |
| backend/  | 后端代码主目录，包含所有后端逻辑 | 核心   |
| frontend/ | 前端代码主目录，包含所有前端逻辑 | 核心   |

## 2. 模块功能详解

### 2.1 后端模块

#### 2.1.1 图谱模块 (backend/src/modules/graph/)

**核心功能：**

- 图谱数据管理
- 图谱结构分析
- 图谱数据生成和处理

**主要组件：**

- `GraphController`：处理图谱相关的 HTTP 请求
- `GraphService`：实现图谱业务逻辑
- `GraphModule`：模块配置

#### 2.1.2 交互分析模块 (backend/src/modules/interaction/)

**核心功能：**

- 交互数据管理
- 交互关系分析
- 交互数据统计

**主要组件：**

- `InteractionController`：处理交互相关的 HTTP 请求
- `InteractionService`：实现交互分析业务逻辑
- `InteractionDto`：数据传输对象
- `InteractionModule`：模块配置

#### 2.1.3 交互会话模块 (backend/src/modules/interaction-session/)

**核心功能：**

- 交互会话管理
- 会话数据处理
- 会话分析

**主要组件：**

- `InteractionSessionController`：处理交互会话相关的 HTTP 请求
- `InteractionSessionService`：实现交互会话业务逻辑
- `InteractionSessionDto`：数据传输对象
- `InteractionSessionModule`：模块配置

#### 2.1.4 节点模块 (backend/src/modules/node/)

**核心功能：**

- 节点数据管理
- 节点属性处理
- 节点关系管理

**主要组件：**

- `NodeController`：处理节点相关的 HTTP 请求
- `NodeService`：实现节点业务逻辑
- `NodeDto`：数据传输对象
- `NodeModule`：模块配置

#### 2.1.5 组织模块 (backend/src/modules/org/)

**核心功能：**

- 组织信息管理
- 组织结构处理

**主要组件：**

- `OrgController`：处理组织相关的 HTTP 请求
- `OrgService`：实现组织业务逻辑
- `OrgModule`：模块配置

#### 2.1.6 场景模块 (backend/src/modules/scenario/)

**核心功能：**

- 场景信息管理
- 场景配置处理

**主要组件：**

- `ScenarioController`：处理场景相关的 HTTP 请求
- `ScenarioService`：实现场景业务逻辑
- `ScenarioModule`：模块配置

#### 2.1.7 学生模块 (backend/src/modules/student/)

**核心功能：**

- 学生信息管理
- 学生数据处理

**主要组件：**

- `StudentController`：处理学生相关的 HTTP 请求
- `StudentService`：实现学生业务逻辑
- `StudentDto`：数据传输对象
- `StudentModule`：模块配置

#### 2.1.8 共享资源模块 (backend/src/shared/)

**核心功能：**

- 类型定义
- 工具函数
- 数据库服务

**主要组件：**

- `types/`：类型定义文件
- `utils/`：工具函数集合
- `prisma.service.ts`：Prisma 数据库服务

### 2.2 前端模块

#### 2.2.1 组件模块 (frontend/components/)

**核心功能：**

- 分析面板组件
- 网络图谱组件

**主要组件：**

- `AnalysisPanel.tsx`：分析面板组件，用于展示分析结果
- `NetworkGraph.tsx`：网络图谱组件，用于可视化交互网络

#### 2.2.2 服务模块 (frontend/services/)

**核心功能：**

- API 服务
- 数据处理服务
- 数据验证服务
- 性能工具

**主要组件：**

- `apiService.ts`：API 服务，处理与后端的通信
- `dataService.ts`：数据服务，处理数据逻辑
- `dataParser.ts`：数据解析器，解析和转换数据
- `dataValidator.ts`：数据验证器，验证数据格式
- `performanceUtils.ts`：性能工具，优化前端性能
- `realData.ts`：真实数据处理
- `strategies.ts`：策略处理

## 3. 开发指南

### 3.1 环境要求

- **Node.js**：v16.0.0 或更高版本
- **npm**：v8.0.0 或更高版本
- **MSSQL**：SQL Server 2019 或更高版本

### 3.2 项目启动

#### 3.2.1 安装依赖

```bash
# 进入后端目录并安装后端依赖
cd backend
pnpm install
cd ..

# 进入前端目录并安装前端依赖
cd frontend
pnpm install
cd ..
```

#### 3.2.2 启动服务

```bash
# 启动后端服务
cd backend
pnpm start:dev
# 后端服务将运行在 http://localhost:3000

# 启动前端服务 (在另一个终端)
cd frontend
pnpm dev
# 前端服务将运行在 http://localhost:8080
```

### 3.3 命名规范

- **类名和接口名**：使用帕斯卡命名法（PascalCase），如 `StudentService`
- **方法名和变量名**：使用驼峰命名法（camelCase），如 `findAllStudents`
- **常量**：使用大写字母和下划线（SNAKE_CASE），如 `MAX_PAGE_SIZE`
- **文件和目录名**：使用小写字母和连字符（kebab-case），如 `student-controller.ts`

### 3.4 API 命名规范

- **API 路径**：使用蛇形命名法（snake_case），如 `/api/v1/students`
- **查询参数**：使用蛇形命名法（snake_case），如 `teacher_id`
- **请求体参数**：使用驼峰命名法（camelCase），如 `teacherId`
- **响应字段**：使用驼峰命名法（camelCase），如 `studentProfile`

### 3.5 数据库命名规范

- **表名**：使用蛇形命名法（snake_case），全部小写，单词之间使用下划线分隔，复数形式，如 `students`
- **字段名**：使用蛇形命名法（snake_case），全部小写，如 `learning_engagement`
- **索引名**：使用 `[表名]_[字段1]_[字段2]...` 格式，如 `students_school_grade`

## 4. 数据模型

系统核心数据模型包括：

- **学生 (Student)**：存储学生基本信息和学习属性
- **教师 (Teacher)**：存储教师基本信息和教学信息
- **知识点 (Knowledge)**：存储课程知识点信息
- **交互 (Interaction)**：存储三者之间的交互关系
- **节点 (Node)**：存储网络节点信息
- **图谱 (Graph)**：存储网络图谱信息
- **场景 (Scenario)**：存储场景信息
- **组织 (Org)**：存储组织信息

详细数据模型定义请参考 `backend/prisma/schema.prisma` 文件。

## 5. API 接口

系统提供完整的 RESTful API 接口，包括：

- **图谱管理接口**：/api/graph
- **交互管理接口**：/api/interaction
- **交互会话接口**：/api/interaction-session
- **节点管理接口**：/api/node
- **组织管理接口**：/api/org
- **场景管理接口**：/api/scenario
- **学生管理接口**：/api/student

详细 API 接口设计请参考项目内部文档。

## 6. 部署指南

### 6.1 前端部署

1. 构建前端项目：

   ```bash
   cd frontend
   pnpm build
   ```

2. 将构建产物部署到指定目录：

   ```bash
   # 确保目标目录存在
   sudo mkdir -p /var/www/interaction-network/frontend

   # 复制构建文件
   sudo cp -r dist/* /var/www/interaction-network/frontend/

   # 设置权限
   sudo chown -R www-data:www-data /var/www/interaction-network/frontend
   ```

3. 配置 Web 服务器（如 Nginx）指向 `/var/www/interaction-network/frontend` 目录。

### 6.2 后端部署

1. 构建后端项目：

   ```bash
   cd backend
   pnpm build
   ```

2. 安装 PM2：

   ```bash
   npm install -g pm2
   ```

3. 使用 PM2 启动后端服务：

   ```bash
   # 在 backend 目录下执行
   pm2 start dist/main.js --name interaction-network-backend
   ```

4. 设置 PM2 开机自启：

   ```bash
   pm2 save
   pm2 startup
   ```

5. 查看服务状态：
   ```bash
   pm2 status
   ```

## 7. 待办清单

- [ ] 通义千问大模型集成
