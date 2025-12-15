"""报告生成 API 路由"""

from fastapi import APIRouter, Depends, HTTPException
import structlog

from app.services.report_service import ReportService
from app.dependencies import get_report_service

logger = structlog.get_logger()

router = APIRouter(prefix="/api/reports", tags=["reports"])


@router.get(
    "/",
    summary="生成报告",
    description="生成知识图谱的综合分析报告，包括学生表现、课程效果、互动模式等统计信息。",
    responses={
        200: {"description": "报告生成成功"},
        500: {"description": "服务器内部错误"},
    },
)
async def generate_report(report_service: ReportService = Depends(get_report_service)):
    """生成报告

    生成知识图谱的综合分析报告

    Returns:
        包含报告数据的响应

    Raises:
        HTTPException: 报告生成失败
    """
    try:
        report = await report_service.generate_report()

        logger.info("report_generated")

        return {
            "success": True,
            "data": report.to_dict(),
        }

    except Exception as e:
        logger.error("report_generation_error", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to generate report: {e}")


@router.get(
    "/{report_id}",
    summary="获取报告详情",
    description="根据报告ID，获取特定报告的详细信息。",
    responses={
        200: {"description": "报告详情获取成功"},
        404: {"description": "报告不存在"},
        500: {"description": "服务器内部错误"},
    },
)
async def get_report(
    report_id: str, report_service: ReportService = Depends(get_report_service)
):
    """获取报告详情

    根据 ID 获取已生成的报告

    Args:
        report_id: 报告的唯一标识符

    Returns:
        包含报告详情的响应

    Raises:
        HTTPException: 报告不存在或服务器内部错误
    """
    try:
        report = await report_service.get_report(report_id)

        if not report:
            raise HTTPException(
                status_code=404,
                detail=f"Report not found: {report_id}",
            )

        return {
            "success": True,
            "data": report.to_dict(),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error("report_retrieval_error", report_id=report_id, error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get report: {e}")


@router.post(
    "/{report_id}/export",
    summary="导出报告",
    description="根据报告ID，将报告导出为指定格式（JSON或PDF）。",
    responses={
        200: {"description": "报告导出成功"},
        404: {"description": "报告不存在"},
        500: {"description": "服务器内部错误"},
    },
)
async def export_report(
    report_id: str,
    format: str = "json",
    report_service: ReportService = Depends(get_report_service),
):
    """导出报告

    将报告导出为指定格式

    Args:
        report_id: 报告的唯一标识符
        format: 导出格式，支持 json 或 pdf

    Returns:
        包含导出结果的响应

    Raises:
        HTTPException: 报告不存在或服务器内部错误
    """
    try:
        report = await report_service.get_report(report_id)

        if not report:
            raise HTTPException(
                status_code=404,
                detail=f"Report not found: {report_id}",
            )

        if format not in ["json", "pdf"]:
            raise HTTPException(
                status_code=400,
                detail="Invalid format. Supported formats: json, pdf",
            )

        # 调用报告服务的导出方法
        export_result = await report_service.export_report(report, format)

        logger.info("report_exported", report_id=report_id, format=format)

        return {
            "success": True,
            "data": export_result,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "report_export_error", report_id=report_id, format=format, error=str(e)
        )
        raise HTTPException(status_code=500, detail=f"Failed to export report: {e}")
