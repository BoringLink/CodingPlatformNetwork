import { Test, TestingModule } from "@nestjs/testing";
import { INestApplication } from "@nestjs/common";
import * as request from "supertest";
import { KnowledgeController } from "./knowledge.controller";
import { KnowledgeService } from "./knowledge.service";
import { CreateKnowledgeDto } from "./knowledge.dto";

const mockKnowledgeService = {
  findAll: jest.fn(),
  findOne: jest.fn(),
  create: jest.fn(),
  update: jest.fn(),
  delete: jest.fn(),
};

describe("KnowledgeController", () => {
  let app: INestApplication;

  beforeEach(async () => {
    const moduleFixture: TestingModule = await Test.createTestingModule({
      controllers: [KnowledgeController],
      providers: [
        {
          provide: KnowledgeService,
          useValue: mockKnowledgeService,
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

  describe("GET /api/v1/knowledge-points", () => {
    it("should return an array of knowledge points", async () => {
      const mockKnowledgePoints = [
        {
          id: "K001",
          content: "测试知识点内容",
          knowledgePoint: "测试知识点",
          grade: "5年级",
          type: "知识点",
          parentId: "K002",
          parentName: "上级知识点",
          relatedKnowledgeIds: ["K003", "K004"],
          relatedKnowledgeNames: ["相关知识点1", "相关知识点2"],
        },
      ];

      mockKnowledgeService.findAll.mockResolvedValue(mockKnowledgePoints);

      const response = await request(app.getHttpServer()).get(
        "/api/v1/knowledge-points",
      );
      expect(response.status).toBe(200);
      expect(response.body).toEqual(mockKnowledgePoints);
    });

    it("should handle query parameters", async () => {
      const mockKnowledgePoints = [
        {
          id: "K001",
          content: "测试知识点内容",
          knowledgePoint: "测试知识点",
          grade: "5年级",
          type: "知识点",
          parentId: "K002",
          parentName: "上级知识点",
          relatedKnowledgeIds: ["K003", "K004"],
          relatedKnowledgeNames: ["相关知识点1", "相关知识点2"],
        },
      ];

      mockKnowledgeService.findAll.mockResolvedValue(mockKnowledgePoints);

      const response = await request(app.getHttpServer())
        .get("/api/v1/knowledge-points")
        .query({ grade: "5年级", type: "知识点", parent_id: "K002" });
      expect(response.status).toBe(200);
      expect(response.body).toEqual(mockKnowledgePoints);
    });
  });

  describe("GET /api/v1/knowledge-points/:id", () => {
    it("should return a knowledge point by id", async () => {
      const mockKnowledgePoint = {
        id: "K001",
        content: "测试知识点内容",
        knowledgePoint: "测试知识点",
        grade: "5年级",
        type: "知识点",
        parentId: "K002",
        parentName: "上级知识点",
        relatedKnowledgeIds: ["K003", "K004"],
        relatedKnowledgeNames: ["相关知识点1", "相关知识点2"],
      };

      mockKnowledgeService.findOne.mockResolvedValue(mockKnowledgePoint);

      const response = await request(app.getHttpServer()).get(
        "/api/v1/knowledge-points/K001",
      );
      expect(response.status).toBe(200);
      expect(response.body).toEqual(mockKnowledgePoint);
    });

    it("should handle knowledge point not found", async () => {
      mockKnowledgeService.findOne.mockResolvedValue(null);

      const response = await request(app.getHttpServer()).get(
        "/api/v1/knowledge-points/non-existent",
      );
      expect(response.status).toBe(404);
      expect(response.body).toHaveProperty("message", "知识点不存在");
    });
  });

  describe("POST /api/v1/knowledge-points", () => {
    it("should create a new knowledge point", async () => {
      const createKnowledgeDto: CreateKnowledgeDto = {
        content: "测试知识点内容",
        knowledgePoint: "测试知识点",
        grade: "5年级",
        type: "知识点",
        parentId: "K002",
        parentName: "上级知识点",
        relatedKnowledgeIds: ["K003", "K004"],
        relatedKnowledgeNames: ["相关知识点1", "相关知识点2"],
      };

      const mockKnowledgePoint = {
        id: "K001",
        ...createKnowledgeDto,
      };

      mockKnowledgeService.create.mockResolvedValue(mockKnowledgePoint);

      const response = await request(app.getHttpServer())
        .post("/api/v1/knowledge-points")
        .send(createKnowledgeDto);
      expect(response.status).toBe(201);
      expect(response.body).toEqual(mockKnowledgePoint);
    });

    it("should handle validation errors", async () => {
      const invalidKnowledgeDto = {
        content: "",
        knowledgePoint: "",
        grade: "",
        type: "",
      };

      const response = await request(app.getHttpServer())
        .post("/api/v1/knowledge-points")
        .send(invalidKnowledgeDto);
      expect(response.status).toBe(400);
      expect(Array.isArray(response.body)).toBe(true);
    });
  });

  describe("PUT /api/v1/knowledge-points/:id", () => {
    it("should update a knowledge point", async () => {
      const updateData = {
        content: "更新后的知识点内容",
        knowledgePoint: "更新后的知识点",
      };

      const mockUpdatedKnowledgePoint = {
        id: "K001",
        content: "更新后的知识点内容",
        knowledgePoint: "更新后的知识点",
        grade: "5年级",
        type: "知识点",
        parentId: "K002",
        parentName: "上级知识点",
        relatedKnowledgeIds: ["K003", "K004"],
        relatedKnowledgeNames: ["相关知识点1", "相关知识点2"],
      };

      mockKnowledgeService.update.mockResolvedValue(mockUpdatedKnowledgePoint);

      const response = await request(app.getHttpServer())
        .put("/api/v1/knowledge-points/K001")
        .send(updateData);
      expect(response.status).toBe(200);
      expect(response.body).toEqual(mockUpdatedKnowledgePoint);
    });

    it("should handle knowledge point not found", async () => {
      mockKnowledgeService.update.mockResolvedValue(null);

      const response = await request(app.getHttpServer())
        .put("/api/v1/knowledge-points/non-existent")
        .send({ content: "更新后的知识点内容" });
      expect(response.status).toBe(404);
      expect(response.body).toHaveProperty("message", "知识点不存在");
    });
  });

  describe("DELETE /api/v1/knowledge-points/:id", () => {
    it("should delete a knowledge point", async () => {
      mockKnowledgeService.delete.mockResolvedValue({
        message: "知识点删除成功",
      });

      const response = await request(app.getHttpServer()).delete(
        "/api/v1/knowledge-points/K001",
      );
      expect(response.status).toBe(200);
      expect(response.body).toHaveProperty("message", "知识点删除成功");
    });

    it("should handle knowledge point not found", async () => {
      mockKnowledgeService.delete.mockResolvedValue({
        message: "知识点不存在",
      });

      const response = await request(app.getHttpServer()).delete(
        "/api/v1/knowledge-points/non-existent",
      );
      expect(response.status).toBe(200);
      expect(response.body).toHaveProperty("message", "知识点不存在");
    });
  });
});
