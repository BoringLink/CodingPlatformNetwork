#!/bin/bash
# Project Development Environment Setup Script
# 项目开发环境初始化脚本
# 使用: bash setup.sh

set -e  # 遇到错误立即退出

echo "🚀 交互网络可视化系统 - 开发环境初始化"
echo "================================================"

# 检查 Node.js 版本
echo "✓ 检查 Node.js 版本..."
NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 18 ]; then
  echo "❌ Node.js 版本过低 (需要 v18+)，当前: $(node -v)"
  exit 1
fi
echo "✓ Node.js 版本: $(node -v)"

# macOS M1 检测（仅提示）
echo ""
echo "✓ 检查系统架构..."
ARCH=$(uname -m)
if [ "$ARCH" = "arm64" ]; then
  echo "✓ 检测到 Apple Silicon (M1/M2/M3) - 已原生支持"
fi

# 检查 pnpm
echo ""
echo "✓ 检查 pnpm..."
if ! command -v pnpm &> /dev/null; then
  echo "❌ 未找到 pnpm，安装中..."
  npm install -g pnpm
fi
echo "✓ pnpm 版本: $(pnpm --version)"

# 检查或创建 Python 虚拟环境（可选）
echo ""
echo "✓ 检查 Python 虚拟环境..."
if [ -d ".venv" ]; then
  echo "✓ 虚拟环境已存在"
else
  # 检查 Python 和 uv 是否可用
  if command -v python3 &> /dev/null && command -v uv &> /dev/null; then
    echo "ⓘ 创建 Python 虚拟环境..."
    uv venv
    echo "✓ 虚拟环境已创建"
    echo "⚠️  若有 Python 脚本，请运行: source .venv/bin/activate"
  elif command -v python3 &> /dev/null; then
    echo "⚠️  检测到 Python，但未安装 uv"
    echo "    若需使用 Python，请运行: pip install uv && uv venv"
  else
    echo "ⓘ 可选: 未检测到 Python 或 uv (项目不需要时可忽略)"
  fi
fi

# 安装根依赖
echo ""
echo "✓ 安装根依赖..."
pnpm install

# 安装后端依赖
echo ""
echo "✓ 安装后端依赖..."
cd backend
pnpm install
pnpm exec prisma generate  # 生成Prisma客户端
echo "✓ 后端依赖已安装"

# 检查并初始化 .env.example
if [ ! -f ".env" ] && [ -f ".env.example" ]; then
  echo "ⓘ 从 .env.example 创建 .env..."
  cp .env.example .env
  echo "⚠️  请更新 .env 中的数据库连接字符串"
fi

cd ..

# 安装前端依赖
echo ""
echo "✓ 安装前端依赖..."
cd frontend
pnpm install
echo "✓ 前端依赖已安装"

# 检查 .env.local
if [ ! -f ".env.local" ]; then
  echo "ⓘ 创建前端环境变量文件..."
  cat > .env.local << EOF
VITE_API_URL=http://localhost:3333
VITE_ENV=development
EOF
  echo "✓ .env.local 已创建"
fi

cd ..

# 数据库初始化提示
echo ""
echo "================================================"
echo "💾 数据库设置"
echo "================================================"
echo "1. 确保数据库服务已启动"
echo "2. 更新 backend/.env 的 DATABASE_URL"
echo "3. 运行: pnpm db:push"
echo "4. （可选）运行: pnpm db:seed 初始化示例数据"

# 启动提示
echo ""
echo "================================================"
echo "🎯 启动开发服务器"
echo "================================================"
echo ""
echo "打开两个终端，分别运行:"
echo ""
if [ -d ".venv" ]; then
  echo "✓ 如果使用 Python 脚本，先激活虚拟环境:"
  echo "  source .venv/bin/activate"
  echo ""
fi
echo "终端1 - 后端服务 (端口 3333):"
echo "  cd backend && pnpm start:dev"
echo ""
echo "终端2 - 前端服务 (端口 3000):"
echo "  cd frontend && pnpm dev"
echo ""
echo "💡 关键提示:"
echo "  • 前端 (React + Vite) 支持热重载，修改文件自动刷新"
echo "  • 后端 (Nest.js + Prisma) 不支持热重载，修改后按 Ctrl+C 然后重新运行"
echo "  • Python 虚拟环境只需创建一次，每次执行脚本前激活"
echo ""
echo "🌐 访问地址:"
echo "  后端 API:   http://localhost:3333"
echo "  前端应用:   http://localhost:3000"
echo ""
echo "✓ 初始化完成！"
echo "📖 更多信息请查看 .github/skills/project-development/SKILL.md"
