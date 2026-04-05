import { Injectable } from "@nestjs/common";
import { PrismaService } from "../../shared/utils/prisma.service";

@Injectable()
export class StudentService {
  constructor(private prisma: PrismaService) {}

  async getLatestCognitiveTemplate(studentNodeId: string) {
    const studentNode = await this.prisma.graphNode.findFirst({
      where: {
        id: studentNodeId,
        nodeType: "STUDENT",
      },
      include: {
        studentProfile: true,
      },
    });

    if (!studentNode) {
      return null;
    }

    const latestProfile = await this.prisma.studentCognitiveProfile.findFirst({
      where: { studentNodeId },
      orderBy: {
        generatedAt: "desc",
      },
      include: {
        dimensionScores: {
          include: {
            dimensionDef: true,
          },
          orderBy: {
            dimensionDef: {
              sortOrder: "asc",
            },
          },
        },
      },
    });

    return {
      data: {
        student: {
          id: studentNode.id,
          name: studentNode.displayName,
          school: studentNode.schoolId ?? null,
          grade: studentNode.gradeId ?? null,
          classId: studentNode.classId ?? null,
          learningStylePreference:
            studentNode.studentProfile?.learningStylePreference ?? null,
          personality: studentNode.studentProfile?.personality ?? null,
          groupBehavior: studentNode.studentProfile?.groupBehavior ?? null,
        },
        profile: latestProfile
          ? {
              profileVersion: latestProfile.profileVersion,
              generatedAt: latestProfile.generatedAt,
              totalScore: Number(latestProfile.totalScore),
            }
          : null,
        dimensions:
          latestProfile?.dimensionScores.map((item) => ({
            dimensionCode: item.dimensionCode,
            dimensionNameZh: item.dimensionDef.dimensionNameZh,
            category: item.dimensionDef.category,
            scoreValue: Number(item.scoreValue),
            scoreLevel: item.scoreLevel,
          })) ?? [],
      },
      meta: null,
      error: null,
    };
  }
}
