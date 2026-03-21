import { BadRequestException, Injectable } from "@nestjs/common";
import { Prisma } from "@prisma/client";
import { PrismaService } from "../../shared/utils/prisma.service";
import { GraphData, Link, Node } from "../../shared/types/graph-data.type";

type GraphQuery = {
  scenarioCode?: string;
  schoolId?: string;
  gradeId?: string;
  classId?: string;
  from?: string;
  to?: string;
};

@Injectable()
export class GraphService {
  constructor(private prisma: PrismaService) {}

  async getGraphData(params: GraphQuery) {
    const where = await this.buildSessionWhere(params);

    const sessions = await this.prisma.interactionSession.findMany({
      where,
      select: { id: true },
    });

    if (sessions.length === 0) {
      return {
        data: {
          nodes: [],
          links: [],
          meta: {
            nodeCount: 0,
            linkCount: 0,
            scenarioCode: params.scenarioCode ?? "ALL",
          },
        },
        meta: null,
        error: null,
      };
    }

    const schoolNames = await this.buildSchoolNameMap();
    const gradeNames = await this.buildGradeNameMap();
    const classNames = await this.buildClassNameMap();

    const sessionIds = sessions.map((session) => session.id);

    const interactions = await this.prisma.interaction.findMany({
      where: { sessionId: { in: sessionIds } },
      include: {
        sourceNode: {
          include: {
            studentProfile: true,
            teacherProfile: true,
            knowledgeProfile: true,
          },
        },
        targetNode: {
          include: {
            studentProfile: true,
            teacherProfile: true,
            knowledgeProfile: true,
          },
        },
      },
    });

    const nodeMap = new Map<string, Node>();

    for (const interaction of interactions) {
      this.putNode(
        nodeMap,
        interaction.sourceNode,
        schoolNames,
        gradeNames,
        classNames,
      );
      this.putNode(
        nodeMap,
        interaction.targetNode,
        schoolNames,
        gradeNames,
        classNames,
      );
    }

    const mapInteractionType = (type: string): "PHYSICAL" | "PLATFORM" => {
      const platformTypes = ["DISCUSS", "ASK", "ANSWER", "EVALUATE", "AI_QA"];
      return platformTypes.includes(type) ? "PLATFORM" : "PHYSICAL";
    };

    const links: Link[] = interactions.map((interaction) => ({
      source: interaction.sourceNodeId,
      target: interaction.targetNodeId,
      value: Number(interaction.strength),
      type: mapInteractionType(interaction.interactionType),
      actionType: interaction.actionType,
    }));

    const nodes = Array.from(nodeMap.values());

    return {
      data: {
        nodes,
        links,
        meta: {
          nodeCount: nodes.length,
          linkCount: links.length,
          scenarioCode: params.scenarioCode ?? "ALL",
        },
      } as GraphData,
      meta: null,
      error: null,
    };
  }

  async getScenarioStats(params: Omit<GraphQuery, "scenarioCode">) {
    const scenarios = await this.prisma.learningScenario.findMany({
      where: { isActive: true },
      select: { id: true, code: true, nameZh: true },
      orderBy: { sortOrder: "asc" },
    });

    const stats = [] as Array<{
      scenarioCode: string;
      scenarioNameZh: string;
      nodeCount: number;
      linkCount: number;
      avgStrength: number;
      density: number;
      studentTeacherRatio: number;
    }>;

    for (const scenario of scenarios) {
      const sessions = await this.prisma.interactionSession.findMany({
        where: {
          scenarioId: scenario.id,
          ...(params.schoolId ? { schoolId: params.schoolId } : {}),
          ...(params.gradeId ? { gradeId: params.gradeId } : {}),
          ...(params.classId ? { classId: params.classId } : {}),
          ...(params.from || params.to
            ? {
                occurredAt: {
                  ...(params.from ? { gte: new Date(params.from) } : {}),
                  ...(params.to ? { lte: new Date(params.to) } : {}),
                },
              }
            : {}),
        },
        select: { id: true },
      });

      if (sessions.length === 0) {
        stats.push({
          scenarioCode: scenario.code,
          scenarioNameZh: scenario.nameZh,
          nodeCount: 0,
          linkCount: 0,
          avgStrength: 0,
          density: 0,
          studentTeacherRatio: 0,
        });
        continue;
      }

      const interactions = await this.prisma.interaction.findMany({
        where: { sessionId: { in: sessions.map((s) => s.id) } },
        select: {
          sourceNodeId: true,
          targetNodeId: true,
          strength: true,
          sourceNode: { select: { nodeType: true } },
          targetNode: { select: { nodeType: true } },
        },
      });

      const nodeIds = new Set<string>();
      let totalStrength = 0;
      let studentNodeCount = 0;
      let teacherNodeCount = 0;
      const seenNodeTypes = new Map<string, string>();

      for (const item of interactions) {
        nodeIds.add(item.sourceNodeId);
        nodeIds.add(item.targetNodeId);
        totalStrength += Number(item.strength);

        if (!seenNodeTypes.has(item.sourceNodeId)) {
          seenNodeTypes.set(item.sourceNodeId, item.sourceNode.nodeType);
        }
        if (!seenNodeTypes.has(item.targetNodeId)) {
          seenNodeTypes.set(item.targetNodeId, item.targetNode.nodeType);
        }
      }

      for (const nodeType of seenNodeTypes.values()) {
        if (nodeType === "STUDENT") {
          studentNodeCount += 1;
        }
        if (nodeType === "TEACHER") {
          teacherNodeCount += 1;
        }
      }

      const nodeCount = nodeIds.size;
      const linkCount = interactions.length;
      const avgStrength = linkCount === 0 ? 0 : totalStrength / linkCount;
      const density =
        nodeCount <= 1 ? 0 : linkCount / (nodeCount * (nodeCount - 1));
      const studentTeacherRatio =
        teacherNodeCount === 0 ? 0 : studentNodeCount / teacherNodeCount;

      stats.push({
        scenarioCode: scenario.code,
        scenarioNameZh: scenario.nameZh,
        nodeCount,
        linkCount,
        avgStrength: Number(avgStrength.toFixed(3)),
        density: Number(density.toFixed(3)),
        studentTeacherRatio: Number(studentTeacherRatio.toFixed(3)),
      });
    }

    return {
      data: stats,
      meta: null,
      error: null,
    };
  }

  private async buildSessionWhere(params: GraphQuery) {
    let scenarioId: string | undefined;

    if (params.scenarioCode) {
      const scenario = await this.prisma.learningScenario.findUnique({
        where: { code: params.scenarioCode },
        select: { id: true },
      });

      if (!scenario) {
        throw new BadRequestException("SCENARIO_CODE_INVALID");
      }

      scenarioId = scenario.id;
    }

    return {
      ...(scenarioId ? { scenarioId } : {}),
      ...(params.schoolId ? { schoolId: params.schoolId } : {}),
      ...(params.gradeId ? { gradeId: params.gradeId } : {}),
      ...(params.classId ? { classId: params.classId } : {}),
      ...(params.from || params.to
        ? {
            occurredAt: {
              ...(params.from ? { gte: new Date(params.from) } : {}),
              ...(params.to ? { lte: new Date(params.to) } : {}),
            },
          }
        : {}),
    } as Prisma.InteractionSessionWhereInput;
  }

  private putNode(
    nodeMap: Map<string, Node>,
    node: any,
    schoolNames: Map<string, string>,
    gradeNames: Map<string, string>,
    classNames: Map<string, string>,
  ) {
    if (nodeMap.has(node.id)) {
      return;
    }

    if (node.nodeType === "STUDENT") {
      nodeMap.set(node.id, {
        id: node.id,
        type: "STUDENT",
        name: node.displayName,
        group: 3,
        val: 8,
        studentProfile: {
          school: node.schoolId
            ? schoolNames.get(node.schoolId) ?? node.schoolId
            : null,
          grade: node.gradeId
            ? gradeNames.get(node.gradeId) ?? node.gradeId
            : null,
          classId: node.classId
            ? classNames.get(node.classId) ?? node.classId
            : null,
          learningStylePreference:
            node.studentProfile?.learningStylePreference ?? null,
          personality: node.studentProfile?.personality ?? null,
          groupBehavior: node.studentProfile?.groupBehavior ?? null,
        },
      });
      return;
    }

    if (node.nodeType === "TEACHER") {
      nodeMap.set(node.id, {
        id: node.id,
        type: "TEACHER",
        name: node.displayName,
        group: 1,
        val: 25,
        teacherProfile: {
          school: node.schoolId
            ? schoolNames.get(node.schoolId) ?? node.schoolId
            : null,
          teachingGrade:
            node.teacherProfile?.teachingGrade ??
            (node.gradeId
              ? gradeNames.get(node.gradeId) ?? node.gradeId
              : null),
          teachingClass:
            node.teacherProfile?.teachingClass ??
            (node.classId
              ? classNames.get(node.classId) ?? node.classId
              : null),
          subject: node.teacherProfile?.subject ?? null,
        },
      });
      return;
    }

    nodeMap.set(node.id, {
      id: node.id,
      type: "KNOWLEDGE",
      name: node.displayName,
      group: 2,
      val: 15,
      knowledgeProfile: {
        content: node.knowledgeProfile?.content ?? null,
        type: node.knowledgeProfile?.knowledgeType ?? null,
        category: node.knowledgeProfile?.category ?? null,
        parentId: node.knowledgeProfile?.parentNodeId ?? null,
      },
    });
  }

  private async buildSchoolNameMap(): Promise<Map<string, string>> {
    const schoolNames = new Map<string, string>();
    const schools = await this.prisma.school.findMany({
      select: { id: true, name: true },
    });
    for (const school of schools) {
      schoolNames.set(school.id, school.name);
    }
    return schoolNames;
  }

  private async buildGradeNameMap(): Promise<Map<string, string>> {
    const gradeNames = new Map<string, string>();
    const grades = await this.prisma.grade.findMany({
      select: { id: true, gradeName: true },
    });
    for (const grade of grades) {
      gradeNames.set(grade.id, grade.gradeName);
    }
    return gradeNames;
  }

  private async buildClassNameMap(): Promise<Map<string, string>> {
    const classNames = new Map<string, string>();
    const classes = await this.prisma.schoolClass.findMany({
      select: { id: true, className: true },
    });
    for (const cls of classes) {
      classNames.set(cls.id, cls.className);
    }
    return classNames;
  }
}
