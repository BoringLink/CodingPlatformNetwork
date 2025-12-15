"""结构化日志配置"""

import sys
import structlog
from typing import Any

from app.config import settings


def configure_logging() -> None:
    """配置 structlog 结构化日志
    
    根据配置的日志格式（JSON 或 Console）和日志级别设置日志处理器
    """
    
    # 共享的处理器
    shared_processors = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
    ]
    
    if settings.log_format == "json":
        # JSON 格式 - 适合生产环境
        processors = shared_processors + [
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ]
    else:
        # Console 格式 - 适合开发环境
        processors = shared_processors + [
            structlog.processors.format_exc_info,
            structlog.dev.ConsoleRenderer(colors=True),
        ]
    
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(
            _get_log_level_from_string(settings.log_level)
        ),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(file=sys.stdout),
        cache_logger_on_first_use=True,
    )


def _get_log_level_from_string(level: str) -> int:
    """将字符串日志级别转换为整数"""
    import logging
    
    level_map = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL,
    }
    
    return level_map.get(level.upper(), logging.INFO)


def get_logger(name: str | None = None) -> Any:
    """获取结构化日志记录器
    
    Args:
        name: 日志记录器名称，通常使用模块名
        
    Returns:
        structlog 日志记录器实例
    """
    if name:
        return structlog.get_logger(name)
    return structlog.get_logger()
