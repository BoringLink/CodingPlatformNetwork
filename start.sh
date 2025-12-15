#!/bin/bash

echo "=========================================="
echo "教育知识图谱系统 - 快速启动脚本"
echo "=========================================="
echo ""

# 检查 .env 文件
if [ ! -f .env ]; then
    echo "⚠️  未找到 .env 文件，正在从 .env.example 创建..."
    cp .env.example .env
    echo "✅ .env 文件已创建"
    echo "⚠️  请编辑 .env 文件并设置 OPENAI_API_KEY"
    echo ""
fi

# 检查 Docker
if ! command -v docker &> /dev/null; then
    echo "❌ 未安装 Docker，请先安装 Docker"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ 未安装 Docker Compose，请先安装 Docker Compose"
    exit 1
fi

echo "✅ Docker 环境检查通过"
echo ""

# 启动服务
echo "🚀 正在启动所有服务..."
docker-compose up -d

echo ""
echo "=========================================="
echo "✅ 服务启动成功！"
echo "=========================================="
echo ""
echo "访问地址："
echo "  - 前端应用: http://localhost:3000"
echo "  - 后端 API: http://localhost:8000"
echo "  - API 文档: http://localhost:8000/docs"
echo "  - Neo4j Browser: http://localhost:7474 (用户名: neo4j, 密码: password)"
echo "  - Flower 监控: http://localhost:5555"
echo ""
echo "查看日志："
echo "  docker-compose logs -f"
echo ""
echo "停止服务："
echo "  docker-compose down"
echo ""
