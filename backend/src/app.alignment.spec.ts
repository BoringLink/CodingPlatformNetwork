import { INestApplication } from "@nestjs/common";
import { Test, TestingModule } from "@nestjs/testing";
import * as request from "supertest";
import { AppModule } from "./app.module";
import { PrismaService } from "./shared/utils/prisma.service";

const mockPrisma = {
  learningScenario: {
    findMany: jest.fn(),
    findUnique: jest.fn(),
  },
  graphNode: {
    findMany: jest.fn(),
    findFirst: jest.fn(),
  },
  interactionSession: {
    findMany: jest.fn(),
    findUnique: jest.fn(),
    count: jest.fn(),
  },
  interaction: {
    findMany: jest.fn(),
    count: jest.fn(),
    create: jest.fn(),
  },
  studentCognitiveProfile: {
    findFirst: jest.fn(),
  },
  $transaction: jest.fn(async (ops: Promise<unknown>[]) => Promise.all(ops)),
};

describe("Backend Alignment Integration", () => {
  let app: INestApplication;

  beforeAll(async () => {
    const moduleRef: TestingModule = await Test.createTestingModule({
      imports: [AppModule],
    })
      .overrideProvider(PrismaService)
      .useValue(mockPrisma)
      .compile();

    app = moduleRef.createNestApplication();
    await app.init();
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  afterAll(async () => {
    if (app) {
      await app.close();
    }
  });

  it("GET /api/v1/scenarios returns wrapped scenarios list", async () => {
    mockPrisma.learningScenario.findMany.mockResolvedValue([
      {
        code: "ONLINE_COURSE",
        nameZh: "学科课程在线学习",
        sortOrder: 1,
        isActive: true,
      },
    ]);

    const res = await request(app.getHttpServer()).get("/api/v1/scenarios");

    expect(res.status).toBe(200);
    expect(res.body).toEqual({
      data: [
        {
          code: "ONLINE_COURSE",
          nameZh: "学科课程在线学习",
          sortOrder: 1,
          isActive: true,
        },
      ],
      meta: null,
      error: null,
    });
  });

  it("GET /api/v1/org/schools returns wrapped school names", async () => {
    mockPrisma.graphNode.findMany.mockResolvedValue([
      { school: "测试学校A" },
      { school: "测试学校B" },
    ]);

    const res = await request(app.getHttpServer()).get("/api/v1/org/schools");

    expect(res.status).toBe(200);
    expect(res.body).toEqual({
      data: ["测试学校A", "测试学校B"],
      meta: null,
      error: null,
    });
  });

  it("GET /api/v1/graph-data returns wrapped graph payload", async () => {
    mockPrisma.learningScenario.findUnique.mockResolvedValue({ id: "sc-1" });
    mockPrisma.interactionSession.findMany.mockResolvedValue([{ id: "ses-1" }]);
    mockPrisma.interaction.findMany.mockResolvedValue([
      {
        sourceNodeId: "node-s1",
        targetNodeId: "node-k1",
        strength: 1.25,
        interactionType: "PLATFORM",
        actionType: "QUESTION",
        sourceNode: {
          id: "node-s1",
          nodeType: "STUDENT",
          displayName: "学生A",
          school: "测试学校A",
          grade: "五年级",
          classId: "1班",
          studentProfile: {
            learningStylePreference: "独自学习",
            personality: "内向",
            groupBehavior: "保持安静，倾听意见",
          },
          teacherProfile: null,
          knowledgeProfile: null,
        },
        targetNode: {
          id: "node-k1",
          nodeType: "KNOWLEDGE",
          displayName: "知识点A",
          school: null,
          grade: null,
          classId: null,
          studentProfile: null,
          teacherProfile: null,
          knowledgeProfile: {
            content: "内容A",
            knowledgeType: "GENERAL",
            category: "基础",
            parentNodeId: null,
          },
        },
      },
    ]);

    const res = await request(app.getHttpServer())
      .get("/api/v1/graph-data")
      .query({ scenario_code: "ONLINE_COURSE", school: "测试学校A" });

    expect(res.status).toBe(200);
    expect(res.body.data.nodes).toHaveLength(2);
    expect(res.body.data.links).toHaveLength(1);
    expect(res.body.data.meta.scenarioCode).toBe("ONLINE_COURSE");
    expect(res.body.meta).toBeNull();
    expect(res.body.error).toBeNull();
  });

  it("GET /api/v1/students/:id/cognitive-template returns wrapped profile", async () => {
    mockPrisma.graphNode.findFirst.mockResolvedValue({
      id: "node-s1",
      displayName: "学生A",
      nodeType: "STUDENT",
      school: "测试学校A",
      grade: "五年级",
      classId: "1班",
      studentProfile: {
        learningStylePreference: "独自学习",
        personality: "内向",
        groupBehavior: "保持安静，倾听意见",
      },
    });
    mockPrisma.studentCognitiveProfile.findFirst.mockResolvedValue({
      profileVersion: "v2026-03-19",
      generatedAt: new Date("2026-03-19T08:00:00.000Z"),
      totalScore: 4.2,
      dimensionScores: [
        {
          dimensionCode: "learningMotivation",
          scoreValue: 4.2,
          scoreLevel: "HIGH",
          dimensionDef: {
            sortOrder: 1,
            dimensionNameZh: "学习动机",
            categoryName: "认知模板",
          },
        },
      ],
    });

    const res = await request(app.getHttpServer()).get(
      "/api/v1/students/node-s1/cognitive-template",
    );

    expect(res.status).toBe(200);
    expect(res.body.data.student.id).toBe("node-s1");
    expect(res.body.data.profile.profileVersion).toBe("v2026-03-19");
    expect(res.body.data.dimensions[0].dimensionCode).toBe(
      "learningMotivation",
    );
    expect(res.body.meta).toBeNull();
    expect(res.body.error).toBeNull();
  });

  it("POST /api/v1/interactions/batchCreate requires idempotency key", async () => {
    const res = await request(app.getHttpServer())
      .post("/api/v1/interactions/batchCreate")
      .send({
        sessionId: "ses-1",
        items: [
          {
            sourceNodeId: "node-s1",
            targetNodeId: "node-k1",
            interactionType: "PLATFORM",
            strength: 1,
          },
        ],
      });

    expect(res.status).toBe(400);
  });

  it("POST /api/v1/interactions/batchCreate succeeds with idempotency key", async () => {
    mockPrisma.interactionSession.findUnique.mockResolvedValue({ id: "ses-1" });
    mockPrisma.graphNode.findMany.mockResolvedValue([
      { id: "node-s1" },
      { id: "node-k1" },
    ]);
    mockPrisma.interaction.create.mockResolvedValue({ id: "int-1" });

    const res = await request(app.getHttpServer())
      .post("/api/v1/interactions/batchCreate")
      .set("idempotency-key", "idem-1")
      .send({
        sessionId: "ses-1",
        items: [
          {
            sourceNodeId: "node-s1",
            targetNodeId: "node-k1",
            interactionType: "PLATFORM",
            strength: 1.5,
            actionType: "QUESTION",
          },
        ],
      });

    expect(res.status).toBe(201);
    expect(res.body).toEqual({
      data: {
        createdCount: 1,
        duplicateCount: 0,
      },
      meta: {
        idempotencyKey: "idem-1",
        duplicatedRequest: false,
      },
      error: null,
    });
  });
});
