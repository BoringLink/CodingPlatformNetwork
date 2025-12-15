# 教育知识图谱神经网络系统 - 后端

基于 FastAPI 的后端服务，用于构建和管理教育知识图谱。

## 技术栈

- Python 3.12+
- FastAPI 0.110+
- Neo4j 5.15+
- Redis 7.2
- Celery 5.3+
- OpenAI API

## 开发环境设置

1. 安装依赖：
```bash
pip install -e ".[dev]"
```

2. 启动服务：
```bash
uvicorn app.main:app --reload
```

3. 运行测试：
```bash
pytest
```

## 项目结构

```
backend/
├── app/
│   ├── main.py           # FastAPI 应用入口
│   ├── config.py         # 配置管理
│   ├── models/           # 数据模型
│   ├── services/         # 业务逻辑服务
│   ├── routers/          # API 路由
│   └── utils/            # 工具函数
├── tests/                # 测试文件
├── pyproject.toml        # 项目配置
└── README.md
```
