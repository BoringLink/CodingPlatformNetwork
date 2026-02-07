import { Test, TestingModule } from "@nestjs/testing";
import { INestApplication } from "@nestjs/common";
import * as request from "supertest";
import { StudentController } from "./student.controller";
import { StudentService } from "./student.service";
import { CreateStudentDto } from "./student.dto";

const mockStudentService = {
  findAll: jest.fn(),
  findOne: jest.fn(),
  create: jest.fn(),
  update: jest.fn(),
  delete: jest.fn(),
};

describe("StudentController", () => {
  let app: INestApplication;

  beforeEach(async () => {
    const moduleFixture: TestingModule = await Test.createTestingModule({
      controllers: [StudentController],
      providers: [
        {
          provide: StudentService,
          useValue: mockStudentService,
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

  describe("GET /api/v1/students", () => {
    it("should return an array of students", async () => {
      const mockStudents = [
        {
          id: "S001",
          name: "测试学生",
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
      ];

      mockStudentService.findAll.mockResolvedValue(mockStudents);

      const response = await request(app.getHttpServer()).get(
        "/api/v1/students",
      );
      expect(response.status).toBe(200);
      expect(response.body).toEqual(mockStudents);
    });

    it("should handle query parameters", async () => {
      const mockStudents = [
        {
          id: "S001",
          name: "测试学生",
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
      ];

      mockStudentService.findAll.mockResolvedValue(mockStudents);

      const response = await request(app.getHttpServer())
        .get("/api/v1/students")
        .query({ school: "测试学校", grade: "5年级", class_id: "1班" });
      expect(response.status).toBe(200);
      expect(response.body).toEqual(mockStudents);
    });
  });

  describe("GET /api/v1/students/:id", () => {
    it("should return a student by id", async () => {
      const mockStudent = {
        id: "S001",
        name: "测试学生",
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
      };

      mockStudentService.findOne.mockResolvedValue(mockStudent);

      const response = await request(app.getHttpServer()).get(
        "/api/v1/students/S001",
      );
      expect(response.status).toBe(200);
      expect(response.body).toEqual(mockStudent);
    });

    it("should handle student not found", async () => {
      mockStudentService.findOne.mockResolvedValue(null);

      const response = await request(app.getHttpServer()).get(
        "/api/v1/students/non-existent",
      );
      expect(response.status).toBe(404);
      expect(response.body).toHaveProperty("message", "学生不存在");
    });
  });

  describe("POST /api/v1/students", () => {
    it("should create a new student", async () => {
      const createStudentDto: CreateStudentDto = {
        name: "测试学生",
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
      };

      const mockStudent = {
        id: "S001",
        ...createStudentDto,
      };

      mockStudentService.create.mockResolvedValue(mockStudent);

      const response = await request(app.getHttpServer())
        .post("/api/v1/students")
        .send(createStudentDto);
      expect(response.status).toBe(201);
      expect(response.body).toEqual(mockStudent);
    });

    it("should handle validation errors", async () => {
      const invalidStudentDto = {
        name: "",
        school: "",
        grade: "",
        classId: "",
      };

      const response = await request(app.getHttpServer())
        .post("/api/v1/students")
        .send(invalidStudentDto);
      expect(response.status).toBe(400);
      expect(Array.isArray(response.body)).toBe(true);
    });
  });

  describe("PUT /api/v1/students/:id", () => {
    it("should update a student", async () => {
      const updateData = {
        name: "更新后的学生",
        knowledgeReserve: 5,
      };

      const mockUpdatedStudent = {
        id: "S001",
        name: "更新后的学生",
        school: "测试学校",
        grade: "5年级",
        classId: "1班",
        knowledgeReserve: 5,
        learningEngagement: 4,
        cognitiveLoad: 3,
        learningMotivation: 4,
        computationalThinking: 3,
        humanAiTrust: 4,
        learningMethod: 3,
        learningAttitude: 4,
      };

      mockStudentService.update.mockResolvedValue(mockUpdatedStudent);

      const response = await request(app.getHttpServer())
        .put("/api/v1/students/S001")
        .send(updateData);
      expect(response.status).toBe(200);
      expect(response.body).toEqual(mockUpdatedStudent);
    });

    it("should handle student not found", async () => {
      mockStudentService.update.mockResolvedValue(null);

      const response = await request(app.getHttpServer())
        .put("/api/v1/students/non-existent")
        .send({ name: "更新后的学生" });
      expect(response.status).toBe(404);
      expect(response.body).toHaveProperty("message", "学生不存在");
    });
  });

  describe("DELETE /api/v1/students/:id", () => {
    it("should delete a student", async () => {
      mockStudentService.delete.mockResolvedValue({ message: "学生删除成功" });

      const response = await request(app.getHttpServer()).delete(
        "/api/v1/students/S001",
      );
      expect(response.status).toBe(200);
      expect(response.body).toHaveProperty("message", "学生删除成功");
    });

    it("should handle student not found", async () => {
      mockStudentService.delete.mockResolvedValue({ message: "学生不存在" });

      const response = await request(app.getHttpServer()).delete(
        "/api/v1/students/non-existent",
      );
      expect(response.status).toBe(200);
      expect(response.body).toHaveProperty("message", "学生不存在");
    });
  });
});
