"""FastAPI依赖注入模块

本模块提供了所有服务的依赖注入函数，用于在路由和其他组件中获取服务实例。
"""

from typing import Optional

from app.services.llm_service import LLMAnalysisService, llm_service
from app.services.cache_service import CacheService, cache_service
from app.services.graph_service import GraphService, graph_service
from app.services.data_import_service import DataImportService, data_import_service
from app.services.visualization_service import VisualizationService, visualization_service
from app.services.report_service import ReportService, report_service
from app.services.query_service import QueryService, query_service


async def get_llm_service() -> Optional[LLMAnalysisService]:
    """获取LLM分析服务实例
    
    Returns:
        LLM分析服务实例，如果未初始化则返回None
    """
    return llm_service


def get_cache_service() -> Optional[CacheService]:
    """获取缓存服务实例
    
    Returns:
        缓存服务实例，如果未初始化则返回None
    """
    return cache_service


def get_graph_service() -> Optional[GraphService]:
    """获取图服务实例
    
    Returns:
        图服务实例，如果未初始化则返回None
    """
    return graph_service


def get_data_import_service() -> Optional[DataImportService]:
    """获取数据导入服务实例
    
    Returns:
        数据导入服务实例，如果未初始化则返回None
    """
    return data_import_service


def get_visualization_service() -> Optional[VisualizationService]:
    """获取可视化服务实例
    
    Returns:
        可视化服务实例，如果未初始化则返回None
    """
    return visualization_service


def get_report_service() -> Optional[ReportService]:
    """获取报告服务实例
    
    Returns:
        报告服务实例，如果未初始化则返回None
    """
    return report_service


def get_query_service() -> Optional[QueryService]:
    """获取查询服务实例
    
    Returns:
        查询服务实例，如果未初始化则返回None
    """
    return query_service
