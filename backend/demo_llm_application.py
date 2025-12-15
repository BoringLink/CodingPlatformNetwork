#!/usr/bin/env python3
"""
LLM应用演示脚本

演示如何使用LLM服务处理数据并构建知识图谱
"""

import asyncio
import json
from typing import List, Dict, Any

from app.services.llm_service import LLMAnalysisService, CourseContext
from app.services.graph_service import (
    GraphManagementService,
    NodeType,
    RelationshipType,
)
from app.services.cache_service import CacheService
from app.config import settings
from app.database import neo4j_connection
from neo4j import AsyncGraphDatabase


def load_test_data() -> Dict[str, List[Dict[str, Any]]]:
    """加载测试数据"""
    return {
        "interactions": [
            {
                "interaction_id": "i1",
                "from_user": "张三",
                "to_user": "李四",
                "content": "李四，我不太理解分数加法，能帮我解释一下吗？",
                "timestamp": "2024-01-01T10:00:00Z",
            },
            {
                "interaction_id": "i2",
                "from_user": "李四",
                "to_user": "张三",
                "content": "当然可以，分数加法需要先通分，然后分子相加，分母不变。",
                "timestamp": "2024-01-01T10:05:00Z",
            },
            {
                "interaction_id": "i3",
                "from_user": "王五",
                "to_user": "张三",
                "content": "张三，我也不太理解这个知识点，能一起讨论吗？",
                "timestamp": "2024-01-01T10:10:00Z",
            },
        ],
        "error_records": [
            {
                "error_id": "e1",
                "student": "张三",
                "course": "数学101",
                "content": "学生在计算3/4 + 1/2时得到了4/6，计算错误",
                "timestamp": "2024-01-02T09:30:00Z",
            },
            {
                "error_id": "e2",
                "student": "王五",
                "course": "数学101",
                "content": "学生在计算5/8 - 1/4时得到了4/4，计算错误",
                "timestamp": "2024-01-02T10:00:00Z",
            },
        ],
        "course_contents": [
            {
                "course_id": "c1",
                "course_name": "数学101",
                "content": "分数是数学中的重要概念，分数加法需要先通分，然后分子相加，分母不变。通分是指将不同分母的分数转换为相同分母的分数，以便进行加减运算。",
            }
        ],
    }


async def process_interaction(
    llm_service: LLMAnalysisService,
    graph_service: GraphManagementService,
    interaction: Dict[str, Any],
) -> None:
    """处理互动数据"""
    print(f"\n=== 处理互动: {interaction['interaction_id']} ===")
    print(f"内容: {interaction['content']}")

    # 1. 分析互动内容
    analysis = await llm_service.analyze_interaction(interaction["content"])
    print(f"互动分析结果: 情感={analysis.sentiment}, 主题={analysis.topics}")

    # 2. 提取实体和关系
    entities = [
        {"text": interaction["from_user"], "type": "Student"},
        {"text": interaction["to_user"], "type": "Student"},
    ]
    relationships = await llm_service.extract_relationships(
        interaction["content"], entities
    )
    print(f"提取的关系: {relationships}")

    # 3. 创建或更新节点
    node_map = {}
    for entity in entities:
        # 将字符串类型转换为NodeType枚举
        node_type = NodeType(entity["type"].upper())

        # 创建节点属性
        node_properties = {"name": entity["text"]}

        # 为不同节点类型添加特定属性
        if node_type == NodeType.STUDENT:
            node_properties["student_id"] = entity["text"].lower()

        # 创建节点
        node = await graph_service.create_node(node_type, node_properties)
        node_map[entity["text"]] = node

    # 4. 创建关系
    for rel in relationships:
        # 获取节点
        from_node = node_map.get(rel["from_entity"])
        to_node = node_map.get(rel["to_entity"])

        if from_node and to_node:
            # 将字符串关系类型转换为RelationshipType枚举
            rel_type = RelationshipType(rel["relationship_type"].upper())

            await graph_service.create_relationship(
                from_node.id, to_node.id, rel_type, rel.get("properties", {})
            )

    print(f"互动处理完成: {interaction['interaction_id']}")


async def process_error_record(
    llm_service: LLMAnalysisService,
    graph_service: GraphManagementService,
    error_record: Dict[str, Any],
) -> None:
    """处理错误记录"""
    print(f"\n=== 处理错误记录: {error_record['error_id']} ===")
    print(f"内容: {error_record['content']}")

    # 1. 分析错误内容
    context = CourseContext(
        course_id=error_record["course"].lower(), course_name=error_record["course"]
    )
    analysis = await llm_service.analyze_error(error_record["content"], context)
    print(
        f"错误分析结果: 类型={analysis.error_type}, 知识点={analysis.related_knowledge_points}"
    )

    # 2. 提取实体和关系
    entities = [
        {"text": error_record["student"], "type": "Student"},
        {"text": error_record["course"], "type": "Course"},
        {"text": analysis.error_type, "type": "ErrorType"},
    ]
    for kp in analysis.related_knowledge_points:
        entities.append({"text": kp, "type": "KnowledgePoint"})

    relationships = await llm_service.extract_relationships(
        error_record["content"], entities
    )
    print(f"提取的关系: {relationships}")

    # 3. 创建或更新节点
    node_map = {}
    for entity in entities:
        # 将字符串类型转换为NodeType枚举
        node_type = NodeType(entity["type"].upper())

        # 创建节点属性
        node_properties = {"name": entity["text"]}

        # 为不同节点类型添加特定属性
        if node_type == NodeType.COURSE:
            node_properties["course_id"] = entity["text"].lower()
        elif node_type == NodeType.KNOWLEDGE_POINT:
            node_properties["knowledge_point_id"] = (
                entity["text"].lower().replace(" ", "_")
            )
        elif node_type == NodeType.ERROR_TYPE:
            node_properties["error_type_id"] = entity["text"].lower().replace(" ", "_")

        # 创建节点
        node = await graph_service.create_node(node_type, node_properties)
        node_map[entity["text"]] = node

    # 4. 创建关系
    for rel in relationships:
        if rel["from_entity"] in node_map and rel["to_entity"] in node_map:
            # 将字符串关系类型转换为RelationshipType枚举
            rel_type = RelationshipType(rel["relationship_type"].upper())

            await graph_service.create_relationship(
                node_map[rel["from_entity"]].id,
                node_map[rel["to_entity"]].id,
                rel_type,
                rel.get("properties", {}),
            )

    print(f"错误记录处理完成: {error_record['error_id']}")


async def process_course_content(
    llm_service: LLMAnalysisService,
    graph_service: GraphManagementService,
    course_content: Dict[str, Any],
) -> None:
    """处理课程内容"""
    print(f"\n=== 处理课程内容: {course_content['course_id']} ===")
    print(f"课程: {course_content['course_name']}")

    # 1. 提取知识点
    knowledge_points = await llm_service.extract_knowledge_points(
        course_content["content"]
    )
    print(f"提取的知识点: {[kp.name for kp in knowledge_points]}")

    # 2. 创建或更新课程节点
    course_node = await graph_service.create_node(
        NodeType.COURSE,
        {
            "name": course_content["course_name"],
            "course_id": course_content["course_id"],
        },
    )

    # 3. 创建或更新知识点节点
    kp_node_map = {}
    for kp in knowledge_points:
        kp_node = await graph_service.create_node(
            NodeType.KNOWLEDGE_POINT,
            {
                "name": kp.name,
                "knowledge_point_id": kp.id,
                "description": kp.description,
            },
        )
        kp_node_map[kp.id] = kp_node

    # 4. 创建课程包含知识点的关系
    for kp in knowledge_points:
        await graph_service.create_relationship(
            course_node.id, kp_node_map[kp.id].id, RelationshipType.CONTAINS
        )

    # 5. 创建知识点依赖关系
    for kp in knowledge_points:
        for dep_id in kp.dependencies:
            if dep_id in kp_node_map:
                await graph_service.create_relationship(
                    kp_node_map[kp.id].id,
                    kp_node_map[dep_id].id,
                    RelationshipType.DEPENDS_ON,
                )

    print(f"课程内容处理完成: {course_content['course_id']}")


async def analyze_knowledge_statistics(
    llm_service: LLMAnalysisService, records: List[Dict[str, Any]]
) -> None:
    """分析知识点统计数据"""
    print(f"\n=== 分析知识点统计 ===")
    stats = await llm_service.analyze_knowledge_statistics(records)

    print(f"知识点出现次数: {stats['knowledge_point_counts']}")
    print(f"知识热点: {stats['hot_topics']}")
    print(f"知识点集群: {stats['knowledge_clusters']}")

    print(f"知识点统计分析完成")


async def analyze_student_attention(
    llm_service: LLMAnalysisService, interactions: List[Dict[str, Any]]
) -> None:
    """分析学生群体关注度"""
    print(f"\n=== 分析学生群体关注度 ===")
    attention_stats = await llm_service.analyze_student_attention(interactions)

    print(f"学生关注度分数: {attention_stats['student_attention_scores']}")
    print(f"关注度排名: {attention_stats['attention_rankings']}")
    print(f"社交影响力: {attention_stats['social_influence']}")

    print(f"学生群体关注度分析完成")


async def main():
    """主函数"""
    print("=== LLM应用演示 ===")

    # 1. 初始化服务
    print("\n1. 初始化服务...")

    # 初始化缓存服务
    cache_service = CacheService()
    await cache_service.connect()

    # 初始化LLM服务
    llm_service = LLMAnalysisService(cache_service=cache_service)

    # 初始化图服务
    await neo4j_connection.connect()
    graph_service = GraphManagementService()

    # 2. 加载测试数据
    print("\n2. 加载测试数据...")
    test_data = load_test_data()

    # 3. 处理数据
    print("\n3. 处理数据...")

    # 处理课程内容
    for course_content in test_data["course_contents"]:
        await process_course_content(llm_service, graph_service, course_content)

    # 处理互动数据
    for interaction in test_data["interactions"]:
        await process_interaction(llm_service, graph_service, interaction)

    # 处理错误记录
    for error_record in test_data["error_records"]:
        await process_error_record(llm_service, graph_service, error_record)

    # 4. 分析数据
    print("\n4. 分析数据...")

    # 分析知识点统计
    await analyze_knowledge_statistics(llm_service, test_data["course_contents"])

    # 分析学生群体关注度
    await analyze_student_attention(llm_service, test_data["interactions"])

    # 5. 清理资源
    print("\n5. 清理资源...")
    await cache_service.close()
    await driver.close()

    print("\n=== 演示完成 ===")


if __name__ == "__main__":
    asyncio.run(main())
