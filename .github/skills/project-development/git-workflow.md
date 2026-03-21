# Git 工作流程完整指南

## 分支模型: Git Flow

我们采用 **Git Flow** 模型，这是一个稳健的团队协作方案。

```
┌─────────────────────────────────────────────────────────────┐
│                      main (生产)                             │
│                   ↑         ↓                                │
├─────────────────────────────────────────────────────────────┤
│                    develop (开发)                             │
│                   ↑    ↑              ↓↓ ↓                   │
├──feature/X──┬──bugfix/X──┬──refactor/X───┬release/1.0──┤
│             │            │                │              │
│      (功能开发)  (bug修复)  (代码重构)    (准备发布)       │
└─────────────────────────────────────────────────────────────┘
```

## 1. 创建功能分支

适用于: 新功能、新模块的开发

```bash
# 从 develop 创建功能分支
git checkout develop
git pull origin develop
git checkout -b feature/student-excel-import

# 确保分支名清晰表达功能
feature/student-excel-import  ✅
feature/graph-layout          ✅
feature/stu_import            ❌ (不够清晰)
feature/new_stuff             ❌ (太模糊)
```

## 2. 本地开发与提交

```bash
# 查看你的改动
git status                    # 检查修改的文件
git diff                      # 查看具体改动

# 分段提交（逻辑清晰）
git add backend/src/modules/student/student.service.ts
git commit -m "feat(student): add excel parsing logic"

git add backend/src/modules/student/student.controller.ts
git commit -m "feat(student): expose POST /students/import endpoint"

git add backend/prisma/schema.prisma
git commit -m "refactor: normalize student table schema"

# 不要一次性提交所有更改！
git add .
git commit -m "updated" ❌

# 查看本地提交历史
git log --oneline --graph
```

### 提交信息模板

```
<type>(<scope>): <subject>

<body>

<footer>

示例：

feat(student): implement excel import with validation

- Parse .xlsx format with xlsx library
- Validate email and phone format before insertion
- Handle duplicate entries with skip strategy
- Log import stats (processed, skipped, failed)

Closes #123
Co-authored-by: Alice <alice@example.com>
```

**Type 列表：**

- `feat`: 新功能
- `fix`: 修复bug
- `refactor`: 代码重构
- `perf`: 性能优化
- `style`: 代码格式（无逻辑改变）
- `test`: 测试相关
- `docs`: 文档更新
- `chore`: 构建、依赖更新

## 3. 推送和创建 Pull Request

```bash
# 推送到远程
git push origin feature/student-excel-import

# GitHub 会自动显示创建 PR 的链接
# 或在 GitHub web 上手动创建

# PR 描述模板：
"""
## 描述
简述这个 PR 做了什么

## 改动列表
- [ ] 添加学生导入服务
- [ ] 实现 DTO 验证
- [ ] 编写单元测试

## 相关 Issues
Closes #123

## 测试
- [ ] 本地测试成功
- [ ] 通过所有 linting 检查
- [ ] 测试覆盖率 > 70%

## 截图/视频（如适用）
[请附加截图]

@reviewer 请审查
"""
```

## 4. 处理代码审查反馈

```bash
# 修复审查意见
# 1. 编辑文件
vim src/file.ts

# 2. 格式化和检查
pnpm format
pnpm lint

# 3. 提交修改
git add src/file.ts
git commit -m "refactor: address code review feedback on validation"

# 4. 推送（无需创建新分支）
git push origin feature/student-excel-import

# PR 会自动更新
```

## 5. 合并到 Develop

```bash
# PR 批准后，在 GitHub 上合并 (使用 Squash Merge 保持主线清晰)
# Squash Merge: 将所有提交合并为一个

# 或本地合并
git checkout develop
git pull origin develop
git merge feature/student-excel-import
git push origin develop

# 删除已合并的分支
git branch -d feature/student-excel-import
git push origin --delete feature/student-excel-import
```

## 6. 发布流程 (Release)

```bash
# 当 develop 准备好发布时
git checkout -b release/1.0.0 develop

# 在release分支上：
# 1. 更新版本号
# 2. 更新 CHANGELOG
# 3. 最后的测试和修复

# 完成release
git checkout main
git merge --no-ff release/1.0.0
git tag -a v1.0.0 -m "Release version 1.0.0"

# 也合并回develop（防止版本差异）
git checkout develop
git merge --no-ff release/1.0.0

# 删除release分支
git branch -d release/1.0.0
git push origin develop main --tags
```

## 7. 紧急修复 (Hotfix)

```bash
# 生产环境发现bug
git checkout -b hotfix/critical-data-loss main

# 修复bug
# 编辑、测试

# 提交修复
git commit -m "fix: prevent data loss in deletion endpoint"

# 完成hotfix
git checkout main
git merge --no-ff hotfix/critical-data-loss
git tag -a v1.0.1 -m "Hotfix for data loss"

# 也合并回develop和release
git checkout develop
git merge --no-ff hotfix/critical-data-loss

# 清理
git branch -d hotfix/critical-data-loss
git push origin main develop --tags
```

## 常见任务

### 更新你的分支

```bash
# 当远程develop有新提交时
git fetch origin
git rebase origin/develop

# 如果有冲突
git rebase --abort           # 取消rebase
# 或
git add .
git rebase --continue        # 解决冲突后继续
```

### 压缩多个提交

```bash
# 假设你有3个提交，想要压缩为1个
git rebase -i HEAD~3

# 交互式编辑器会出现：
# pick abc1234 feat: add feature
# pick def5678 refactor: fix style issues
# pick ghi9012 test: add unit tests

# 改为：
# pick abc1234 feat: add feature
# squash def5678 refactor: fix style issues
# squash ghi9012 test: add unit tests

# 保存并编辑新的提交信息
```

### 撤销不小心的提交

```bash
# 撤销最后一个提交（保留改动）
git reset --soft HEAD~1

# 撤销提交及改动
git reset --hard HEAD~1

# 撤销已推送的提交（创建反向提交）
git revert HEAD
git push origin feature/my-branch
```

### 查看提交历史

```bash
# 简洁日志
git log --oneline --decorate --graph --all

# 指定日期范围
git log --since="2 weeks ago" --until="now"

# 指定作者
git log --author="Alice"

# 搜索提交消息
git log --grep="student" -i
```

## 团队协议

| 规则     | 要求                                  |
| -------- | ------------------------------------- |
| 分支命名 | `type/scope-description`              |
| 提交消息 | 遵循 Conventional Commits             |
| PR 审查  | 至少1个 Approve                       |
| 合并策略 | 使用 Squash Merge（功能分支）         |
| 提交前   | 必须运行 `pnpm format` 和 `pnpm lint` |
| 测试     | 功能分支必须包含单元测试              |
| 文档     | 新API必须更新文档                     |

## 故障排查

### 问题: "Your branch is behind origin/develop"

```bash
git fetch origin
git rebase origin/develop
# 或
git pull origin develop --rebase
```

### 问题: 不小心在 main 分支开发

```bash
git checkout -b feature/my-feature    # 现在在新分支
git checkout main
git reset --hard origin/main          # 重置main
```

### 问题: 想修改已提交的消息

```bash
# 修改最后一个提交
git commit --amend -m "新的提交消息"

# 修改之前的提交（高级）
git rebase -i HEAD~3
# 选择 reword，编辑消息
```

### 问题: 想要放弃所有本地改动

```bash
git reset --hard HEAD
git clean -fd  # 删除未跟踪的文件
```

---

## 相关文档

- [Git 官方文档](https://git-scm.com/doc)
- [GitHub Flow 指南](https://guides.github.com/introduction/flow/)
- [Conventional Commits](https://www.conventionalcommits.org/)
