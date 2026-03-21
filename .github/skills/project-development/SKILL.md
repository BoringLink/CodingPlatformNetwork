---
name: project-development
description: "Use when: setting up development environment, reviewing project structure, establishing coding standards, managing git workflow, or onboarding to full-stack education data visualization project. Covers monorepo structure, NestJS backend, React frontend, development conventions, testing, and deployment practices."
---

# 项目开发规范与工作流指南

交互网络可视化系统是一个 **Monorepo 全栈项目**，包含 NestJS 后端和 React 前端。本skill为团队开发提供统一的规范和最佳实践。

## 快速启动

### 1. 环境准备

```bash
# 确保已安装
node --version  # v18+
pnpm --version  # v8+

# 安装根级依赖
pnpm install

# 安装后端依赖
cd backend && pnpm install && cd ..

# 安装前端依赖
cd frontend && pnpm install && cd ..
```

### 2. Python 虚拟环境设置（如果需要Python脚本）

```bash
# ⚠️ 重要：检查是否已有虚拟环境
ls -la | grep venv  # 或其他虚拟环境目录

# 如果没有虚拟环境，创建一个（使用uv）
uv venv

# 激活虚拟环境
source .venv/bin/activate  # macOS/Linux
# 或
.venv\Scripts\activate     # Windows

# 验证虚拟环境激活成功
which python  # 应该指向 .venv/bin/python
```

### 3. 启动开发服务器

```bash
# 方案A: 并行运行后端+前端（推荐）
# 终端1 - 后端（端口3333）
cd backend && pnpm start:dev

# 终端2 - 前端（端口3000）
cd frontend && pnpm dev

# ⚠️ 注意端口冲突和重启需求
# - 前端（React + Vite）支持热重载，修改文件后会自动刷新
# - 后端（Nest.js + Prisma）不支持热重载，修改后需要手动重启
# - 如果遇到「端口3000/3333已占用」错误
#   表示开发服务已在后台运行，无需重启
#   直接访问 localhost:3333 (后端) 和 localhost:3000 (前端)
```

### 4. 快速验证

```bash
# 后端健康检查
curl http://localhost:3333

# 前端访问
open http://localhost:3000  # macOS
# 或在浏览器输入: http://localhost:3000
```

---

## 目录结构详解

```
project-root/
├── backend/                    # NestJS 后端应用
│   ├── src/
│   │   ├── main.ts            # 应用入口
│   │   ├── app.module.ts       # 根模块
│   │   ├── modules/            # 功能模块（按MVC分层）
│   │   │   ├── student/        # 学生模块
│   │   │   ├── teacher/        # 教师模块
│   │   │   ├── knowledge/      # 知识点模块
│   │   │   ├── interaction/    # 交互分析模块
│   │   │   ├── node/           # 网络节点数据模块
│   │   │   ├── org/            # 组织机构模块
│   │   │   ├── scenario/       # 学习场景模块
│   │   │   ├── graph/          # 图谱数据模块
│   │   │   ├── interaction-session/  # 交互会话模块
│   │   │   ├── teacher-observation/  # 教师观察数据模块
│   │   │   └── data-migration/ # 数据导入迁移模块
│   │   ├── shared/             # 共享资源
│   │   │   ├── config/         # 应用配置
│   │   │   ├── decorators/     # NestJS 装饰器
│   │   │   ├── types/          # 共享TypeScript类型
│   │   │   └── utils/          # 公共工具函数
│   │   └── test/               # 单元测试文件
│   ├── prisma/
│   │   ├── schema.prisma       # 数据库模型定义（权威真值）
│   │   ├── seed.ts             # 数据初始化脚本
│   │   └── migrations/         # 数据库版本控制
│   ├── package.json            # 后端依赖声明
│   └── tsconfig.json           # 后端TypeScript配置
│
├── frontend/                   # React + Vite 前端应用
│   ├── src/
│   │   ├── index.tsx           # React 入口
│   │   ├── App.tsx             # 根组件
│   │   ├── types.ts            # 全局类型定义
│   │   ├── components/         # React 组件库
│   │   │   ├── NetworkGraph.tsx    # D3可视化核心
│   │   │   ├── AnalysisPanel.tsx   # 数据分析面板
│   │   │   └── ...
│   │   ├── services/           # 业务逻辑层
│   │   │   ├── apiService.ts   # API调用
│   │   │   ├── dataService.ts  # 数据处理
│   │   │   ├── dataParser.ts   # 数据解析
│   │   │   ├── dataValidator.ts # 数据验证
│   │   │   ├── strategies.ts   # 增强算法
│   │   │   └── performanceUtils.ts
│   │   └── src/
│   │       ├── setupTests.ts   # Jest配置
│   │       └── components/     # 更多组件
│   ├── index.html              # HTML模板
│   ├── package.json            # 前端依赖声明
│   ├── vite.config.ts          # Vite构建配置
│   └── tsconfig.json           # 前端TypeScript配置
│
├── documents/                  # 项目文档
│   ├── 学习场景级联筛选与认知模板完整方案.md
│   ├── 学习场景区分技术方案_数据库与API设计.md
│   ├── 问卷与认知模板映射.md
│   └── 学生问卷数据_清洗.jsonl
│
├── Real Data/                  # 测试数据集
│   ├── 教师列表_filtered.json
│   └── 知识点.json
│
├── .github/                    # GitHub配置
│   └── skills/                 # AI Copilot工作流技能
│
├── package.json                # 根级配置文件
├── pnpm-lock.yaml              # 依赖锁定文件
├── playwright.config.ts        # E2E测试配置
└── README.md                   # 项目概览
```

### 关键路径速查

| 需求            | 路径                             |
| --------------- | -------------------------------- |
| 添加新数据库表  | `backend/prisma/schema.prisma`   |
| 添加新后端API   | `backend/src/modules/{feature}/` |
| 添加新React组件 | `frontend/src/components/`       |
| 编写后端测试    | `backend/src/{module}.spec.ts`   |
| 配置共享常量    | `backend/src/shared/config/`     |
| 修改全局类型    | `frontend/src/types.ts`          |

---

## 开发规范

### 代码风格与格式

#### TypeScript 规范

**命名约定：**

```typescript
// ✅ 类 - PascalCase，可选后缀
class StudentService {}
class UserDTO {}
interface INodeData {}
type NodeType = "student" | "teacher" | "knowledge";

// ✅ 函数 - camelCase
function calculateNetworkMetrics() {}
const parseExcelData = () => {};

// ✅ 常量 - UPPER_SNAKE_CASE（重要常量）
const MAX_BATCH_SIZE = 1000;
const DEFAULT_TIMEOUT = 30000;

// ✅ 私有字段 - camelCase 前缀 # 或 private
class DataProcessor {
  #buffer: Buffer;
  private cache: Map<string, any>;
}
```

**文件结构规范：**

```typescript
// 顺序: 导入 > 类型定义 > 类/函数实现 > 导出

// 1. 外部导入
import { Injectable, Controller } from "@nestjs/common";
import { Prisma } from "@prisma/client";

// 2. 内部导入
import { DatabaseService } from "../shared/database.service";
import { NodeDTO } from "./node.dto";

// 3. 类型定义
interface ProcessingOptions {
  batchSize?: number;
  verbose?: boolean;
}

// 4. 实现
@Injectable()
export class NodeService {
  constructor(private db: DatabaseService) {}

  async processNodes(data: NodeDTO[]): Promise<void> {
    // 实现
  }
}

// 5. 导出
export { NodeService };
```

#### 后端 (NestJS) 特定规范

**模块组织：**

```
modules/student/
├── student.controller.ts    # HTTP路由 @Controller
├── student.service.ts       # 业务逻辑 @Injectable
├── student.dto.ts           # 数据传输对象 (request/response)
├── student.entity.ts        # 数据库表映射（可选）
├── student.module.ts        # 模块定义 @Module
└── student.spec.ts          # 单元测试
```

**命名约定：**

```typescript
// Controller
@Controller("students")
export class StudentController {
  constructor(private readonly studentService: StudentService) {}

  @Get()
  async findAll(): Promise<StudentDTO[]> {}
}

// Service
@Injectable()
export class StudentService {
  async findById(id: string): Promise<StudentDTO> {}
  async create(dto: CreateStudentDTO): Promise<StudentDTO> {}
}

// DTO - 定义request/response格式
export class CreateStudentDTO {
  name: string;
  email: string;
  classId: string;
}

export class StudentDTO extends CreateStudentDTO {
  id: string;
  createdAt: Date;
  updatedAt: Date;
}
```

#### 前端 (React) 特定规范

**组件结构：**

```typescript
// ✅ 函数组件为主，配合Hooks
interface NetworkGraphProps {
  nodes: NodeData[];
  edges: EdgeData[];
  onNodeClick?: (nodeId: string) => void;
}

export const NetworkGraph: React.FC<NetworkGraphProps> = ({
  nodes,
  edges,
  onNodeClick,
}) => {
  const [selectedNode, setSelectedNode] = React.useState<string | null>(null);

  return (
    <div className="network-graph">
      {/* JSX */}
    </div>
  );
};
```

**服务层分离：**

```
services/
├── apiService.ts       # HTTP客户端 (fetch/axios)
├── dataService.ts      # 业务数据处理
├── dataParser.ts       # 数据解析与转换
├── dataValidator.ts    # 数据验证规则
├── strategies.ts       # 算法实现
└── performanceUtils.ts # 性能优化工具
```

### 代码格式化与检查

**自动格式化（必须在提交前运行）：**

```bash
# 使用 Prettier 格式化代码
pnpm format

# 或指定目录
pnpm format --write src/**/*.ts
```

**代码检查：**

```bash
# 后端 - 运行 ESLint 检查并自动修复
cd backend && pnpm lint

# 前端 - 运行 ESLint 检查并自动修复
cd frontend && pnpm lint

# 使用 Oxlint 高性能检查（可选）
oxlint
```

**配置文件优先级：**

1. `.eslintrc` / `.eslintrc.json` - ESLint 配置
2. `prettier.config.js` - Prettier 格式化配置
3. `oxlint.config.js` - Oxlint 快速检查配置
4. `tsconfig.json` - TypeScript 编译配置

### 数据库规范 (Prisma)

**模型定义原则：**

```prisma
// ✅ 模型名 - PascalCase（单数）
model Student {
  id        String    @id @default(cuid())
  name      String
  email     String    @unique
  classId   String
  class     Class     @relation(fields: [classId], references: [id])

  // 时间戳
  createdAt DateTime  @default(now())
  updatedAt DateTime  @updatedAt

  // 索引优化查询性能
  @@index([classId])
  @@index([email])  // 频繁查询的字段加索引
}
```

**数据库迁移流程：**

```bash
# 1. 修改 schema.prisma
# 2. 生成迁移文件
pnpm exec prisma migrate dev --name <migration_name>

# 3. 为新迁移编写种子数据（可选）
# 编辑 prisma/seed.ts

# 4. 执行种子数据
pnpm db:seed

# 5. 验证数据库（开发环境）
pnpm exec prisma studio
```

### 测试规范

**后端测试（Jest）：**

```typescript
// student.service.spec.ts
describe("StudentService", () => {
  let service: StudentService;
  let mockDb: jest.Mocked<DatabaseService>;

  beforeEach(() => {
    // 设置依赖注入和Mock
    mockDb = {
      student: { findUnique: jest.fn() },
    } as any;
    service = new StudentService(mockDb);
  });

  describe("findById", () => {
    it("应该返回指定ID的学生", async () => {
      const mockStudent = { id: "1", name: "Alice" };
      mockDb.student.findUnique.mockResolvedValue(mockStudent);

      const result = await service.findById("1");

      expect(result).toEqual(mockStudent);
      expect(mockDb.student.findUnique).toHaveBeenCalledWith({
        where: { id: "1" },
      });
    });
  });
});
```

**测试覆盖率目标：**

- 业务逻辑服务（Service）：≥ 70% 覆盖率
- 数据验证函数：≥ 90% 覆盖率
- 控制器路由逻辑：≥ 60% 覆盖率（可选）

**运行测试：**

```bash
# 运行所有测试
pnpm test

# 监视模式（开发时自动重新运行）
pnpm test:watch

# 生成覆盖率报告
pnpm test:cov

# 运行E2E测试（端到端）
cd .. && pnpm test:e2e
```

---

## 代码管理规范

### Git 工作流

**分支命名约定：**

```
main/                          # 生产环境分支（受保护）
├── develop                    # 开发主分支
│   ├── feature/student-import # 功能分支
│   ├── feature/graph-layout
│   ├── bugfix/node-sorting    # 修复分支
│   ├── refactor/db-schema     # 重构分支
│   └── docs/api-documentation # 文档分支
└── hotfix/data-validation     # 紧急修复 (基于main)
```

**分支命名规则：**

```
<type>/<scope>-<description>

type: feature(特性) | bugfix(修复) | refactor(重构) | docs(文档) | hotfix(紧急)
scope: 受影响模块 (student, teacher, graph, etc.)
description: 简短英文描述 (kebab-case)

示例：
✅ feature/student-import-excel
✅ bugfix/graph-layout-performance
✅ docs/api-authentication
❌ feature/新增学生导入功能 (中文)
❌ fix_bug (缺少scope)
```

### 提交规范

**Commit Message 格式：**

```
<type>(<scope>): <subject>

<body>

<footer>

@param type:
  feat:     新功能
  fix:      修复bug
  refactor: 代码重构（不修改功能）
  perf:     性能优化
  style:    格式调整（无逻辑改变）
  test:     测试相关
  docs:     文档更新
  chore:    构建、依赖更新

@param scope:
  可选，受影响的模块名 (student, teacher, graph, etc.)

@param subject:
  命令句态、现在时、第一人称
  长度 ≤ 50 字符
  首字母小写
  末尾无句号

示例提交消息：
```

feat(student): add batch import from excel

- Support .xlsx file upload
- Validate required fields before insertion
- Handle duplicate entries with merge strategy
- Add progress logging for large batches

Closes #42

```

```

**提交前检查清单：**

```bash
# 1. 格式化代码
pnpm format

# 2. 代码检查
pnpm lint

# 3. 运行测试
pnpm test

# 4. 分阶段提交（逻辑提交，而非一次性全部）
git add src/modules/student/student.service.ts
git commit -m "feat(student): add findById method"

# 5. 推送到远程
git push origin feature/student-import

# 6. 创建 Pull Request
# - 填写详细描述
# - 关联相关issue
# - 请求审查
```

### 代码审查流程

**审查者检查项：**

- [ ] 代码遵循项目规范
- [ ] 逻辑清晰，无明显缺陷
- [ ] 包含适当的测试
- [ ] 数据库变更包含迁移文件
- [ ] 文档更新（如适用）
- [ ] 提交信息清晰

**被审查者回应：**

```bash
# 修复审查意见后
git add .
git commit -m "refactor: address code review feedback"
git push

# 或追加提交并rebase
git rebase -i HEAD~2
# 选择 fixup 或 squash 来合并提交
```

---

## 开发环境配置

### 本地环境要求

**必需（JavaScript/Node.js）：**

```
Node.js: v18.0.0 或更高
pnpm: v8.0.0 或更高
```

**可选（Python脚本）：**

```
Python: 3.9 或更高
uv: 最新版本（虚拟环境管理）
```

**验证环境：**

```bash
node --version    # v18.x.x 或更高
pnpm --version    # 8.x.x 或更高
python --version  # 3.9+ (可选)
uv --version      # 最新版本 (可选)
```

### MacBook (M1 Pro) 特定配置

M1/M2/M3芯片的macOS通常已原生支持Node.js和Python。如遇到二进制兼容性问题：

```bash
# 确认当前架构
uname -m  # 应该输出 arm64

# 如果某些包需要编译，确保已安装Xcode命令行工具
xcode-select --install

# 如果需要使用Rosetta 2运行某些工具
arch -x86_64 pnpm install  # 强制使用x86_64架构
```

### IDE/编辑器推荐配置

**VS Code 推荐扩展：**

```json
{
  "recommendations": [
    "dbaeumer.vscode-eslint", // ESLint 实时检查
    "esbenp.prettier-vscode", // Prettier 格式化
    "prisma.prisma", // Prisma SQL语法高亮
    "typescript.typescript-react", // TypeScript支持
    "ms-vscode.vscode-typescript-next" // 最新TypeScript版本
  ]
}
```

**工作区设置 (.vscode/settings.json)：**

```json
{
  "editor.defaultFormatter": "esbenp.prettier-vscode",
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": true
  },
  "[typescript]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode",
    "editor.formatOnSave": true
  },
  "typescript.tsdk": "node_modules/typescript/lib",
  "typescript.enablePromptUseWorkspaceTsdk": true
}
```

### 环境变量配置

**后端 (.env 或 .env.local）：**

```env
# 数据库连接
DATABASE_URL="sqlserver://user:password@localhost:1433/InteractionNetworkDB"

# 应用配置
NODE_ENV="development"
PORT=3333

# 日志级别
LOG_LEVEL="debug"
```

**前端 (.env.local)：**

```env
VITE_API_URL=http://localhost:3333
VITE_ENV=development
```

### Docker 开发环境（可选）

```bash
# 启动必要的服务容器（如数据库）
docker-compose -f docker-compose.dev.yml up -d

# 查看日志
docker compose logs -f database

# 停止容器
docker compose down
```

---

## 常见开发任务

### 添加新API端点

**步骤：**

```typescript
// 1. 定义DTO (backend/src/modules/{feature}/{feature}.dto.ts)
export class CreateNodeDTO {
  @IsString()
  name: string;

  @IsEnum(["student", "teacher", "knowledge"])
  type: string;
}

// 2. 添加Service方法 ({feature}.service.ts)
@Injectable()
export class NodeService {
  async create(dto: CreateNodeDTO): Promise<NodeDTO> {
    return this.prisma.node.create({ data: dto });
  }
}

// 3. 添加Controller路由 ({feature}.controller.ts)
@Controller("nodes")
export class NodeController {
  constructor(private readonly nodeService: NodeService) {}

  @Post()
  @HttpCode(201)
  async create(@Body() dto: CreateNodeDTO): Promise<NodeDTO> {
    return this.nodeService.create(dto);
  }
}

// 4. 在Module中注册 ({feature}.module.ts)
@Module({
  controllers: [NodeController],
  providers: [NodeService],
})
export class NodeModule {}

// 5. 在main.ts中全局使用pipe等 (可选)
app.useGlobalPipes(new ValidationPipe());

// 6. 编写测试 ({feature}.spec.ts)
```

### 修改数据库模式

```bash
# 1. 编辑 prisma/schema.prisma
# 2. 生成迁移
pnpm exec prisma migrate dev --name add_teacher_rating_field

# 3. 更新相关 DTO 类型
# 4. 更新 test fixtures 数据
# 5. 提交 migrations/ 文件夹中的SQL文件
```

### 集成新数据源

```typescript
// 1. 创建数据适配器 (backend/src/shared/adapters/)
export class ExcelDataAdapter {
  parse(file: Buffer): Promise<StudentData[]> {
    const workbook = read(file);
    // 解析逻辑
  }
}

// 2. 在Service中使用
@Injectable()
export class DataMigrationService {
  constructor(private readonly excelAdapter: ExcelDataAdapter) {}

  async importStudents(file: Express.Multer.File): Promise<ImportResult> {
    const data = await this.excelAdapter.parse(file.buffer);
    // 插入数据库逻辑
  }
}

// 3. 暴露控制器端点
@Post('import/students')
async importStudents(@UploadedFile() file: Express.Multer.File) {
  return this.dataMigrationService.importStudents(file);
}
```

### 添加React组件并连接API

```typescript
// 1. 创建组件 (frontend/src/components/StudentList.tsx)
interface StudentListProps {
  classId: string;
}

export const StudentList: React.FC<StudentListProps> = ({ classId }) => {
  const [students, setStudents] = React.useState<StudentDTO[]>([]);
  const [loading, setLoading] = React.useState(true);

  React.useEffect(() => {
    // 2. 在服务中定义API调用
    apiService.getStudentsByClass(classId)
      .then(setStudents)
      .catch(handleError)
      .finally(() => setLoading(false));
  }, [classId]);

  return (
    <div>
      {loading ? <Spinner /> : <StudentGrid students={students} />}
    </div>
  );
};

// 3. apiService.ts
export const apiService = {
  async getStudentsByClass(classId: string): Promise<StudentDTO[]> {
    const response = await fetch(
      `${API_BASE_URL}/students?classId=${classId}`
    );
    if (!response.ok) throw new Error('Failed to fetch students');
    return response.json();
  },
};
```

### 性能测试与优化

```typescript
// 后端性能检测
import { performance } from "perf_hooks";

const startTime = performance.now();
await this.processLargeDataset();
const duration = performance.now() - startTime;
console.log(`Processing took ${duration.toFixed(2)}ms`);

// 前端性能优化
import { performanceUtils } from "../services/performanceUtils";

// 使用虚拟滚动处理大列表
const memoizedComponent = React.memo(StudentRow);

// 使用 useMemo 避免不必要的重新计算
const sortedStudents = React.useMemo(
  () => students.sort((a, b) => a.name.localeCompare(b.name)),
  [students],
);
```

---

## 故障排除

### 常见问题

**Q: 数据库连接失败**

```bash
# 1. 检查 DATABASE_URL 环境变量
echo $DATABASE_URL

# 2. 验证文件权限
ls -la .env

# 3. 重新生成 Prisma 客户端
pnpm exec prisma generate

# 4. 推送数据库更改
pnpm db:push --accept-data-loss
```

**Q: 依赖冲突**

```bash
# 清除锁定文件并重新安装
rm pnpm-lock.yaml
pnpm install
```

**Q: TypeScript 编译错误**

```bash
# 重新生成 Prisma 客户端（更新类型）
pnpm exec prisma generate

# 清除 dist 目录
rm -rf dist

# 重新构建
pnpm build
```

**Q: ESLint/Prettier 不工作**

```bash
# 重启 VS Code
# 或手动触发格式化
pnpm format
pnpm lint
```

**Q: 端口3000/3333报「已在使用」错误**

```bash
# 这通常表示开发服务已经在运行
# 前端直接访问即可，后端需要手动重启：
# 如果确实需要清理旧进程：

lsof -i :3333      # 查看占用3333端口的进程（后端）
lsof -i :3000      # 查看占用3000端口的进程（前端）
kill -9 <PID>      # 终止进程

# 清理所有Node进程（谨慎）
killall node
```

**Q: Python虚拟环境找不到依赖**

```bash
# 确保虚拟环境已激活
source .venv/bin/activate  # macOS/Linux

# 验证环境
which python

# 重新安装依赖
uv pip install -r requirements.txt

# ⚠️ 不要重复创建虚拟环境！
# 检查现有虚拟环境
ls -la | grep venv
```

---

## 推荐阅读

- [NestJS 官方文档](https://docs.nestjs.com/)
- [Prisma ORM 指南](https://www.prisma.io/docs/)
- [React 最佳实践](https://react.dev)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- 项目专属文档：`documents/` 目录

---

**最后更新：** 2026年3月
**维护者：** 团队开发成员
