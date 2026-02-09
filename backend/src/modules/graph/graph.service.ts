import { Injectable } from '@nestjs/common';
import { PrismaService } from '../../shared/utils/prisma.service';
import { GraphData, Node, Link } from '../../shared/types/graph-data.type';

@Injectable()
export class GraphService {
  constructor(private prisma: PrismaService) {}

  async getGraphData(params: {
    scenario?: string;
    school?: string;
    grade?: string;
    classId?: string;
  }) {
    const {
      school,
      grade,
      classId,
    } = params;

    // 构建学生查询条件
    const studentWhere = {
      ...(school && { school }),
      ...(grade && { grade }),
      ...(classId && { classId }),
    };

    // 构建教师查询条件
    const teacherWhere = {
      ...(school && { school }),
    };

    // 构建知识点查询条件
    const knowledgeWhere = {
      ...(grade && { grade }),
    };

    // 并行查询所有数据
    const [students, teachers, knowledge, interactions] = await Promise.all([
      this.prisma.student.findMany({ where: studentWhere }),
      this.prisma.teacher.findMany({ where: teacherWhere }),
      this.prisma.knowledge.findMany({ where: knowledgeWhere }),
      this.prisma.interaction.findMany(),
    ]);

    // 构建节点数据
    const nodes: Node[] = [
      // 学生节点
      ...students.map(student => ({
        id: student.id,
        type: 'STUDENT' as const,
        name: student.name,
        group: 3,
        val: 8,
        studentProfile: {
          school: student.school,
          grade: student.grade,
          classId: student.classId,
          knowledgeReserve: student.knowledgeReserve,
          learningEngagement: student.learningEngagement,
          cognitiveLoad: student.cognitiveLoad,
          learningMotivation: student.learningMotivation,
          computationalThinking: student.computationalThinking,
          humanAiTrust: student.humanAiTrust,
          learningMethod: student.learningMethod,
          learningAttitude: student.learningAttitude,
        },
      })),
      // 教师节点
      ...teachers.map(teacher => ({
        id: teacher.id,
        type: 'TEACHER' as const,
        name: teacher.name,
        group: 1,
        val: 25,
        teacherProfile: {
          school: teacher.school,
          teachingGrade: teacher.teachingGrade,
          teachingClass: teacher.teachingClass,
        },
      })),
      // 知识点节点
      ...knowledge.map(k => {
        let relatedKnowledgeIds: string[] = [];
        let relatedKnowledgeNames: string[] = [];
        
        // 安全解析 JSON 字符串
        try {
          relatedKnowledgeIds = JSON.parse(k.relatedKnowledgeIds) || [];
          if (!Array.isArray(relatedKnowledgeIds)) {
            relatedKnowledgeIds = [];
          }
        } catch (error) {
          console.warn(`Failed to parse relatedKnowledgeIds for knowledge ${k.id}:`, error);
          relatedKnowledgeIds = [];
        }
        
        try {
          relatedKnowledgeNames = JSON.parse(k.relatedKnowledgeNames) || [];
          if (!Array.isArray(relatedKnowledgeNames)) {
            relatedKnowledgeNames = [];
          }
        } catch (error) {
          console.warn(`Failed to parse relatedKnowledgeNames for knowledge ${k.id}:`, error);
          relatedKnowledgeNames = [];
        }
        
        return {
          id: k.id,
          type: 'KNOWLEDGE' as const,
          name: k.knowledgePoint,
          group: 2,
          val: 15,
          knowledgeProfile: {
            content: k.content,
            type: k.type,
            parentId: k.parentId,
            parentName: k.parentName,
            relatedKnowledgeIds,
            relatedKnowledgeNames,
          },
        };
      }),
    ];

    // 构建节点ID集合用于快速查找
    const nodeIds = new Set(nodes.map(node => node.id));

    // 构建链接数据，过滤掉无效的链接
    const links: Link[] = interactions
      .filter(interaction => {
        // 只保留sourceId和targetId都在节点集合中的链接
        return nodeIds.has(interaction.sourceId) && nodeIds.has(interaction.targetId);
      })
      .map(interaction => ({
        source: interaction.sourceId,
        target: interaction.targetId,
        value: interaction.value,
        type: interaction.type,
      }));

    return { nodes, links } as GraphData;
  }
}