import "dotenv/config";
import { INestApplication } from "@nestjs/common";
import { Test, TestingModule } from "@nestjs/testing";
import { afterAll, beforeAll, describe, expect, it } from "@jest/globals";
import request from "supertest";
import { AppModule } from "../../src/app.module";
import { PrismaService } from "../../src/shared/utils/prisma.service";

describe("Graph API Integration (real DB)", () => {
  let app: INestApplication;
  let prisma: PrismaService;

  const scope = `graph_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`;

  let scenarioId: string | null = null;
  let schoolId: string | null = null;
  let gradeId: string | null = null;
  let classId: string | null = null;
  let sessionId: string | null = null;
  let nodeIds: string[] = [];
  let interactionIds: string[] = [];
  let scenarioCode = "";

  beforeAll(async () => {
    const moduleRef: TestingModule = await Test.createTestingModule({
      imports: [AppModule],
    }).compile();

    app = moduleRef.createNestApplication();
    await app.init();
    prisma = app.get(PrismaService);

    scenarioCode = `SC_${scope}`;

    const scenario = await prisma.learningScenario.create({
      data: {
        code: scenarioCode,
        nameZh: "图谱集成测试场景",
        sortOrder: 9998,
        isActive: true,
      },
      select: { id: true },
    });
    scenarioId = scenario.id;

    const school = await prisma.school.create({
      data: { name: `学校_${scope}` },
      select: { id: true },
    });
    schoolId = school.id;

    const grade = await prisma.grade.create({
      data: {
        schoolId: school.id,
        gradeName: `年级_${scope}`,
      },
      select: { id: true },
    });
    gradeId = grade.id;

    const classEntity = await prisma.schoolClass.create({
      data: {
        gradeId: grade.id,
        className: `班级_${scope}`,
      },
      select: { id: true },
    });
    classId = classEntity.id;

    const nodes = await Promise.all([
      prisma.graphNode.create({
        data: {
          nodeType: "STUDENT",
          displayName: `学生_${scope}`,
          schoolId: school.id,
          gradeId: grade.id,
          classId: classEntity.id,
          studentProfile: {
            create: {
              learningStylePreference: "主动",
              personality: "外向",
              groupBehavior: "协作",
            },
          },
        },
        select: { id: true },
      }),
      prisma.graphNode.create({
        data: {
          nodeType: "TEACHER",
          displayName: `教师_${scope}`,
          schoolId: school.id,
          gradeId: grade.id,
          classId: classEntity.id,
          teacherProfile: {
            create: {
              subject: "数学",
              teachingGrade: "三年级",
              teachingClass: "1班",
            },
          },
        },
        select: { id: true },
      }),
      prisma.graphNode.create({
        data: {
          nodeType: "KNOWLEDGE",
          displayName: `知识点_${scope}`,
          knowledgeProfile: {
            create: {
              content: "测试知识点内容",
              knowledgeType: "知识点",
              category: "测试分类",
            },
          },
        },
        select: { id: true },
      }),
    ]);

    nodeIds = nodes.map((item) => item.id);

    const session = await prisma.interactionSession.create({
      data: {
        scenarioId: scenario.id,
        sessionName: `会话_${scope}`,
        occurredAt: new Date(),
        schoolId: school.id,
        gradeId: grade.id,
        classId: classEntity.id,
      },
      select: { id: true },
    });
    sessionId = session.id;

    const [studentId, teacherId, knowledgeId] = nodeIds;

    const interactions = await Promise.all([
      prisma.interaction.create({
        data: {
          sessionId: session.id,
          sourceNodeId: studentId,
          targetNodeId: teacherId,
          interactionType: "PHYSICAL",
          strength: 1.5,
          actionType: "ASK",
        },
        select: { id: true },
      }),
      prisma.interaction.create({
        data: {
          sessionId: session.id,
          sourceNodeId: studentId,
          targetNodeId: knowledgeId,
          interactionType: "PLATFORM",
          strength: 2.0,
          actionType: "LEARN",
        },
        select: { id: true },
      }),
    ]);

    interactionIds = interactions.map((item) => item.id);
  });

  afterAll(async () => {
    if (interactionIds.length > 0) {
      await prisma.interaction.deleteMany({
        where: { id: { in: interactionIds } },
      });
    }

    if (sessionId) {
      await prisma.interactionSession.deleteMany({ where: { id: sessionId } });
    }

    if (nodeIds.length > 0) {
      await prisma.studentProfile.deleteMany({
        where: { nodeId: { in: nodeIds } },
      });
      await prisma.teacherProfile.deleteMany({
        where: { nodeId: { in: nodeIds } },
      });
      await prisma.knowledgeProfile.deleteMany({
        where: { nodeId: { in: nodeIds } },
      });
      await prisma.graphNode.deleteMany({ where: { id: { in: nodeIds } } });
    }

    if (classId) {
      await prisma.schoolClass.deleteMany({ where: { id: classId } });
    }
    if (gradeId) {
      await prisma.grade.deleteMany({ where: { id: gradeId } });
    }
    if (schoolId) {
      await prisma.school.deleteMany({ where: { id: schoolId } });
    }
    if (scenarioId) {
      await prisma.learningScenario.deleteMany({ where: { id: scenarioId } });
    }

    if (app) {
      await app.close();
    }
  });

  it("returns non-empty nodes and links for valid cascade IDs", async () => {
    const response = await request(app.getHttpServer())
      .get("/api/v1/graph-data")
      .query({
        scenario_code: scenarioCode,
        school_id: schoolId,
        grade_id: gradeId,
        class_id: classId,
      });

    expect(response.status).toBe(200);

    const payload = response.body?.data;
    expect(Array.isArray(payload?.nodes)).toBe(true);
    expect(Array.isArray(payload?.links)).toBe(true);
    expect(payload.nodes.length).toBeGreaterThanOrEqual(3);
    expect(payload.links.length).toBeGreaterThanOrEqual(2);

    const nodeTypes = new Set(payload.nodes.map((node: any) => node.type));
    expect(nodeTypes.has("STUDENT")).toBe(true);
    expect(nodeTypes.has("TEACHER")).toBe(true);
    expect(nodeTypes.has("KNOWLEDGE")).toBe(true);
  });

  it("rejects legacy name filters when ID filters are absent", async () => {
    const response = await request(app.getHttpServer())
      .get("/api/v1/graph-data")
      .query({
        scenario_code: scenarioCode,
        school: `学校_${scope}`,
        grade: `年级_${scope}`,
      });

    expect(response.status).toBe(400);
  });
});
