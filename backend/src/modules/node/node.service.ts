import { Injectable } from "@nestjs/common";
import { Prisma } from "@prisma/client";
import { PrismaService } from "../../shared/utils/prisma.service";
import { CreateNodeDto, QueryNodeDto } from "./node.dto";

@Injectable()
export class NodeService {
  constructor(private readonly prisma: PrismaService) {}

  async queryNodes(query: QueryNodeDto) {
    const { nodeType, schoolId, gradeId, classId, page, pageSize } = query;

    const where: Prisma.GraphNodeWhereInput = {
      ...(nodeType ? { nodeType } : {}),
      ...(schoolId ? { schoolId } : {}),
      ...(gradeId ? { gradeId } : {}),
      ...(classId ? { classId } : {}),
    };

    const [items, total] = await this.prisma.$transaction([
      this.prisma.graphNode.findMany({
        where,
        include: {
          studentProfile: true,
          teacherProfile: true,
          knowledgeProfile: true,
        },
        orderBy: { createdAt: "desc" },
        skip: (page - 1) * pageSize,
        take: pageSize,
      }),
      this.prisma.graphNode.count({ where }),
    ]);

    return {
      data: items,
      meta: {
        page,
        pageSize,
        total,
      },
      error: null,
    };
  }

  async createNode(dto: CreateNodeDto) {
    const created = await this.prisma.$transaction(async (tx) => {
      const node = await tx.graphNode.create({
        data: {
          nodeType: dto.nodeType,
          displayName: dto.displayName,
          schoolId: dto.schoolId ?? null,
          gradeId: dto.gradeId ?? null,
          classId: dto.classId ?? null,
        },
      });

      if (dto.nodeType === "STUDENT") {
        await tx.studentProfile.create({
          data: {
            nodeId: node.id,
            learningStylePreference:
              dto.profile?.learningStylePreference ?? null,
            personality: dto.profile?.personality ?? null,
            groupBehavior: dto.profile?.groupBehavior ?? null,
          },
        });
      }

      if (dto.nodeType === "TEACHER") {
        await tx.teacherProfile.create({
          data: {
            nodeId: node.id,
            teachingGrade: dto.profile?.teachingGrade ?? null,
            teachingClass: dto.profile?.teachingClass ?? null,
            subject: dto.profile?.subject ?? null,
          },
        });
      }

      if (dto.nodeType === "KNOWLEDGE") {
        await tx.knowledgeProfile.create({
          data: {
            nodeId: node.id,
            content: dto.profile?.content ?? dto.displayName,
            knowledgeType: dto.profile?.knowledgeType ?? "GENERAL",
            category: dto.profile?.category ?? null,
            parentNodeId: dto.profile?.parentNodeId ?? null,
          },
        });
      }

      return node;
    });

    return {
      data: created,
      meta: null,
      error: null,
    };
  }
}
