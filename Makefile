.PHONY: help install dev up down logs clean test backend-test frontend-test celery-worker celery-flower celery-status celery-purge test-celery

help:
	@echo "教育知识图谱系统 - 开发命令"
	@echo ""
	@echo "make install       - 安装所有依赖"
	@echo "make dev          - 启动开发环境"
	@echo "make up           - 启动所有服务（后台）"
	@echo "make down         - 停止所有服务"
	@echo "make logs         - 查看服务日志"
	@echo "make clean        - 清理所有容器和数据卷"
	@echo "make test         - 运行所有测试"
	@echo "make backend-test - 运行后端测试"
	@echo "make frontend-test - 运行前端测试"
	@echo ""
	@echo "Celery任务队列命令："
	@echo "make celery-worker - 启动Celery Worker"
	@echo "make celery-flower - 启动Flower监控"
	@echo "make celery-status - 查看Celery状态"
	@echo "make celery-purge  - 清空任务队列"
	@echo "make test-celery   - 测试Celery集成"

install:
	@echo "安装后端依赖..."
	cd backend && pip install -e ".[dev]"
	@echo "安装前端依赖..."
	cd frontend && npm install
	@echo "依赖安装完成！"

dev:
	@echo "启动开发环境..."
	docker-compose up

up:
	@echo "启动所有服务（后台）..."
	docker-compose up -d

down:
	@echo "停止所有服务..."
	docker-compose down

logs:
	docker-compose logs -f

clean:
	@echo "清理所有容器和数据卷..."
	docker-compose down -v
	@echo "清理完成！"

test: backend-test frontend-test

backend-test:
	@echo "运行后端测试..."
	cd backend && pytest

frontend-test:
	@echo "运行前端测试..."
	cd frontend && npm test

celery-worker:
	@echo "启动Celery Worker..."
	cd backend && ./start_celery_worker.sh

celery-flower:
	@echo "启动Flower监控..."
	@echo "访问 http://localhost:5555 查看监控界面"
	cd backend && ./start_flower.sh

celery-status:
	@echo "查看Celery状态..."
	cd backend && celery -A app.celery_app inspect active
	@echo ""
	@echo "已注册的任务："
	cd backend && celery -A app.celery_app inspect registered

celery-purge:
	@echo "清空任务队列..."
	cd backend && celery -A app.celery_app purge -f

test-celery:
	@echo "测试Celery集成..."
	cd backend && python test_celery_integration.py
