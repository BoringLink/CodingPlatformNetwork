# 交互网络可视化系统

## 项目概述

交互网络可视化系统是一个基于Nest.js框架开发的教育数据可视化平台，旨在帮助教育工作者和研究人员分析学生、教师、知识点之间的交互关系，从而优化教学策略和学习体验。

### 核心功能

- **学生管理**：管理学生基本信息、学习属性等数据
- **教师管理**：管理教师基本信息、教学信息等数据
- **知识点管理**：管理课程知识点信息
- **交互分析**：分析学生、教师、知识点之间的交互关系
- **教师观察**：记录和管理教师教学观察数据
- **数据迁移**：支持从Excel文件导入数据
- **AI分析**：利用AI技术分析网络结构和推断属性

### 设计目标

- 提供直观的数据可视化界面，帮助用户理解复杂的交互网络
- 构建高效的数据管理系统，支持大规模教育数据的存储和查询
- 实现智能化的数据分析功能，为教育决策提供支持
- 确保系统的可扩展性和可维护性，便于后续功能迭代

### 应用场景

- 教育研究：分析学生学习行为和教师教学效果
- 教学管理：优化教学资源分配和课程设计
- 个性化学习：基于交互数据为学生提供个性化学习建议
- 教师评估：通过观察数据评估教师教学表现

## 目录结构

```
交互网络可视化系统/
├── backend/                  # 后端代码
│   ├── src/
│   │   ├── modules/          # 功能模块
│   │   │   ├── student/      # 学生模块
│   │   │   ├── teacher/      # 教师模块
│   │   │   ├── knowledge/    # 知识点模块
│   │   │   ├── interaction/  # 交互模块
│   │   │   ├── teacher-observation/  # 教师观察模块
│   │   │   └── data-migration/  # 数据迁移模块
│   │   ├── shared/           # 共享资源
│   │   │   ├── config/       # 配置文件
│   │   │   ├── utils/        # 工具函数
│   │   │   └── decorators/   # 装饰器
│   │   └── main.ts           # 应用入口
│   ├── package.json           # 后端依赖
│   └── .env                   # 后端环境变量
├── .trae/documents/          # 项目文档
│   ├── 交互网络可视化项目技术方案.md    # 技术方案文档
│   ├── 数据库架构设计.md        # 数据库架构设计
│   └── API接口设计.md          # API接口设计
├── Real Data/                # 真实数据
├── README.md                 # 项目说明文档
├── package.json              # 项目依赖
└── .env.local                # 环境变量配置
```

### 主要模块功能说明

| 模块         | 主要功能                     | 文件位置                                 |
| ------------ | ---------------------------- | ---------------------------------------- |
| 学生模块     | 管理学生基本信息和学习属性   | backend/src/modules/student/             |
| 教师模块     | 管理教师基本信息和教学信息   | backend/src/modules/teacher/             |
| 知识点模块   | 管理课程知识点信息           | backend/src/modules/knowledge/           |
| 交互模块     | 分析和管理交互关系数据       | backend/src/modules/interaction/         |
| 教师观察模块 | 记录和管理教师教学观察数据   | backend/src/modules/teacher-observation/ |
| 数据迁移模块 | 支持从Excel文件导入数据      | backend/src/modules/data-migration/      |
| 共享资源     | 提供配置、工具函数等共享功能 | backend/src/shared/                      |

## 技术栈

- **后端框架**：Nest.js
- **开发语言**：TypeScript
- **数据库**：MSSQL
- **ORM**：TypeORM
- **数据验证**：Zod
- **数据处理**：xlsx (Excel文件处理)

## 项目启动指南

### 环境要求

- **Node.js**：v16.0.0 或更高版本
- **npm**：v8.0.0 或更高版本
- **MSSQL**：SQL Server 2019 或更高版本

### 1. 克隆项目

```bash
git clone https://github.com/BoringLink/CodingPlatformNetwork.git 交互网络可视化系统
cd 交互网络可视化系统
```

### 2. 安装依赖

```bash
# 安装项目依赖
npm install

# 进入后端目录并安装后端依赖
cd backend
npm install
cd ..
```

### 3. 配置环境变量

#### 3.1 前端环境变量

编辑 `.env.local` 文件，设置以下环境变量：

```env
# .env.local
# 前端环境变量
NEXT_PUBLIC_API_URL=http://localhost:3000/api

# Gemini API Key (用于AI分析功能)
GEMINI_API_KEY=your_gemini_api_key
```

#### 3.2 后端环境变量

编辑 `backend/.env` 文件，设置以下环境变量：

```env
# .env
# 数据库连接配置
DATABASE_HOST=rm-bp10v29fkj305q3smfo.sqlserver.rds.aliyuncs.com
DATABASE_PORT=3433
DATABASE_USERNAME=coding_data
DATABASE_PASSWORD=root
DATABASE_NAME=interaction_network_db

# AI API Key
AI_API_KEY=your_aliyun_ai_key
```

### 4. 启动项目

#### 4.1 启动后端服务

```bash
# 进入后端目录
cd backend

# 启动后端服务
npm run start:dev

# 后端服务将运行在 http://localhost:3000
```

#### 4.2 启动前端服务

```bash
# 回到项目根目录
cd ..

# 启动前端服务
npm run dev

# 前端服务将运行在 http://localhost:8080
```

### 5. 验证服务启动

- 后端服务：访问 http://localhost:3000/api/health，应该返回健康状态信息
- 前端服务：访问 http://localhost:8080，应该看到系统登录页面

## 数据导入指南

### 从Excel文件导入数据

1. 准备Excel数据文件，确保数据格式符合系统要求
2. 登录系统后，进入数据迁移模块
3. 上传Excel文件并选择导入类型
4. 系统将自动解析文件并导入数据
5. 查看导入结果，确认数据导入成功

## 开发指南

### 代码规范

- 使用TypeScript编写代码，确保类型安全
- 遵循Nest.js的代码风格和最佳实践
- 实现模块间的解耦，提高代码可维护性
- 添加适当的注释，提高代码可读性

### 测试

- 为关键功能编写单元测试
- 定期运行测试，确保代码质量
- 使用Postman或其他API测试工具测试接口

### 部署

- 使用Docker容器化部署，确保环境一致性
- 配置CI/CD流水线，实现自动化部署
- 监控系统运行状态，及时发现和解决问题

## 技术支持

- 文档：查看项目文档目录下的技术文档
- 代码注释：参考代码中的详细注释
- 问题反馈：通过项目issue系统提交问题

## 版本信息

- 版本：v1.0.0
- 发布日期：2026-02-06
- 最后更新：2026-02-06
