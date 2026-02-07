import { Test, TestingModule } from "@nestjs/testing";
import { INestApplication } from "@nestjs/common";
import * as request from "supertest";
import { GraphController } from "./graph.controller";
import { GraphService } from "./graph.service";

const mockGraphService = {
  generateGraphData: jest.fn(),
  getResourceRecommendations: jest.fn(),
  getGraphData: jest.fn(),
};

describe("GraphController", () => {
  let app: INestApplication;

  beforeEach(async () => {
    const moduleFixture: TestingModule = await Test.createTestingModule({
      controllers: [GraphController],
      providers: [
        {
          provide: GraphService,
          useValue: mockGraphService,
        },
      ],
    }).compile();

    app = moduleFixture.createNestApplication();
    await app.init();
  });

  afterEach(async () => {
    if (app) {
      await app.close();
    }
  });

  describe("GET /api/v1/graph-data", () => {
    it("should return complete graph data", async () => {
      const mockGraphData = {
        nodes: [
          {
            id: "S001",
            type: "STUDENT",
            name: "测试学生",
            group: 3,
            val: 8,
            studentProfile: {
              school: "测试学校",
              grade: "5年级",
              classId: "1班",
              knowledgeReserve: 4,
              learningEngagement: 4,
              cognitiveLoad: 3,
              learningMotivation: 4,
              computationalThinking: 3,
              humanAiTrust: 4,
              learningMethod: 3,
              learningAttitude: 4,
            },
          },
          {
            id: "T001",
            type: "TEACHER",
            name: "测试教师",
            group: 1,
            val: 25,
            teacherProfile: {
              school: "测试学校",
              teachingGrade: "5年级",
              teachingClass: "1班",
            },
          },
          {
            id: "K001",
            type: "KNOWLEDGE",
            name: "测试知识点",
            group: 2,
            val: 15,
            knowledgeProfile: {
              content: "测试知识点内容",
              type: "知识点",
              parentId: "K002",
              parentName: "上级知识点",
              relatedKnowledgeIds: ["K003", "K004"],
              relatedKnowledgeNames: ["相关知识点1", "相关知识点2"],
            },
          },
        ],
        links: [
          {
            source: "S001",
            target: "T001",
            value: 2,
            type: "PHYSICAL",
          },
          {
            source: "S001",
            target: "K001",
            value: 1.5,
            type: "PLATFORM",
          },
        ],
      };

      mockGraphService.getGraphData.mockResolvedValue(mockGraphData);

      const response = await request(app.getHttpServer()).get(
        "/api/v1/graph-data",
      );
      expect(response.status).toBe(200);
      expect(response.body).toEqual(mockGraphData);
    });

    it("should handle query parameters", async () => {
      const mockGraphData = {
        nodes: [
          {
            id: "S001",
            type: "STUDENT",
            name: "测试学生",
            group: 3,
            val: 8,
            studentProfile: {
              school: "测试学校",
              grade: "5年级",
              classId: "1班",
              knowledgeReserve: 4,
              learningEngagement: 4,
              cognitiveLoad: 3,
              learningMotivation: 4,
              computationalThinking: 3,
              humanAiTrust: 4,
              learningMethod: 3,
              learningAttitude: 4,
            },
          },
        ],
        links: [],
      };

      mockGraphService.getGraphData.mockResolvedValue(mockGraphData);

      const response = await request(app.getHttpServer())
        .get("/api/v1/graph-data")
        .query({
          scenario: "COLLABORATIVE",
          school: "测试学校",
          grade: "5年级",
          class_id: "1班",
        });
      expect(response.status).toBe(200);
      expect(response.body).toEqual(mockGraphData);
    });

    it("should handle empty data", async () => {
      const mockGraphData = {
        nodes: [],
        links: [],
      };

      mockGraphService.getGraphData.mockResolvedValue(mockGraphData);

      const response = await request(app.getHttpServer()).get(
        "/api/v1/graph-data",
      );
      expect(response.status).toBe(200);
      expect(response.body).toEqual(mockGraphData);
    });
  });
});
