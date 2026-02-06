import { Injectable } from "@nestjs/common";
import { PrismaService } from "../../shared/utils/prisma.service";
import { CreateKnowledgeDto, UpdateKnowledgeDto } from "./knowledge.dto";

@Injectable()
export class KnowledgeService {
  constructor(private prisma: PrismaService) {}

  async findAll(params: { grade?: string; type?: string; parentId?: string }) {
    const { grade, type, parentId } = params;

    const where = {
      ...(grade && { grade }),
      ...(type && { type }),
      ...(parentId && { parentId }),
    };

    const knowledgePoints = await this.prisma.knowledge.findMany({
      where,
      orderBy: { createdAt: "desc" },
    });

    return knowledgePoints.map(kp => ({
      ...kp,
      relatedKnowledgeIds: JSON.parse(kp.relatedKnowledgeIds),
      relatedKnowledgeNames: JSON.parse(kp.relatedKnowledgeNames),
    }));
  }

  async findOne(id: string) {
    const knowledgePoint = await this.prisma.knowledge.findUnique({ where: { id } });
    if (!knowledgePoint) return null;
    
    return {
      ...knowledgePoint,
      relatedKnowledgeIds: JSON.parse(knowledgePoint.relatedKnowledgeIds),
      relatedKnowledgeNames: JSON.parse(knowledgePoint.relatedKnowledgeNames),
    };
  }

  async create(data: CreateKnowledgeDto) {
    return {
      ...(await this.prisma.knowledge.create({
        data: {
          content: data.content,
          knowledgePoint: data.knowledgePoint,
          grade: data.grade,
          type: data.type,
          parentId: data.parentId || null,
          parentName: data.parentName || null,
          relatedKnowledgeIds: JSON.stringify(data.relatedKnowledgeIds || []),
          relatedKnowledgeNames: JSON.stringify(data.relatedKnowledgeNames || []),
        },
      })),
      relatedKnowledgeIds: data.relatedKnowledgeIds || [],
      relatedKnowledgeNames: data.relatedKnowledgeNames || [],
    };
  }

  async update(id: string, data: UpdateKnowledgeDto) {
    const updatedKnowledge = await this.prisma.knowledge.update({
      where: { id },
      data: {
        ...data,
        relatedKnowledgeIds: data.relatedKnowledgeIds ? JSON.stringify(data.relatedKnowledgeIds) : undefined,
        relatedKnowledgeNames: data.relatedKnowledgeNames ? JSON.stringify(data.relatedKnowledgeNames) : undefined,
      },
    });

    return {
      ...updatedKnowledge,
      relatedKnowledgeIds: JSON.parse(updatedKnowledge.relatedKnowledgeIds),
      relatedKnowledgeNames: JSON.parse(updatedKnowledge.relatedKnowledgeNames),
    };
  }



  async delete(id: string) {
    await this.prisma.knowledge.delete({ where: { id } });
    return { message: "知识点删除成功" };
  }
}
