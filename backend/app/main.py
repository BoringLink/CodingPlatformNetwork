"""FastAPI 应用入口"""

import structlog
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time

from app.config import settings
from app.utils.logging import configure_logging
from app.database import init_database, close_database
from app.services.cache_service import cache_service, get_cache_service
from app.services.llm_service import llm_service, get_llm_service

# 配置结构化日志
configure_logging()
logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    from app.utils.audit_log import audit_log, OperationType

    # 启动时执行
    logger.info("application_starting", app_name=settings.app_name, version="0.1.0")

    # 记录系统启动事件
    audit_log.log_system_event(
        event_type=OperationType.SYSTEM_START,
        details={
            "app_name": settings.app_name,
            "version": "0.1.0",
            "environment": settings.environment,
            "debug": settings.debug,
        },
    )

    # 初始化数据库连接
    try:
        await init_database()
        logger.info("database_initialized")
    except Exception as e:
        logger.error("database_initialization_failed", error=str(e))
        audit_log.log_system_event(
            event_type=OperationType.SYSTEM_ERROR,
            details={"component": "database"},
            error_message=str(e),
        )
        raise

    # 初始化缓存服务
    try:
        from app.services.cache_service import CacheService

        global cache_service
        cache_service = CacheService()
        await cache_service.connect()
        logger.info("cache_service_initialized")
    except Exception as e:
        logger.error("cache_service_initialization_failed", error=str(e))
        audit_log.log_system_event(
            event_type=OperationType.SYSTEM_ERROR,
            details={"component": "cache"},
            error_message=str(e),
        )
        # 缓存服务失败不应该阻止应用启动
        cache_service = None

    # 初始化LLM服务
    try:
        from app.services.llm_service import LLMAnalysisService

        global llm_service
        llm_service = LLMAnalysisService(cache_service=cache_service)
        logger.info("llm_service_initialized")
    except Exception as e:
        logger.error("llm_service_initialization_failed", error=str(e))
        audit_log.log_system_event(
            event_type=OperationType.SYSTEM_ERROR,
            details={"component": "llm"},
            error_message=str(e),
        )
        raise

    yield

    # 关闭时执行
    logger.info("application_shutting_down")

    # 记录系统关闭事件
    audit_log.log_system_event(
        event_type=OperationType.SYSTEM_SHUTDOWN,
        details={
            "app_name": settings.app_name,
        },
    )

    # 关闭缓存服务
    if cache_service is not None:
        await cache_service.close()

    # 关闭数据库连接
    await close_database()


app = FastAPI(
    title="教育知识图谱神经网络系统",
    description="基于 LLM 和图数据库的教育数据分析平台",
    version="0.1.0",
    lifespan=lifespan,
)


# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    """请求日志中间件"""
    start_time = time.time()

    # 记录请求
    logger.info(
        "request_started",
        method=request.method,
        path=request.url.path,
        client_host=request.client.host if request.client else None,
    )

    try:
        response = await call_next(request)

        # 记录响应
        process_time = time.time() - start_time
        logger.info(
            "request_completed",
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            process_time=f"{process_time:.3f}s",
        )

        # 添加处理时间到响应头
        response.headers["X-Process-Time"] = str(process_time)
        return response

    except Exception as exc:
        process_time = time.time() - start_time
        logger.error(
            "request_failed",
            method=request.method,
            path=request.url.path,
            error=str(exc),
            process_time=f"{process_time:.3f}s",
        )
        raise


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """全局异常处理器"""
    import traceback
    from app.utils.exceptions import (
        BaseAppException,
        DataValidationError,
        NodeNotFoundError,
        RelationshipNotFoundError,
        DatabaseConnectionError,
        LLMServiceError,
    )

    # 获取堆栈跟踪
    stack_trace = traceback.format_exc()

    # 记录详细错误信息
    logger.error(
        "unhandled_exception",
        method=request.method,
        path=request.url.path,
        error=str(exc),
        error_type=type(exc).__name__,
        stack_trace=stack_trace if settings.debug else None,
    )

    # 根据异常类型返回不同的HTTP状态码
    status_code = 500

    if isinstance(exc, (NodeNotFoundError, RelationshipNotFoundError)):
        status_code = 404
    elif isinstance(exc, DataValidationError):
        status_code = 400
    elif isinstance(exc, DatabaseConnectionError):
        status_code = 503
    elif isinstance(exc, LLMServiceError):
        status_code = 503

    # 如果是自定义异常，返回详细信息
    if isinstance(exc, BaseAppException):
        return JSONResponse(
            status_code=status_code,
            content={
                "error": exc.__class__.__name__,
                "message": exc.message,
                "error_code": exc.error_code,
                "details": exc.details if settings.debug else {},
            },
        )

    # 其他异常返回通用错误
    return JSONResponse(
        status_code=status_code,
        content={
            "error": "Internal Server Error",
            "message": str(exc) if settings.debug else "An unexpected error occurred",
            "type": type(exc).__name__,
            "stack_trace": stack_trace if settings.debug else None,
        },
    )


@app.get(
    "/",
    summary="根端点",
    description="知识图谱系统的根端点，返回系统的基本状态信息。",
    responses={200: {"description": "系统正常运行"}},
)
async def root():
    """根端点

    Returns:
        包含系统状态信息的响应
    """
    return {
        "status": "ok",
        "message": "教育知识图谱系统运行中",
        "version": "0.1.0",
    }


@app.get(
    "/health",
    summary="健康检查端点",
    description="知识图谱系统的健康检查端点，用于监控系统的运行状态。",
    responses={200: {"description": "系统健康"}, 503: {"description": "系统不健康"}},
)
async def health_check():
    """健康检查端点

    Returns:
        包含系统健康状态的响应
    """
    return {
        "status": "healthy",
        "app_name": settings.app_name,
        "debug": settings.debug,
    }


# 注册路由
from app.routers import visualization, reports

app.include_router(visualization.router)
app.include_router(reports.router)
