#!/bin/bash
# Flower监控启动脚本
#
# Flower是Celery的实时监控工具，提供Web界面查看：
# - 任务状态和历史
# - Worker状态
# - 任务统计
# - 速率图表

# 设置环境变量
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# 启动Flower
# -A: 指定Celery应用
# --port: Web界面端口
# --broker: 消息代理URL
# --basic_auth: 基本认证（用户名:密码）

celery -A app.celery_app flower \
    --port=5555 \
    --broker="${CELERY_BROKER_URL:-redis://localhost:6379/0}" \
    --basic_auth="${FLOWER_USER:-admin}:${FLOWER_PASSWORD:-admin}"
