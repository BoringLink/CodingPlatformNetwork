"""分析报告生成服务"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Literal
from io import BytesIO
import json
import structlog

from app.database import neo4j_connection
from app.models.nodes import NodeType
from app.models.relationships import RelationshipType

logger = structlog.get_logger()


class ReportFormat(str):
    """报告格式"""
    JSON = "json"
    PDF = "pdf"


class GraphStatistics:
    """图谱统计信息"""
    
    def __init__(
        self,
        total_nodes: int,
        node_type_distribution: Dict[str, int],
        total_relationships: int,
        relationship_type_distribution: Dict[str, int],
        timestamp: datetime,
    ):
        self.total_nodes = total_nodes
        self.node_type_distribution = node_type_distribution
        self.total_relationships = total_relationships
        self.relationship_type_distribution = relationship_type_distribution
        self.timestamp = timestamp
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "total_nodes": self.total_nodes,
            "node_type_distribution": self.node_type_distribution,
            "total_relationships": self.total_relationships,
            "relationship_type_distribution": self.relationship_type_distribution,
            "timestamp": self.timestamp.isoformat(),
        }


class StudentPerformanceAnalysis:
    """学生表现分析"""
    
    def __init__(
        self,
        high_frequency_errors: List[Dict[str, Any]],
        students_needing_attention: List[Dict[str, Any]],
        error_distribution: Dict[str, int],
    ):
        self.high_frequency_errors = high_frequency_errors
        self.students_needing_attention = students_needing_attention
        self.error_distribution = error_distribution
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "high_frequency_errors": self.high_frequency_errors,
            "students_needing_attention": self.students_needing_attention,
            "error_distribution": self.error_distribution,
        }


class CourseEffectivenessAnalysis:
    """课程效果分析"""
    
    def __init__(
        self,
        course_metrics: List[Dict[str, Any]],
    ):
        self.course_metrics = course_metrics
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "course_metrics": self.course_metrics,
        }


class InteractionPatternAnalysis:
    """互动模式分析"""
    
    def __init__(
        self,
        social_networks: List[Dict[str, Any]],
        isolated_students: List[Dict[str, Any]],
        interaction_statistics: Dict[str, Any],
    ):
        self.social_networks = social_networks
        self.isolated_students = isolated_students
        self.interaction_statistics = interaction_statistics
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "social_networks": self.social_networks,
            "isolated_students": self.isolated_students,
            "interaction_statistics": self.interaction_statistics,
        }


class AnalysisReport:
    """分析报告"""
    
    def __init__(
        self,
        graph_statistics: GraphStatistics,
        student_performance: StudentPerformanceAnalysis,
        course_effectiveness: CourseEffectivenessAnalysis,
        interaction_patterns: InteractionPatternAnalysis,
        generated_at: datetime,
    ):
        self.graph_statistics = graph_statistics
        self.student_performance = student_performance
        self.course_effectiveness = course_effectiveness
        self.interaction_patterns = interaction_patterns
        self.generated_at = generated_at
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "graph_statistics": self.graph_statistics.to_dict(),
            "student_performance": self.student_performance.to_dict(),
            "course_effectiveness": self.course_effectiveness.to_dict(),
            "interaction_patterns": self.interaction_patterns.to_dict(),
            "generated_at": self.generated_at.isoformat(),
        }
    
    def to_json(self) -> str:
        """导出为 JSON 格式"""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)


class ReportService:
    """分析报告生成服务
    
    提供图谱统计、学生表现分析、课程效果分析、互动模式分析等功能
    """
    
    async def generate_graph_statistics(self) -> GraphStatistics:
        """生成图谱统计信息
        
        统计图谱中的节点总数和各类型节点的数量分布
        
        Returns:
            图谱统计信息
            
        Raises:
            RuntimeError: 如果数据库操作失败
        """
        try:
            async with neo4j_connection.get_session() as session:
                # 统计节点
                node_query = """
                MATCH (n)
                RETURN labels(n)[0] as node_type, count(n) as count
                """
                
                result = await session.run(node_query)
                node_records = await result.data()
                
                total_nodes = 0
                node_type_distribution = {}
                
                for record in node_records:
                    node_type = record["node_type"]
                    count = record["count"]
                    total_nodes += count
                    node_type_distribution[node_type] = count
                
                # 统计关系
                rel_query = """
                MATCH ()-[r]->()
                RETURN type(r) as rel_type, count(r) as count
                """
                
                result = await session.run(rel_query)
                rel_records = await result.data()
                
                total_relationships = 0
                relationship_type_distribution = {}
                
                for record in rel_records:
                    rel_type = record["rel_type"]
                    count = record["count"]
                    total_relationships += count
                    relationship_type_distribution[rel_type] = count
                
                logger.info(
                    "graph_statistics_generated",
                    total_nodes=total_nodes,
                    total_relationships=total_relationships,
                )
                
                return GraphStatistics(
                    total_nodes=total_nodes,
                    node_type_distribution=node_type_distribution,
                    total_relationships=total_relationships,
                    relationship_type_distribution=relationship_type_distribution,
                    timestamp=datetime.utcnow(),
                )
        except Exception as e:
            logger.error(
                "graph_statistics_generation_failed",
                error=str(e),
            )
            raise RuntimeError(f"Failed to generate graph statistics: {e}")
    
    async def analyze_student_performance(
        self,
        top_n: int = 10,
    ) -> StudentPerformanceAnalysis:
        """分析学生表现
        
        识别高频错误知识点和需要重点关注的学生群体
        
        Args:
            top_n: 返回前 N 个高频错误
            
        Returns:
            学生表现分析结果
            
        Raises:
            RuntimeError: 如果数据库操作失败
        """
        try:
            async with neo4j_connection.get_session() as session:
                # 识别高频错误知识点 - 使用count替代sum(occurrence_count)
                high_freq_query = """
                MATCH (s:Student)-[r:HAS_ERROR]->(e:ErrorType)-[:RELATES_TO]->(k:KnowledgePoint)
                WITH k, e, count(r) as total_occurrences, count(DISTINCT s) as student_count
                ORDER BY total_occurrences DESC
                LIMIT $top_n
                RETURN 
                    k.knowledge_point_id as knowledge_point_id,
                    k.name as knowledge_point_name,
                    e.error_type_id as error_type_id,
                    e.name as error_type_name,
                    total_occurrences,
                    student_count
                """
                
                result = await session.run(high_freq_query, top_n=top_n)
                high_freq_records = await result.data()
                
                high_frequency_errors = []
                for record in high_freq_records:
                    high_frequency_errors.append({
                        "knowledge_point_id": record["knowledge_point_id"],
                        "knowledge_point_name": record["knowledge_point_name"],
                        "error_type_id": record["error_type_id"],
                        "error_type_name": record["error_type_name"],
                        "total_occurrences": record["total_occurrences"],
                        "student_count": record["student_count"],
                    })
                
                # 识别需要重点关注的学生 - 使用count替代sum(occurrence_count)，降低阈值
                students_query = """
                MATCH (s:Student)-[r:HAS_ERROR]->(:ErrorType)
                WITH s, count(r) as total_errors, count(DISTINCT r) as error_types_count
                WHERE total_errors >= 1
                RETURN 
                    s.student_id as student_id,
                    s.name as student_name,
                    total_errors,
                    error_types_count
                ORDER BY total_errors DESC
                LIMIT $top_n
                """
                
                result = await session.run(students_query, top_n=top_n)
                students_records = await result.data()
                
                students_needing_attention = []
                for record in students_records:
                    students_needing_attention.append({
                        "student_id": record["student_id"],
                        "student_name": record["student_name"],
                        "total_errors": record["total_errors"],
                        "error_types_count": record["error_types_count"],
                    })
                
                # 错误分布统计 - 使用count替代sum(occurrence_count)
                error_dist_query = """
                MATCH (s:Student)-[r:HAS_ERROR]->(e:ErrorType)
                WITH e, count(r) as total_count
                RETURN e.error_type_id as error_type_id, e.name as error_name, total_count
                ORDER BY total_count DESC
                """
                
                result = await session.run(error_dist_query)
                error_dist_records = await result.data()
                
                error_distribution = {}
                for record in error_dist_records:
                    error_distribution[record["error_name"]] = record["total_count"]
                
                logger.info(
                    "student_performance_analyzed",
                    high_frequency_errors_count=len(high_frequency_errors),
                    students_needing_attention_count=len(students_needing_attention),
                )
                
                return StudentPerformanceAnalysis(
                    high_frequency_errors=high_frequency_errors,
                    students_needing_attention=students_needing_attention,
                    error_distribution=error_distribution,
                )
        except Exception as e:
            logger.error(
                "student_performance_analysis_failed",
                error=str(e),
            )
            raise RuntimeError(f"Failed to analyze student performance: {e}")
    
    async def analyze_course_effectiveness(self) -> CourseEffectivenessAnalysis:
        """分析课程效果
        
        计算每个课程的学生参与度和错误率
        
        Returns:
            课程效果分析结果
            
        Raises:
            RuntimeError: 如果数据库操作失败
        """
        try:
            async with neo4j_connection.get_session() as session:
                # 计算课程指标
                course_query = """
                MATCH (c:Course)
                OPTIONAL MATCH (s:Student)-[l:LEARNS]->(c)
                OPTIONAL MATCH (s2:Student)-[e:HAS_ERROR]->(:ErrorType)
                WHERE e.course_id = c.course_id
                WITH c, 
                     count(DISTINCT s) as student_count,
                     count(DISTINCT s2) as students_with_errors,
                     sum(e.occurrence_count) as total_errors
                RETURN 
                    c.course_id as course_id,
                    c.name as course_name,
                    student_count as participation,
                    students_with_errors,
                    total_errors,
                    CASE 
                        WHEN student_count > 0 
                        THEN toFloat(students_with_errors) / student_count 
                        ELSE 0.0 
                    END as error_rate
                ORDER BY participation DESC
                """
                
                result = await session.run(course_query)
                course_records = await result.data()
                
                course_metrics = []
                for record in course_records:
                    course_metrics.append({
                        "course_id": record["course_id"],
                        "course_name": record["course_name"],
                        "participation": record["participation"],
                        "students_with_errors": record["students_with_errors"],
                        "total_errors": record["total_errors"] or 0,
                        "error_rate": round(record["error_rate"], 4),
                    })
                
                logger.info(
                    "course_effectiveness_analyzed",
                    courses_count=len(course_metrics),
                )
                
                return CourseEffectivenessAnalysis(
                    course_metrics=course_metrics,
                )
        except Exception as e:
            logger.error(
                "course_effectiveness_analysis_failed",
                error=str(e),
            )
            raise RuntimeError(f"Failed to analyze course effectiveness: {e}")
    
    async def analyze_interaction_patterns(
        self,
        min_network_size: int = 2,
    ) -> InteractionPatternAnalysis:
        """分析互动模式
        
        识别活跃的学生社交网络和孤立的学生节点
        
        Args:
            min_network_size: 最小网络规模（节点数）
            
        Returns:
            互动模式分析结果
            
        Raises:
            RuntimeError: 如果数据库操作失败
        """
        try:
            async with neo4j_connection.get_session() as session:
                # 识别社交网络（连接度高的学生群组）
                network_query = """
                MATCH (s:Student)-[r:CHAT_WITH|LIKES]-(other:Student)
                WITH s, count(DISTINCT other) as connection_count, collect(DISTINCT other.student_id) as connected_students
                WHERE connection_count >= $min_size
                RETURN 
                    s.student_id as student_id,
                    s.name as student_name,
                    connection_count,
                    connected_students
                ORDER BY connection_count DESC
                LIMIT 20
                """
                
                result = await session.run(network_query, min_size=min_network_size)
                network_records = await result.data()
                
                social_networks = []
                for record in network_records:
                    social_networks.append({
                        "student_id": record["student_id"],
                        "student_name": record["student_name"],
                        "connection_count": record["connection_count"],
                        "connected_students": record["connected_students"],
                    })
                
                # 识别孤立学生（没有互动关系）
                isolated_query = """
                MATCH (s:Student)
                WHERE NOT (s)-[:CHAT_WITH|LIKES]-(:Student)
                RETURN 
                    s.student_id as student_id,
                    s.name as student_name,
                    s.grade as grade
                LIMIT 50
                """
                
                result = await session.run(isolated_query)
                isolated_records = await result.data()
                
                isolated_students = []
                for record in isolated_records:
                    isolated_students.append({
                        "student_id": record["student_id"],
                        "student_name": record["student_name"],
                        "grade": record["grade"],
                    })
                
                # 互动统计
                stats_query = """
                MATCH (s:Student)
                OPTIONAL MATCH (s)-[r:CHAT_WITH|LIKES]-(:Student)
                WITH count(DISTINCT s) as total_students,
                     count(DISTINCT CASE WHEN r IS NOT NULL THEN s END) as students_with_interactions,
                     count(r) as total_interactions
                RETURN 
                    total_students,
                    students_with_interactions,
                    total_interactions,
                    CASE 
                        WHEN total_students > 0 
                        THEN toFloat(students_with_interactions) / total_students 
                        ELSE 0.0 
                    END as interaction_rate
                """
                
                result = await session.run(stats_query)
                stats_record = await result.single()
                
                interaction_statistics = {
                    "total_students": stats_record["total_students"],
                    "students_with_interactions": stats_record["students_with_interactions"],
                    "total_interactions": stats_record["total_interactions"],
                    "interaction_rate": round(stats_record["interaction_rate"], 4),
                }
                
                logger.info(
                    "interaction_patterns_analyzed",
                    social_networks_count=len(social_networks),
                    isolated_students_count=len(isolated_students),
                )
                
                return InteractionPatternAnalysis(
                    social_networks=social_networks,
                    isolated_students=isolated_students,
                    interaction_statistics=interaction_statistics,
                )
        except Exception as e:
            logger.error(
                "interaction_patterns_analysis_failed",
                error=str(e),
            )
            raise RuntimeError(f"Failed to analyze interaction patterns: {e}")
    
    async def generate_report(
        self,
        include_graph_stats: bool = True,
        include_student_performance: bool = True,
        include_course_effectiveness: bool = True,
        include_interaction_patterns: bool = True,
    ) -> AnalysisReport:
        """生成完整的分析报告
        
        Args:
            include_graph_stats: 是否包含图谱统计
            include_student_performance: 是否包含学生表现分析
            include_course_effectiveness: 是否包含课程效果分析
            include_interaction_patterns: 是否包含互动模式分析
            
        Returns:
            完整的分析报告
            
        Raises:
            RuntimeError: 如果报告生成失败
        """
        try:
            # 创建默认报告组件
            default_stats = GraphStatistics(0, {}, 0, {}, datetime.utcnow())
            default_student_perf = StudentPerformanceAnalysis([], [], {})
            default_course_eff = CourseEffectivenessAnalysis([])
            default_interaction_pat = InteractionPatternAnalysis([], [], {})
            
            # 生成图谱统计（如果包含）
            graph_stats = default_stats
            if include_graph_stats:
                try:
                    graph_stats = await self.generate_graph_statistics()
                except Exception as e:
                    logger.warning("graph_statistics_generation_failed", error=str(e))
            
            # 生成学生表现分析（如果包含）
            student_perf = default_student_perf
            if include_student_performance:
                try:
                    student_perf = await self.analyze_student_performance()
                except Exception as e:
                    logger.warning("student_performance_analysis_failed", error=str(e))
            
            # 生成课程效果分析（如果包含）
            course_eff = default_course_eff
            if include_course_effectiveness:
                try:
                    course_eff = await self.analyze_course_effectiveness()
                except Exception as e:
                    logger.warning("course_effectiveness_analysis_failed", error=str(e))
            
            # 生成互动模式分析（如果包含）
            interaction_pat = default_interaction_pat
            if include_interaction_patterns:
                try:
                    interaction_pat = await self.analyze_interaction_patterns()
                except Exception as e:
                    logger.warning("interaction_patterns_analysis_failed", error=str(e))
            
            # 创建报告
            report = AnalysisReport(
                graph_statistics=graph_stats,
                student_performance=student_perf,
                course_effectiveness=course_eff,
                interaction_patterns=interaction_pat,
                generated_at=datetime.utcnow(),
            )
            
            logger.info("analysis_report_generated")
            
            return report
        except Exception as e:
            logger.error(
                "report_generation_failed",
                error=str(e),
            )
            raise RuntimeError(f"Failed to generate report: {e}")
    
    async def export_report(
        self,
        report: AnalysisReport,
        format: str = ReportFormat.JSON,
    ) -> bytes:
        """导出报告
        
        Args:
            report: 分析报告
            format: 导出格式（json 或 pdf）
            
        Returns:
            报告内容（字节）
            
        Raises:
            ValueError: 如果格式不支持
            RuntimeError: 如果导出失败
        """
        try:
            if format == ReportFormat.JSON:
                # 导出为 JSON
                json_str = report.to_json()
                logger.info("report_exported_as_json")
                return json_str.encode("utf-8")
            
            elif format == ReportFormat.PDF:
                # 导出为 PDF
                pdf_bytes = await self._generate_pdf_report(report)
                logger.info("report_exported_as_pdf")
                return pdf_bytes
            
            else:
                raise ValueError(f"Unsupported format: {format}")
        except Exception as e:
            logger.error(
                "report_export_failed",
                format=format,
                error=str(e),
            )
            raise RuntimeError(f"Failed to export report: {e}")
    
    async def _generate_pdf_report(self, report: AnalysisReport) -> bytes:
        """生成 PDF 格式报告
        
        Args:
            report: 分析报告
            
        Returns:
            PDF 内容（字节）
            
        Raises:
            RuntimeError: 如果 PDF 生成失败
        """
        try:
            # 尝试导入 reportlab
            try:
                from reportlab.lib.pagesizes import letter, A4
                from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
                from reportlab.lib.units import inch
                from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
                from reportlab.lib import colors
                from reportlab.pdfbase import pdfmetrics
                from reportlab.pdfbase.ttfonts import TTFont
            except ImportError:
                logger.warning("reportlab_not_installed")
                raise RuntimeError(
                    "PDF export requires reportlab library. "
                    "Install it with: pip install reportlab"
                )
            
            # 创建 PDF 文档
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4)
            story = []
            
            # 样式
            styles = getSampleStyleSheet()
            title_style = styles['Title']
            heading_style = styles['Heading2']
            normal_style = styles['Normal']
            
            # 标题
            story.append(Paragraph("教育知识图谱分析报告", title_style))
            story.append(Spacer(1, 0.3 * inch))
            
            # 生成时间
            story.append(Paragraph(
                f"生成时间: {report.generated_at.strftime('%Y-%m-%d %H:%M:%S')}",
                normal_style
            ))
            story.append(Spacer(1, 0.3 * inch))
            
            # 图谱统计
            story.append(Paragraph("1. 图谱统计", heading_style))
            story.append(Spacer(1, 0.1 * inch))
            
            stats = report.graph_statistics
            stats_data = [
                ["指标", "数值"],
                ["节点总数", str(stats.total_nodes)],
                ["关系总数", str(stats.total_relationships)],
            ]
            
            # 添加节点类型分布
            for node_type, count in stats.node_type_distribution.items():
                stats_data.append([f"  {node_type} 节点", str(count)])
            
            stats_table = Table(stats_data)
            stats_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))
            story.append(stats_table)
            story.append(Spacer(1, 0.3 * inch))
            
            # 学生表现分析
            story.append(Paragraph("2. 学生表现分析", heading_style))
            story.append(Spacer(1, 0.1 * inch))
            
            perf = report.student_performance
            story.append(Paragraph(
                f"高频错误数量: {len(perf.high_frequency_errors)}",
                normal_style
            ))
            story.append(Paragraph(
                f"需要关注的学生数量: {len(perf.students_needing_attention)}",
                normal_style
            ))
            story.append(Spacer(1, 0.3 * inch))
            
            # 课程效果分析
            story.append(Paragraph("3. 课程效果分析", heading_style))
            story.append(Spacer(1, 0.1 * inch))
            
            course_data = [["课程名称", "参与人数", "错误率"]]
            for course in report.course_effectiveness.course_metrics[:10]:
                course_data.append([
                    course["course_name"],
                    str(course["participation"]),
                    f"{course['error_rate']:.2%}",
                ])
            
            if len(course_data) > 1:
                course_table = Table(course_data)
                course_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ]))
                story.append(course_table)
            story.append(Spacer(1, 0.3 * inch))
            
            # 互动模式分析
            story.append(Paragraph("4. 互动模式分析", heading_style))
            story.append(Spacer(1, 0.1 * inch))
            
            interaction = report.interaction_patterns
            story.append(Paragraph(
                f"活跃社交网络数量: {len(interaction.social_networks)}",
                normal_style
            ))
            story.append(Paragraph(
                f"孤立学生数量: {len(interaction.isolated_students)}",
                normal_style
            ))
            story.append(Paragraph(
                f"互动率: {interaction.interaction_statistics.get('interaction_rate', 0):.2%}",
                normal_style
            ))
            
            # 构建 PDF
            doc.build(story)
            
            # 获取 PDF 内容
            pdf_bytes = buffer.getvalue()
            buffer.close()
            
            return pdf_bytes
        except Exception as e:
            logger.error(
                "pdf_generation_failed",
                error=str(e),
            )
            raise RuntimeError(f"Failed to generate PDF report: {e}")


# 全局服务实例
report_service = ReportService()
