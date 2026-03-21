# 项目开发Skill使用指南

## 📋 Skill概览

**名称**: `project-development`
**位置**: `.github/skills/project-development/`
**用途**: 为交互网络可视化项目提供统一的开发规范、工作流和最佳实践
**触发方式**: 在VS Code中输入 `/project-development` 或相关关键词

## 📁 包含资源

```
.github/skills/project-development/
├── SKILL.md                 # 主要文档（完整规范）
├── quick-reference.md       # 快速参考卡
├── git-workflow.md          # Git工作流详解
├── setup.sh                 # 开发环境初始化脚本
└── README.md               # 本文件
```

### 各文件用途

| 文件                 | 用途         | 适合场景                                     |
| -------------------- | ------------ | -------------------------------------------- |
| `SKILL.md`           | 完整开发规范 | 项目架构、代码规范、环保境配置、常见开发任务 |
| `quick-reference.md` | 快速速查表   | 忘记命令、快速查找常用操作                   |
| `git-workflow.md`    | Git详细指南  | Git分支管理、团队协作、提交规范              |
| `setup.sh`           | 自动化初始化 | 新成员第一次设置开发环境                     |

## 🚀 快速开始

### 💻 系统要求

**必需：**

- Node.js v24
- pnpm v8+
- macOS/Linux/Windows (推荐 MacBook M1/M2/M3)

**可选：**

- Python 3.9+（如果项目有Python脚本）
- uv（Python虚拟环境管理器）

### 新成员入职

```bash
# 1. 克隆仓库
git clone <repo-url>
cd 交互网络可视化

# 2. 运行初始化脚本（自动检测和配置所有依赖）
bash .github/skills/project-development/setup.sh

# 3. 按照脚本提示完成配置
# 数据库连接 → 激活Python虚拟环境(如需要) → 启动开发服务

# 4. 激活Python虚拟环境（仅在需要执行Python脚本时）
source .venv/bin/activate  # macOS/Linux
```

### 重要注意事项⚠️

1. **虚拟环境**
   - ✅ 第一次设置时运行 `uv venv` 创建虚拟环境
   - ✅ 每次执行Python脚本前运行 `source .venv/bin/activate`
   - ❌ 不要重复创建虚拟环境
   - ❌ 不要将虚拟环境提交到Git

2. **热重载**
   - 前端 (React + Vite): 支持热重载，修改文件后浏览器会自动刷新
   - 后端 (Nest.js + Prisma): 不支持热重载，修改文件后需要手动重启服务

3. **端口冲突**
   - 如果看到"端口3000/3333已占用"错误
   - 这表示开发服务已在后台运行
   - 直接访问 http://localhost:3333 (后端) 和 http://localhost:3000 (前端)
   - 不需要重新启动服务

4. **MacBook M1+**
   - 已原生支持，无需特殊配置
   - 如遇到二进制兼容性问题，实现器会自动处理

### 开发流程

1. **查看项目结构** → `SKILL.md` 的"目录结构详解"部分
2. **了解代码规范** → `SKILL.md` 的"开发规范"部分
3. **快速查命令** → `quick-reference.md`
4. **Git操作** → 查看 `git-workflow.md`

### 遇到问题

```
问题: 不知道某个目录的用途
→ 查看 SKILL.md 的"目录结构详解"

问题: 忘记项目启动命令
→ 查看 quick-reference.md 或 SKILL.md 的"快速启动"

问题: Git提交和分支管理
→ 查看 git-workflow.md

问题: ESLint报错、类型错误
→ 查看 SKILL.md 的"故障排除"
```

## 🔑 核心规范速览

### 分支命名

```
feature/student-import
bugfix/graph-layout-performance
refactor/db-schema
docs/api-authentication
hotfix/critical-bug
```

### 提交消息

```
feat(student): add excel import functionality
fix(graph): resolve infinite loop in layout algorithm
docs(api): update authentication endpoints
```

### 代码检查 (开发前执行)

```bash
pnpm format      # 自动格式化
pnpm lint        # 代码检查
pnpm test        # 单元测试
```

### 项目启动 (两个终端)

```bash
# 如需要，先激活Python虚拟环境
source .venv/bin/activate

# 终端1: 后端服务 (端口3333)
cd backend && pnpm start:dev

# 终端2: 前端服务 (端口3000)
cd frontend && pnpm dev

# 💡 关键提示:
# - 前端支持热重载，修改文件立即生效
# - 后端不支持热重载：需要手动重启（在控制台按 Ctrl+C 然后重新运行）
# - 访问: http://localhost:3333 (后端) 和 http://localhost:3000 (前端)
```

## 💡 使用建议

### 对于新开发者

1. 首先阅读 `SKILL.md` 的"快速启动"和"目录结构"
2. 跑一遍本地开发环境设置
3. 熟悉项目的目录布局
4. 阅读相关模块的现有代码
5. 开始第一个小改动，体验完整流程

### 对于代码审查者

- 参考 `SKILL.md` 的"代码规范"部分检查代码
- 使用 `git-workflow.md` 的"代码审查流程"
- 确保提交消息符合规范

### 对于DevOps/部署

- 查看 `SKILL.md` 的"开发环境配置"部分
- 了解 `.env` 和配置文件位置
- 参考数据库迁移章节

## 🔄 维护和更新

### 何时更新本skill

当以下情况发生时：

- [ ] 项目目录结构有重大变化
- [ ] 开发规范有更新
- [ ] 新增必做的开发工具/流程
- [ ] 团队对Git工作流的共识有变化

### 如何更新

```bash
# 1. 编辑相应文件
vim .github/skills/project-development/SKILL.md

# 2. 变更应该通过PR审核进行
git checkout -b docs/update-development-skill
git add .github/skills/project-development/
git commit -m "docs: update development guidelines for new feature"
git push origin docs/update-development-skill

# 3. 在PR中说明变更原因
```

## 📞 获取帮助

### 常见问题

**Q: 我不确定是应该用 `feature` 还是 `refactor` 分支？**
A:

- 如果是新功能或新模块 → `feature/`
- 如果是改进现有代码但不改变功能 → `refactor/`
- 如果是修复bug → `bugfix/`

**Q: PR被要求改进，我应该怎样提交修改？**
A: 查看 `git-workflow.md` 的"处理代码审查反馈"部分

**Q: 数据库连接失败？**
A: 查看 `SKILL.md` 的"故障排除"部分或 `quick-reference.md` 的表格

## 📈 项目结构回顾

```
交互网络可视化系统
├── Monorepo (根目录统一管理)
├── Backend (NestJS + Prisma + TypeScript)
│   ├── 8 大功能模块
│   ├── 共享layer (config, utils, types)
│   └── 数据库 (SQL Server via Prisma)
├── Frontend (React + Vite + TypeScript)
│   ├── D3.js 可视化
│   ├ ├─ 数据处理服务
│   └── REST API 调用
└── Monorepo工具链 (pnpm, linting, testing)
```

## 🎯 下次更新计划

- [ ] 添加API文档链接（Swagger/OpenAPI）
- [ ] 创建常见bug修复案例库
- [ ] 添加性能基准测试文档
- [ ] 建立架构决策记录（ADR）

---

**版本**: 1.0  
**最后更新**: 2026年3月19日  
**维护者**: 团队开发成员
