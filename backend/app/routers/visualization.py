"""可视化 API 路由"""

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from app.dependencies import (
    get_llm_service,
    get_query_service,
    get_visualization_service,
)
from app.models.nodes import NodeType
from app.models.relationships import RelationshipType
from app.services.query_service import GraphFilter, NodeFilter, RelationshipFilter
from app.services.visualization_service import (
    VisualizationOptions,
)

logger = structlog.get_logger()

router = APIRouter(prefix="/api", tags=["visualization"])  # 添加API版本控制


class VisualizationRequest(BaseModel):
    """可视化请求"""

    root_node_id: str = Field(..., description="根节点 ID")
    depth: int = Field(default=2, ge=1, le=5, description="查询深度（1-5）")
    layout: str = Field(default="force-directed", description="布局算法")
    node_types: list[str] | None = Field(default=None, description="节点类型过滤")
    relationship_types: list[str] | None = Field(default=None, description="关系类型过滤")
    show_labels: bool = Field(default=True, description="是否显示标签")
    start_date: str | None = Field(default=None, description="开始日期")
    end_date: str | None = Field(default=None, description="结束日期")
    school: str | None = Field(default=None, description="学校筛选")
    grade: int | None = Field(default=None, description="年级筛选")
    class_: str | None = Field(default=None, alias="class", description="班级筛选")
    limit: int = Field(default=1000, ge=100, le=5000, description="返回节点数量限制")
    offset: int = Field(default=0, ge=0, description="返回节点偏移量")


class SubviewCreateRequest(BaseModel):
    """创建子视图请求"""

    name: str = Field(..., description="子视图名称")
    root_node_id: str = Field(..., description="根节点 ID")
    depth: int = Field(default=2, ge=1, le=5, description="查询深度")
    node_types: list[str] | None = Field(default=None, description="节点类型过滤")
    relationship_types: list[str] | None = Field(default=None, description="关系类型过滤")


class SubviewUpdateRequest(BaseModel):
    """更新子视图请求"""

    root_node_id: str = Field(..., description="根节点 ID")
    depth: int = Field(default=2, ge=1, le=5, description="查询深度")
    node_types: list[str] | None = Field(default=None, description="节点类型过滤")
    relationship_types: list[str] | None = Field(default=None, description="关系类型过滤")


@router.get(
    "/visualization",
    summary="生成可视化数据",
    description="根据根节点ID和查询深度，生成知识图谱的可视化数据。支持节点类型和关系类型过滤，以及不同的布局算法选择。",
    responses={
        200: {"description": "可视化数据生成成功"},
        400: {"description": "无效的请求参数"},
        404: {"description": "根节点不存在"},
        500: {"description": "服务器内部错误"},
    },
)
async def generate_visualization_get(
    rootNodeId: str,
    depth: int = 2,
    nodeTypes: list[str] | None = Query(None),
    relationshipTypes: list[str] | None = Query(None),
    startDate: str | None = Query(None),
    endDate: str | None = Query(None),
    layout: str = Query("force-directed"),
    showLabels: bool = Query(True),
    school: str | None = Query(None),
    grade: int | None = Query(None),
    class_: str | None = Query(None, alias="class"),
    viz_service=Depends(get_visualization_service),
    q_service=Depends(get_query_service),
    llm_service=Depends(get_llm_service),
):
    """生成可视化数据（GET）

    根据根节点和深度查询子图，并生成可视化数据

    Args:
        rootNodeId: 根节点ID
        depth: 查询深度
        nodeTypes: 节点类型过滤
        relationshipTypes: 关系类型过滤
        startDate: 开始日期
        endDate: 结束日期
        layout: 布局算法
        showLabels: 是否显示标签

    Returns:
        包含可视化数据的响应

    Raises:
        HTTPException: 请求参数无效或根节点不存在
    """
    # 处理逗号分隔的字符串参数
    processed_node_types = []
    if nodeTypes:
        for node_type in nodeTypes:
            if isinstance(node_type, str):
                # 分割逗号分隔的字符串
                processed_node_types.extend(
                    [nt.strip() for nt in node_type.split(",") if nt.strip()]
                )
            else:
                processed_node_types.append(node_type)

    processed_relationship_types = []
    if relationshipTypes:
        for rel_type in relationshipTypes:
            if isinstance(rel_type, str):
                # 分割逗号分隔的字符串
                processed_relationship_types.extend(
                    [rt.strip() for rt in rel_type.split(",") if rt.strip()]
                )
            else:
                processed_relationship_types.append(rel_type)

    # 构造请求对象
    request = VisualizationRequest(
        root_node_id=rootNodeId,
        depth=depth,
        node_types=processed_node_types,  # 始终传递列表，即使为空
        relationship_types=processed_relationship_types,  # 始终传递列表，即使为空
        layout=layout,
        show_labels=showLabels,
        start_date=startDate,
        end_date=endDate,
        school=school,
        grade=grade,
        class_=class_,
    )
    return await generate_visualization(request, viz_service, q_service, llm_service)


@router.post(
    "/generate",
    summary="生成可视化数据",
    description="根据根节点ID和查询深度，生成知识图谱的可视化数据。支持节点类型和关系类型过滤，以及不同的布局算法选择。",
    responses={
        200: {"description": "可视化数据生成成功"},
        400: {"description": "无效的请求参数"},
        404: {"description": "根节点不存在"},
        500: {"description": "服务器内部错误"},
    },
)
async def generate_visualization(
    request: VisualizationRequest,
    viz_service=Depends(get_visualization_service),
    q_service=Depends(get_query_service),
    llm_service=Depends(get_llm_service),
):
    """生成可视化数据

    根据根节点和深度查询子图，并生成可视化数据

    Args:
        request: 可视化请求参数，包含根节点ID、查询深度、布局算法等

    Returns:
        包含可视化数据的响应

    Raises:
        HTTPException: 请求参数无效或根节点不存在
    """
    try:
        # 解析节点类型过滤
        # 注意：空列表表示不过滤（显示所有类型），None也表示不过滤
        node_types = None
        if request.node_types is not None and len(request.node_types) > 0:
            try:
                node_types = [NodeType(nt) for nt in request.node_types]
            except ValueError as e:
                raise HTTPException(
                    status_code=400,
                    detail=f"无效的节点类型: {e}",
                )

        # 检查节点类型过滤是否包含根节点类型
        # 注意：我们不能在此时检查，因为我们不知道根节点的类型
        # 这个检查将在query_subgraph方法中处理

        # 解析关系类型过滤
        # 注意：空列表表示不过滤（显示所有类型），None也表示不过滤
        relationship_types = None
        if request.relationship_types is not None and len(request.relationship_types) > 0:
            try:
                relationship_types = [RelationshipType(rt) for rt in request.relationship_types]
            except ValueError as e:
                raise HTTPException(
                    status_code=400,
                    detail=f"无效的关系类型: {e}",
                )

        # 创建图过滤器（包含学校/年级/班级筛选）
        graph_filter = GraphFilter(
            node_types=node_types,
            relationship_types=relationship_types,
            date_range=(
                {
                    "start": request.start_date,
                    "end": request.end_date,
                }
                if request.start_date or request.end_date
                else None
            ),
            school=request.school,
            grade=request.grade,
            class_=request.class_,
        )

        # 创建节点过滤器（用于查询子图中的节点筛选）
        node_filter = NodeFilter(
            types=node_types,
            school=request.school,
            grade=request.grade,
            class_=request.class_,
        )

        try:
            # 使用请求参数作为最大节点数和关系数限制
            max_nodes = request.limit  # 设置最大节点数限制
            max_relationships = request.limit * 5  # 设置最大关系数限制（节点数的5倍）

            # 查询子图，添加节点和关系数量限制
            subgraph = await q_service.query_subgraph(
                root_node_id=request.root_node_id,
                depth=request.depth,
                filter=graph_filter,
                max_nodes=max_nodes,
                max_relationships=max_relationships,
            )
        except ValueError as e:
            # 记录完整的异常信息，包括堆栈跟踪
            import traceback

            logger.warning(
                "visualization_generation_failed",
                error=str(e),
                error_type=type(e).__name__,
                root_node_id=request.root_node_id,
                stack_trace=traceback.format_exc(),
            )

            # 检查异常是否真的是根节点不存在
            # 只有当异常消息明确表示根节点不存在时，才返回404
            if "根节点不存在" in str(e) or "root node" in str(e).lower():
                raise HTTPException(
                    status_code=404,
                    detail=f"根节点不存在: {request.root_node_id}",
                )
            else:
                # 其他ValueError异常应该返回500
                raise HTTPException(
                    status_code=500,
                    detail=f"生成可视化数据失败: {str(e)}",
                )
        except RuntimeError as e:
            # 数据库查询错误
            logger.error("subgraph_query_failed", error=str(e), root_node_id=request.root_node_id)
            raise HTTPException(
                status_code=500,
                detail=f"查询子图失败: {e}",
            )
        except Exception as e:
            # 捕获其他异常，包括内存不足错误
            logger.error(
                "subgraph_query_generic_error", error=str(e), root_node_id=request.root_node_id
            )
            if "OutOfMemory" in str(e):
                raise HTTPException(
                    status_code=500,
                    detail=f"查询数据量过大，请尝试减小查询深度或缩小筛选范围: {e}",
                )
            raise HTTPException(
                status_code=500,
                detail=f"生成可视化数据失败: {e}",
            )

        # 创建可视化选项
        viz_options = VisualizationOptions(
            layout=request.layout,
            show_labels=request.show_labels,
        )

        # 使用LLM分析子图数据
        llm_results = None
        try:
            logger.info(
                "analyzing_subgraph_with_llm",
                root_node_id=request.root_node_id,
                depth=request.depth,
            )

            # 提取子图数据用于LLM分析
            subgraph_data = {
                "nodes": [
                    {
                        "id": node.id,
                        "type": node.type.value,
                        "properties": node.properties,
                    }
                    for node in subgraph.nodes
                ],
                "relationships": [
                    {
                        "id": rel.id,
                        "type": rel.type.value,
                        "from_node_id": rel.from_node_id,
                        "to_node_id": rel.to_node_id,
                        "properties": rel.properties,
                    }
                    for rel in subgraph.relationships
                ],
            }

            # 根据子图数据类型选择合适的LLM分析方法
            if any(node["type"] == "Student" for node in subgraph_data["nodes"]):
                # 如果包含学生节点，分析学生关注度
                llm_results = await llm_service.analyze_student_attention(
                    [
                        {
                            "type": "student_interaction",
                            "data": {"content": str(subgraph_data)},
                        }
                    ]
                )
            else:
                # 否则分析知识点统计
                llm_results = await llm_service.analyze_knowledge_statistics(
                    [{"type": "course_record", "data": {"content": str(subgraph_data)}}]
                )

            logger.info("llm_analysis_completed", result_keys=list(llm_results.keys()))
        except Exception as e:
            logger.warning("llm_analysis_failed", error=str(e), root_node_id=request.root_node_id)
            # 继续执行，即使LLM分析失败也返回可视化数据

        # 生成可视化数据，传入LLM分析结果
        viz_data = viz_service.generate_visualization(
            subgraph=subgraph,
            options=viz_options,
            llm_results=llm_results,
        )

        logger.info(
            "visualization_generated",
            root_node_id=request.root_node_id,
            depth=request.depth,
            node_count=len(viz_data.nodes),
            edge_count=len(viz_data.edges),
            has_llm_results=llm_results is not None,
        )

        return {
            "success": True,
            "data": viz_data.to_dict(),
            "llm_analysis": llm_results,
        }

    except HTTPException:
        # 重新抛出已处理的HTTPException
        raise
    except Exception as e:
        logger.error("visualization_generation_error", error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"生成可视化数据失败: {e}",
        )


@router.post(
    "/subviews",
    summary="创建子视图",
    description="基于筛选条件创建一个新的知识图谱子视图，包括指定根节点、查询深度、节点类型和关系类型过滤。",
    responses={
        200: {"description": "子视图创建成功"},
        400: {"description": "无效的请求参数"},
        404: {"description": "根节点不存在"},
        500: {"description": "服务器内部错误"},
    },
)
async def create_subview(
    request: SubviewCreateRequest,
    viz_service=Depends(get_visualization_service),
    q_service=Depends(get_query_service),
):
    """创建子视图

    基于筛选条件创建一个新的子视图

    Args:
        request: 子视图创建请求参数，包含子视图名称、根节点ID、查询深度等

    Returns:
        包含创建的子视图信息的响应

    Raises:
        HTTPException: 请求参数无效或根节点不存在
    """
    try:
        # 解析节点类型过滤
        node_types = None
        if request.node_types:
            try:
                node_types = [NodeType(nt) for nt in request.node_types]
            except ValueError as e:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid node type: {e}",
                )

        # 解析关系类型过滤
        relationship_types = None
        if request.relationship_types:
            try:
                relationship_types = [RelationshipType(rt) for rt in request.relationship_types]
            except ValueError as e:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid relationship type: {e}",
                )

        # 创建图过滤器
        graph_filter = GraphFilter(
            node_types=node_types,
            relationship_types=relationship_types,
        )

        # 查询子图
        subgraph = await q_service.query_subgraph(
            root_node_id=request.root_node_id,
            depth=request.depth,
            filter=graph_filter,
        )

        # 创建子视图
        subview = await viz_service.create_subview(
            filter=graph_filter,
            name=request.name,
            subgraph=subgraph,
        )

        logger.info(
            "subview_created",
            subview_id=subview.id,
            name=request.name,
        )

        return {
            "success": True,
            "data": subview.to_dict(),
        }

    except ValueError as e:
        logger.warning("subview_creation_failed", error=str(e))
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error("subview_creation_error", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to create subview: {e}")


@router.get(
    "/subviews",
    summary="列出所有子视图",
    description="获取系统中所有已创建的知识图谱子视图的摘要信息，包括ID、名称、创建时间等。",
    responses={
        200: {"description": "子视图列表获取成功"},
        500: {"description": "服务器内部错误"},
    },
)
async def list_subviews(viz_service=Depends(get_visualization_service)):
    """列出所有子视图

    获取所有已创建子视图的摘要信息

    Returns:
        包含子视图列表的响应

    Raises:
        HTTPException: 服务器内部错误
    """
    try:
        subviews = await viz_service.list_subviews()

        return {
            "success": True,
            "data": {
                "subviews": subviews,
                "count": len(subviews),
            },
        }

    except Exception as e:
        logger.error("subview_list_error", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to list subviews: {e}")


@router.get(
    "/subviews/{subview_id}",
    summary="获取子视图详情",
    description="根据子视图ID，获取特定子视图的详细信息，包括筛选条件、创建时间等。",
    responses={
        200: {"description": "子视图详情获取成功"},
        404: {"description": "子视图不存在"},
        500: {"description": "服务器内部错误"},
    },
)
async def get_subview(subview_id: str, viz_service=Depends(get_visualization_service)):
    """获取子视图

    根据 ID 获取已创建的子视图

    Args:
        subview_id: 子视图的唯一标识符

    Returns:
        包含子视图详情的响应

    Raises:
        HTTPException: 子视图不存在或服务器内部错误
    """
    try:
        subview = await viz_service.get_subview(subview_id)

        if not subview:
            raise HTTPException(
                status_code=404,
                detail=f"Subview not found: {subview_id}",
            )

        return {
            "success": True,
            "data": subview.to_dict(),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error("subview_retrieval_error", subview_id=subview_id, error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get subview: {e}")


@router.get(
    "/nodes",
    summary="查询节点列表",
    description="根据过滤条件查询节点列表，支持节点类型过滤、分页等功能。",
    responses={
        200: {"description": "节点列表查询成功"},
        400: {"description": "无效的请求参数"},
        500: {"description": "服务器内部错误"},
    },
)
async def get_nodes(
    nodeTypes: list[str] | None = Query(None, description="节点类型过滤，支持多个值，逗号分隔"),
    school: str | None = Query(None, description="学校筛选"),
    grade: int | None = Query(None, description="年级筛选"),
    class_: str | None = Query(None, alias="class", description="班级筛选"),
    limit: int = Query(100, description="返回节点数量限制，默认100"),
    offset: int = Query(0, description="偏移量，用于分页"),
    q_service=Depends(get_query_service),
):
    """查询节点列表

    根据过滤条件查询节点列表，支持节点类型过滤和分页

    Args:
        nodeTypes: 节点类型过滤，支持多个值，逗号分隔
        limit: 返回节点数量限制，默认100
        offset: 偏移量，用于分页

    Returns:
        包含节点列表的响应

    Raises:
        HTTPException: 请求参数无效或服务器内部错误
    """
    try:
        # 处理节点类型参数
        processed_node_types = []
        if nodeTypes:
            for node_type in nodeTypes:
                if isinstance(node_type, str):
                    # 分割逗号分隔的字符串
                    processed_node_types.extend(
                        [nt.strip() for nt in node_type.split(",") if nt.strip()]
                    )
                else:
                    processed_node_types.append(node_type)

        # 解析节点类型
        node_types = None
        if processed_node_types:
            try:
                node_types = [NodeType(nt) for nt in processed_node_types]
            except ValueError as e:
                raise HTTPException(
                    status_code=400,
                    detail=f"无效的节点类型: {e}",
                )

        # 构造节点过滤器
        node_filter = NodeFilter(
            types=node_types,
            school=school,
            grade=grade,
            class_=class_,
            limit=limit,
            offset=offset,
        )

        # 查询节点
        nodes = await q_service.query_nodes(filter=node_filter)

        # 构造响应
        return {
            "success": True,
            "data": {
                "nodes": [node.to_dict() for node in nodes],
                "count": len(nodes),
                "limit": limit,
                "offset": offset,
            },
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error("nodes_query_failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"查询节点失败: {e}")


@router.get(
    "/nodes/{node_id}/details",
    summary="获取节点详情",
    description="根据节点ID获取节点的详细信息，包括关联关系等。",
    responses={
        200: {"description": "节点详情获取成功"},
        404: {"description": "节点不存在"},
        500: {"description": "服务器内部错误"},
    },
)
async def get_node_details(
    node_id: str,
    q_service=Depends(get_query_service),
):
    """获取节点详情

    根据节点ID获取节点的详细信息，包括关联关系

    Args:
        node_id: 节点ID

    Returns:
        包含节点详情的响应

    Raises:
        HTTPException: 节点不存在或服务器内部错误
    """
    try:
        # 查询节点详情
        node_details = await q_service.query_node_details(node_id)
        if not node_details:
            raise HTTPException(
                status_code=404,
                detail=f"节点不存在: {node_id}",
            )

        # 构造响应数据，确保所有对象都转换为字典
        response_data = {
            "node": node_details["node"].to_dict(),
            "relationshipTypeCounts": node_details["relationshipTypeCounts"],
            # "relationshipCounts": [
            #     rel.to_dict() for rel in node_details["relationshipCounts"]
            # ],
            # "related_nodes": [rn.to_dict() for rn in node_details["related_nodes"]],
        }

        return {
            "success": True,
            "data": response_data,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error("node_details_query_failed", node_id=node_id, error=str(e))
        raise HTTPException(status_code=500, detail=f"查询节点详情失败: {e}")


@router.get(
    "/relationships",
    summary="查询关系列表",
    description="根据过滤条件查询关系列表，支持关系类型过滤、分页等功能。",
    responses={
        200: {"description": "关系列表查询成功"},
        400: {"description": "无效的请求参数"},
        500: {"description": "服务器内部错误"},
    },
)
async def get_relationships(
    relationshipTypes: list[str] | None = Query(
        None, description="关系类型过滤，支持多个值，逗号分隔"
    ),
    limit: int = Query(100, description="返回关系数量限制，默认100"),
    offset: int = Query(0, description="偏移量，用于分页"),
    q_service=Depends(get_query_service),
):
    """查询关系列表

    根据过滤条件查询关系列表，支持关系类型过滤和分页

    Args:
        relationshipTypes: 关系类型过滤，支持多个值，逗号分隔
        limit: 返回关系数量限制，默认100
        offset: 偏移量，用于分页

    Returns:
        包含关系列表的响应

    Raises:
        HTTPException: 请求参数无效或服务器内部错误
    """
    try:
        # 处理关系类型参数
        processed_relationship_types = []
        if relationshipTypes:
            for rel_type in relationshipTypes:
                if isinstance(rel_type, str):
                    # 分割逗号分隔的字符串
                    processed_relationship_types.extend(
                        [rt.strip() for rt in rel_type.split(",") if rt.strip()]
                    )
                else:
                    processed_relationship_types.append(rel_type)

        # 解析关系类型
        relationship_types = None
        if processed_relationship_types:
            try:
                relationship_types = [RelationshipType(rt) for rt in processed_relationship_types]
            except ValueError as e:
                raise HTTPException(
                    status_code=400,
                    detail=f"无效的关系类型: {e}",
                )

        # 构造关系过滤器
        rel_filter = RelationshipFilter(
            types=relationship_types,
            limit=limit,
            offset=offset,
        )

        # 查询关系
        relationships = await q_service.query_relationships(filter=rel_filter)

        return {
            "success": True,
            "data": {
                "relationships": [rel.to_dict() for rel in relationships],
                "count": len(relationships),
                "limit": limit,
                "offset": offset,
            },
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error("relationships_query_failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"查询关系失败: {e}")


@router.get(
    "/subgraph",
    summary="查询子图",
    description="根据根节点ID和深度查询子图，支持节点类型和关系类型过滤。",
    responses={
        200: {"description": "子图查询成功"},
        400: {"description": "无效的请求参数"},
        404: {"description": "根节点不存在"},
        500: {"description": "服务器内部错误"},
    },
)
async def get_subgraph(
    rootNodeId: str,
    depth: int = Query(2, ge=1, le=5, description="查询深度（1-5）"),
    nodeTypes: list[str] | None = Query(None, description="节点类型过滤"),
    relationshipTypes: list[str] | None = Query(None, description="关系类型过滤"),
    q_service=Depends(get_query_service),
):
    """查询子图

    根据根节点ID和深度查询子图，支持节点类型和关系类型过滤

    Args:
        rootNodeId: 根节点ID
        depth: 查询深度
        nodeTypes: 节点类型过滤
        relationshipTypes: 关系类型过滤

    Returns:
        包含子图数据的响应

    Raises:
        HTTPException: 请求参数无效、根节点不存在或服务器内部错误
    """
    try:
        # 处理节点类型参数
        processed_node_types = []
        if nodeTypes:
            for node_type in nodeTypes:
                if isinstance(node_type, str):
                    # 分割逗号分隔的字符串
                    processed_node_types.extend(
                        [nt.strip() for nt in node_type.split(",") if nt.strip()]
                    )
                else:
                    processed_node_types.append(node_type)

        # 处理关系类型参数
        processed_relationship_types = []
        if relationshipTypes:
            for rel_type in relationshipTypes:
                if isinstance(rel_type, str):
                    # 分割逗号分隔的字符串
                    processed_relationship_types.extend(
                        [rt.strip() for rt in rel_type.split(",") if rt.strip()]
                    )
                else:
                    processed_relationship_types.append(rel_type)

        # 解析节点类型
        node_types = None
        if processed_node_types:
            try:
                node_types = [NodeType(nt) for nt in processed_node_types]
            except ValueError as e:
                raise HTTPException(
                    status_code=400,
                    detail=f"无效的节点类型: {e}",
                )

        # 解析关系类型
        relationship_types = None
        if processed_relationship_types:
            try:
                relationship_types = [RelationshipType(rt) for rt in processed_relationship_types]
            except ValueError as e:
                raise HTTPException(
                    status_code=400,
                    detail=f"无效的关系类型: {e}",
                )

        # 创建图过滤器
        graph_filter = GraphFilter(
            node_types=node_types,
            relationship_types=relationship_types,
        )

        # 查询子图
        subgraph = await q_service.query_subgraph(
            root_node_id=rootNodeId,
            depth=depth,
            filter=graph_filter,
        )

        return {
            "success": True,
            "data": subgraph.to_dict(),
        }
    except ValueError as e:
        logger.warning("subgraph_query_failed", error=str(e), root_node_id=rootNodeId)
        raise HTTPException(
            status_code=404,
            detail=f"根节点不存在: {rootNodeId}",
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("subgraph_query_failed", error=str(e), root_node_id=rootNodeId)
        raise HTTPException(status_code=500, detail=f"查询子图失败: {e}")


@router.put(
    "/subviews/{subview_id}",
    summary="更新子视图",
    description="根据子视图ID，更新已存在子视图的筛选条件，包括根节点、查询深度、节点类型和关系类型过滤。",
    responses={
        200: {"description": "子视图更新成功"},
        400: {"description": "无效的请求参数"},
        404: {"description": "子视图不存在"},
        500: {"description": "服务器内部错误"},
    },
)
async def update_subview(
    subview_id: str,
    request: SubviewUpdateRequest,
    viz_service=Depends(get_visualization_service),
    q_service=Depends(get_query_service),
):
    """更新子视图筛选条件

    更新已存在子视图的筛选条件和数据

    Args:
        subview_id: 子视图的唯一标识符
        request: 子视图更新请求参数，包含新的筛选条件

    Returns:
        包含更新后的子视图信息的响应

    Raises:
        HTTPException: 子视图不存在、请求参数无效或服务器内部错误
    """
    try:
        # 解析节点类型过滤
        node_types = None
        if request.node_types:
            try:
                node_types = [NodeType(nt) for nt in request.node_types]
            except ValueError as e:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid node type: {e}",
                )

        # 解析关系类型过滤
        relationship_types = None
        if request.relationship_types:
            try:
                relationship_types = [RelationshipType(rt) for rt in request.relationship_types]
            except ValueError as e:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid relationship type: {e}",
                )

        # 创建图过滤器
        graph_filter = GraphFilter(
            node_types=node_types,
            relationship_types=relationship_types,
        )

        # 查询新的子图
        subgraph = await q_service.query_subgraph(
            root_node_id=request.root_node_id,
            depth=request.depth,
            filter=graph_filter,
        )

        # 更新子视图
        subview = await viz_service.update_subview_filter(
            subview_id=subview_id,
            filter=graph_filter,
            subgraph=subgraph,
        )

        if not subview:
            raise HTTPException(
                status_code=404,
                detail=f"Subview not found: {subview_id}",
            )

        logger.info(
            "subview_updated",
            subview_id=subview_id,
        )

        return {
            "success": True,
            "data": subview.to_dict(),
        }

    except HTTPException:
        raise
    except ValueError as e:
        logger.warning("subview_update_failed", error=str(e))
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error("subview_update_error", subview_id=subview_id, error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to update subview: {e}")


@router.delete(
    "/subviews/{subview_id}",
    summary="删除子视图",
    description="根据子视图ID，从系统中删除指定的知识图谱子视图。",
    responses={
        200: {"description": "子视图删除成功"},
        404: {"description": "子视图不存在"},
        500: {"description": "服务器内部错误"},
    },
)
async def delete_subview(subview_id: str, viz_service=Depends(get_visualization_service)):
    """删除子视图

    从数据库中删除指定的子视图

    Args:
        subview_id: 子视图的唯一标识符

    Returns:
        包含删除结果的响应

    Raises:
        HTTPException: 子视图不存在或服务器内部错误
    """
    try:
        success = await viz_service.delete_subview(subview_id)

        if not success:
            raise HTTPException(
                status_code=404,
                detail=f"Subview not found: {subview_id}",
            )

        logger.info("subview_deleted", subview_id=subview_id)

        return {
            "success": True,
            "message": f"Subview {subview_id} deleted successfully",
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error("subview_deletion_error", subview_id=subview_id, error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to delete subview: {e}")


@router.get(
    "/nodes/{node_id}/details",
    summary="获取节点详情",
    description="根据节点ID，获取知识图谱中特定节点的详细信息，包括节点属性和关联关系统计。",
    responses={
        200: {"description": "节点详情获取成功"},
        404: {"description": "节点不存在"},
        500: {"description": "服务器内部错误"},
    },
)
async def get_node_details(
    node_id: str,
    viz_service=Depends(get_visualization_service),
    q_service=Depends(get_query_service),
):
    """获取节点详情

    获取节点的详细信息，包括属性和关联关系统计

    Args:
        node_id: 节点的唯一标识符

    Returns:
        包含节点详情的响应

    Raises:
        HTTPException: 节点不存在或服务器内部错误
    """
    try:
        from app.services.query_service import NodeFilter, RelationshipFilter

        # 查询节点
        nodes = await q_service.query_nodes(NodeFilter(properties={"id": node_id}))

        if not nodes:
            raise HTTPException(
                status_code=404,
                detail=f"Node not found: {node_id}",
            )

        node = nodes[0]

        # 查询与该节点相关的所有关系
        relationships = await q_service.query_relationships(
            RelationshipFilter(from_node_id=node_id)
        )

        # 同时查询指向该节点的关系
        incoming_relationships = await q_service.query_relationships(
            RelationshipFilter(to_node_id=node_id)
        )

        all_relationships = relationships + incoming_relationships

        # 获取节点详情
        node_details = await viz_service.get_node_details(
            node=node,
            relationships=all_relationships,
        )

        logger.info(
            "node_details_retrieved",
            node_id=node_id,
            relationship_count=len(all_relationships),
        )

        return {
            "success": True,
            "data": node_details.to_dict(),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error("node_details_retrieval_error", node_id=node_id, error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get node details: {e}")


@router.get(
    "/layouts",
    summary="获取可用布局算法",
    description="获取系统支持的所有知识图谱布局算法列表，包括每种布局的名称、显示名称和描述。",
    responses={200: {"description": "布局算法列表获取成功"}},
)
async def get_available_layouts():
    """获取可用的布局算法列表

    Returns:
        包含可用布局算法列表的响应
    """
    return {
        "success": True,
        "data": {
            "layouts": [
                {
                    "name": "force-directed",
                    "display_name": "力导向布局",
                    "description": "基于物理模拟的力导向布局，适合展示复杂网络结构",
                },
                {
                    "name": "hierarchical",
                    "display_name": "层次布局",
                    "description": "按层次结构排列节点，适合展示有向图和树形结构",
                },
                {
                    "name": "circular",
                    "display_name": "圆形布局",
                    "description": "将节点排列成圆形，适合展示循环关系",
                },
                {
                    "name": "concentric",
                    "display_name": "同心圆布局",
                    "description": "将节点按重要性排列成同心圆，适合展示中心化网络",
                },
                {
                    "name": "grid",
                    "display_name": "网格布局",
                    "description": "将节点排列成网格，适合展示规则结构",
                },
            ],
        },
    }


@router.get(
    "/filter-options",
    summary="获取筛选选项",
    description="获取用于筛选的可用选项，包括学校、年级和班级列表，支持层级链式选择。",
    responses={200: {"description": "筛选选项获取成功"}},
)
async def get_filter_options(
    school: str | None = Query(None, description="已选学校，用于获取对应的年级和班级选项"),
    grade: int | None = Query(None, description="已选年级，用于获取对应的班级选项"),
    viz_service=Depends(get_visualization_service),
    q_service=Depends(get_query_service),
):
    """获取筛选选项

    获取系统中可用的学校、年级和班级选项，支持根据已选学校和年级返回对应的选项，用于前端筛选器

    Args:
        school: 已选学校，用于获取对应的年级和班级选项
        grade: 已选年级，用于获取对应的班级选项

    Returns:
        包含筛选选项的响应
    """
    try:
        # 从School、Grade、Class节点获取信息
        all_schools = set()
        available_grades = set()
        available_classes = set()

        # 1. 获取学校列表 - 始终返回所有可用学校
        school_query = "MATCH (s:School) RETURN s.name AS name"
        school_results = await q_service.run_cypher_query(school_query)
        all_schools = {result["name"] for result in school_results if result["name"]}

        # 2. 获取年级列表
        if school:
            # 如果指定了学校，返回该学校关联的所有Grade节点
            grade_query = """MATCH (s:School)-[:HAS_GRADE]->(g:Grade) 
                           WHERE s.name = $school 
                           RETURN g.level AS level"""
            grade_results = await q_service.run_cypher_query(grade_query, {"school": school})
            available_grades = {
                result["level"] for result in grade_results if result["level"] is not None
            }
        else:
            # 如果没有指定学校，返回所有年级
            grade_query = "MATCH (g:Grade) RETURN DISTINCT g.level AS level"
            grade_results = await q_service.run_cypher_query(grade_query)
            available_grades = {
                result["level"] for result in grade_results if result["level"] is not None
            }

        # 3. 获取班级列表
        if school:
            if grade is not None:
                # 如果同时指定了学校和年级，返回该学校和年级关联的所有Class节点
                class_query = """MATCH (s:School)-[:HAS_GRADE]->(g:Grade)-[:HAS_CLASS]->(c:Class) 
                               WHERE s.name = $school AND g.level = $grade 
                               RETURN c.name AS name"""
                class_results = await q_service.run_cypher_query(
                    class_query, {"school": school, "grade": grade}
                )
                available_classes = {result["name"] for result in class_results if result["name"]}
            else:
                # 如果只指定了学校，返回该学校关联的所有Class节点
                class_query = """MATCH (s:School)-[:HAS_GRADE]->(g:Grade)-[:HAS_CLASS]->(c:Class) 
                               WHERE s.name = $school 
                               RETURN c.name AS name"""
                class_results = await q_service.run_cypher_query(class_query, {"school": school})
                available_classes = {result["name"] for result in class_results if result["name"]}
        elif grade is not None:
            # 如果只指定了年级，返回所有学校中该年级的班级
            class_query = """MATCH (s:School)-[:HAS_GRADE]->(g:Grade)-[:HAS_CLASS]->(c:Class) 
                           WHERE g.level = $grade 
                           RETURN c.name AS name"""
            class_results = await q_service.run_cypher_query(class_query, {"grade": grade})
            available_classes = {result["name"] for result in class_results if result["name"]}
        # 否则不返回班级

        return {
            "success": True,
            "data": {
                "schools": sorted(list(all_schools)),
                "grades": sorted(list(available_grades)),
                "classes": sorted(list(available_classes)),
            },
        }

    except Exception as e:
        logger.error("filter_options_retrieval_error", error=str(e))
        raise HTTPException(status_code=500, detail=f"获取筛选选项失败: {e}")


@router.get(
    "/node-types",
    summary="获取节点类型信息",
    description="获取知识图谱中所有节点类型的信息，包括类型名称、显示名称、颜色和形状等视觉属性。",
    responses={200: {"description": "节点类型信息获取成功"}},
)
async def get_node_types(viz_service=Depends(get_visualization_service)):
    """获取所有节点类型及其视觉属性

    Returns:
        包含节点类型信息的响应
    """
    return {
        "success": True,
        "data": {
            "node_types": [
                {
                    "type": NodeType.STUDENT.value,
                    "display_name": "学生",
                    "color": viz_service.NODE_COLORS[NodeType.STUDENT],
                    "shape": viz_service.NODE_SHAPES[NodeType.STUDENT],
                },
                {
                    "type": NodeType.TEACHER.value,
                    "display_name": "教师",
                    "color": viz_service.NODE_COLORS[NodeType.TEACHER],
                    "shape": viz_service.NODE_SHAPES[NodeType.TEACHER],
                },
                {
                    "type": NodeType.KNOWLEDGE_POINT.value,
                    "display_name": "知识点",
                    "color": viz_service.NODE_COLORS[NodeType.KNOWLEDGE_POINT],
                    "shape": viz_service.NODE_SHAPES[NodeType.KNOWLEDGE_POINT],
                },
            ],
        },
    }


@router.get(
    "/relationship-types",
    summary="获取关系类型信息",
    description="获取知识图谱中所有关系类型的信息，包括类型名称、显示名称和颜色等视觉属性。",
    responses={200: {"description": "关系类型信息获取成功"}},
)
async def get_relationship_types(viz_service=Depends(get_visualization_service)):
    """获取所有关系类型及其视觉属性

    Returns:
        包含关系类型信息的响应
    """
    return {
        "success": True,
        "data": {
            "relationship_types": [
                {
                    "type": rel_type.value,
                    "display_name": viz_service.RELATIONSHIP_DISPLAY_NAMES.get(
                        rel_type, rel_type.value
                    ),
                    "color": viz_service.EDGE_COLORS.get(rel_type, "#999999"),
                }
                for rel_type in RelationshipType
            ],
        },
    }
