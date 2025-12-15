#!/usr/bin/env python
"""Celery Worker启动脚本

启动Celery worker进程处理异步任务
"""

import sys
from app.celery_app import celery_app

if __name__ == "__main__":
    # 启动worker
    # 使用命令行参数，例如：
    # python celery_worker.py worker --loglevel=info --queues=data_import,llm_analysis
    celery_app.start(sys.argv[1:])
