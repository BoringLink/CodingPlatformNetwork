#!/bin/bash
# Celery Worker启动脚本

# 设置环境变量
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# 启动Celery worker
# -A: 指定Celery应用
# --loglevel: 日志级别
# --queues: 监听的队列
# --concurrency: 并发worker数量
# --max-tasks-per-child: 每个worker子进程最多处理的任务数

celery -A app.celery_app worker \
    --loglevel=info \
    --queues=data_import,llm_analysis \
    --concurrency=4 \
    --max-tasks-per-child=1000 \
    --time-limit=3600 \
    --soft-time-limit=3300
