# 快速参考卡 (Cheatsheet)

## 常用命令一览

### 项目初始化和启动

```bash
# 第一次克隆后
pnpm install
cd backend && pnpm install && cd ..
cd frontend && pnpm install && cd ..

# 🐍 Python 虚拟环境（如果项目有Python脚本）
# 检查是否已有虚拟环境
ls -la | grep venv
# 如果没有，创建虚拟环境
uv venv
# 激活虚拟环境
source .venv/bin/activate

# 启动完整开发环境
# 终端1 - 后端（端口3333）
cd backend && pnpm start:dev

# 终端2 - 前端（端口3000）
cd frontend && pnpm dev

# ℹ️ 热重载说明
# - 前端 (React + Vite) 支持热重载，修改文件自动刷新
# - 后端 (Nest.js + Prisma) 不支持热重载，修改后需要按 Ctrl+C 停止，然后重新运行
# - 如果遇到"端口3000/3333已占用"，说明服务已在后台运行
#   前端直接访问 http://localhost:3000；后端需要手动重启

# 启动生产构建
cd backend && pnpm build && pnpm start:prod
cd frontend && pnpm build && pnpm start
```

### 代码质量检查

```bash
# 格式化所有代码
pnpm format

# 代码检查（修复）
pnpm lint

# 后端代码检查
cd backend && pnpm lint

# 前端代码检查
cd frontend && pnpm lint
```

### 测试

```bash
# 运行所有测试
pnpm test

# 监视模式
pnpm test:watch

# 覆盖率报告
pnpm test:cov

# E2E测试
pnpm test:e2e

# 后端特定
cd backend && pnpm test:debug
```

### 数据库操作

```bash
# 应用最新迁移
pnpm db:push

# 创建新迁移
pnpm exec prisma migrate dev --name <name>

# 执行种子数据
pnpm db:seed

# 打开数据库UI
pnpm exec prisma studio

# 重置数据库（开发用）
pnpm exec prisma migrate reset
```

### Git 工作流

```bash
# 创建特性分支
git checkout -b feature/student-import

# 查看本地更改
git status
git diff

# 分阶段提交
git add src/modules/student/*.ts
git commit -m "feat(student): add import service"

# 推送
git push origin feature/student-import

# 拉取最新代码
git pull origin develop

# 回滚更改
git restore <file>           # 单个文件
git reset HEAD~1             # 回滚上一个提交
```

---

## 文件快速导航

| 任务         | 文件                                                   |
| ------------ | ------------------------------------------------------ |
| 添加学生API  | `backend/src/modules/student/`                         |
| 修改数据库   | `backend/prisma/schema.prisma`                         |
| 修改UI组件   | `frontend/src/components/`                             |
| 后端业务逻辑 | `backend/src/modules/{feature}/`                       |
| 前端服务集成 | `frontend/src/services/`                               |
| 项目配置     | `package.json` (根目录)                                |
| 环境变量     | `.env.local`                                           |
| 类型定义     | `frontend/src/types.ts` 或 `backend/src/shared/types/` |

---

## 常见错误排查

| 错误                      | 解决                                                                      |
| ------------------------- | ------------------------------------------------------------------------- | ------------------------------------------ |
| `pnpm: command not found` | `npm install -g pnpm`                                                     |
| 数据库连接失败            | 检查 `.env` 的 `DATABASE_URL`                                             |
| TypeScript编译错误        | `pnpm exec prisma generate`                                               |
| **端口3000/3333已占用**   | ✅ 前端支持热重载，直接访问即可                                           | ⚠️ 后端需要手动重启 (Ctrl+C, 然后重新运行) |
| 模块找不到                | `rm -rf node_modules pnpm-lock.yaml && pnpm install`                      |
| **Python虚拟环境问题**    | 执行前先 `source .venv/bin/activate`，检查 `which python` 指向 `.venv`    |
| **Python找不到模块**      | 不要重新创建虚拟环境，确保激活后运行 `uv pip install -r requirements.txt` |
| npm/pnpm混用冲突          | 统一使用 `pnpm`，删除 `package-lock.json` 和 `node_modules`               |

### 关键提示

⚠️ **虚拟环境**

- 执行Python脚本前必须检查虚拟环境状态
- 不要每次都重新创建虚拟环境（`uv venv` 仅需执行一次）
- 激活命令：`source .venv/bin/activate`

⚠️ **热重载**

- 前端 (React + Vite): 支持热重载，修改代码后等待编译完成，浏览器自动刷新
- 后端 (Nest.js + Prisma): 不支持热重载，修改代码后需要在终端按 Ctrl+C，然后重新运行
- 如果前端热重载失败，检查浏览器控制台是否有编译错误

---

## VS Code 快捷键提示

```
Cmd+Shift+P          # 打开命令面板 -> "Format Document"
Cmd+S                # 自动格式化（已配置保存时）
Cmd+K Cmd+X          # 删除末尾空格
Cmd+Shift+F          # 全文件夹搜索
Cmd+F                # 文件内搜索
Cmd+/                # 单行注释
Cmd+Shift+/          # 多行注释
```

---

## 性能优化提示

**后端：**

- 使用 Prisma select 只查询需要的字段
- 添加数据库索引到频繁查询的字段
- 使用 `.skip().take()` 实现分页

**前端：**

- 使用 `React.memo()` 避免不必要渲染
- 使用 `useMemo()` 和 `useCallback()` 优化计算
- 虚拟滚动处理大列表（> 1000 项）
- 延迟加载（code splitting）组件
