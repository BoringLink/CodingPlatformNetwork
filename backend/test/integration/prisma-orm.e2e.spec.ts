import "dotenv/config";
import { INestApplication } from "@nestjs/common";
import { Test, TestingModule } from "@nestjs/testing";
import { afterAll, beforeAll, describe, expect, it } from "@jest/globals";
import { AppModule } from "../../src/app.module";
import { PrismaService } from "../../src/shared/utils/prisma.service";

describe("Prisma ORM Integration (real DB)", () => {
  let app: INestApplication;
  let prisma: PrismaService;

  let scenarioId: string | null = null;
  let sessionId: string | null = null;

  const scope = `orm_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`;
  const schoolToken = `school_${scope}`;
  const gradeToken = `grade_${scope}`;
  const classToken = `class_${scope}`;

  beforeAll(async () => {
    const moduleRef: TestingModule = await Test.createTestingModule({
      imports: [AppModule],
    }).compile();

    app = moduleRef.createNestApplication();
    await app.init();
    prisma = app.get(PrismaService);
  });

  afterAll(async () => {
    if (sessionId) {
      await prisma.interactionSession.deleteMany({ where: { id: sessionId } });
    }
    if (scenarioId) {
      await prisma.learningScenario.deleteMany({ where: { id: scenarioId } });
    }

    if (app) {
      await app.close();
    }
  });

  it("maps schoolId/gradeId filters to interaction_sessions physical columns", async () => {
    const scenario = await prisma.learningScenario.create({
      data: {
        code: `ORM_SCENARIO_${scope}`,
        nameZh: "ORM映射验证场景",
        sortOrder: 9999,
        isActive: true,
      },
      select: { id: true },
    });

    scenarioId = scenario.id;

    const session = await prisma.interactionSession.create({
      data: {
        scenarioId: scenario.id,
        sessionName: `ORM Session ${scope}`,
        occurredAt: new Date(),
        schoolId: schoolToken,
        gradeId: gradeToken,
        classId: classToken,
      },
      select: { id: true },
    });

    sessionId = session.id;

    const queried = await prisma.interactionSession.findMany({
      where: {
        schoolId: schoolToken,
        gradeId: gradeToken,
        classId: classToken,
      },
      select: { id: true },
    });

    expect(queried.some((row) => row.id === session.id)).toBe(true);
  });
});
