import { Test, TestingModule } from "@nestjs/testing";
import { INestApplication } from "@nestjs/common";
import * as request from "supertest";
import { TeacherController } from "./teacher.controller";
import { TeacherService } from "./teacher.service";
import { CreateTeacherDto } from "./teacher.dto";

const mockTeacherService = {
  findAll: jest.fn(),
  findOne: jest.fn(),
  create: jest.fn(),
  update: jest.fn(),
  delete: jest.fn(),
};

describe("TeacherController", () => {
  let app: INestApplication;

  beforeEach(async () => {
    const moduleFixture: TestingModule = await Test.createTestingModule({
      controllers: [TeacherController],
      providers: [
        {
          provide: TeacherService,
          useValue: mockTeacherService,
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

  describe("GET /api/v1/teachers", () => {
    it("should return an array of teachers", async () => {
      const mockTeachers = [
        {
          id: "T001",
          name: "测试教师",
          school: "测试学校",
          teachingGrade: "5年级",
          teachingClass: "1班",
        },
      ];

      mockTeacherService.findAll.mockResolvedValue(mockTeachers);

      const response = await request(app.getHttpServer()).get(
        "/api/v1/teachers",
      );
      expect(response.status).toBe(200);
      expect(response.body).toEqual(mockTeachers);
    });

    it("should handle school parameter", async () => {
      const mockTeachers = [
        {
          id: "T001",
          name: "测试教师",
          school: "测试学校",
          teachingGrade: "5年级",
          teachingClass: "1班",
        },
      ];

      mockTeacherService.findAll.mockResolvedValue(mockTeachers);

      const response = await request(app.getHttpServer())
        .get("/api/v1/teachers")
        .query({ school: "测试学校" });
      expect(response.status).toBe(200);
      expect(response.body).toEqual(mockTeachers);
    });
  });

  describe("GET /api/v1/teachers/:id", () => {
    it("should return a teacher by id", async () => {
      const mockTeacher = {
        id: "T001",
        name: "测试教师",
        school: "测试学校",
        teachingGrade: "5年级",
        teachingClass: "1班",
      };

      mockTeacherService.findOne.mockResolvedValue(mockTeacher);

      const response = await request(app.getHttpServer()).get(
        "/api/v1/teachers/T001",
      );
      expect(response.status).toBe(200);
      expect(response.body).toEqual(mockTeacher);
    });

    it("should handle teacher not found", async () => {
      mockTeacherService.findOne.mockResolvedValue(null);

      const response = await request(app.getHttpServer()).get(
        "/api/v1/teachers/non-existent",
      );
      expect(response.status).toBe(404);
      expect(response.body).toHaveProperty("message", "教师不存在");
    });
  });

  describe("POST /api/v1/teachers", () => {
    it("should create a new teacher", async () => {
      const createTeacherDto: CreateTeacherDto = {
        name: "测试教师",
        school: "测试学校",
        teachingGrade: "5年级",
        teachingClass: "1班",
      };

      const mockTeacher = {
        id: "T001",
        ...createTeacherDto,
      };

      mockTeacherService.create.mockResolvedValue(mockTeacher);

      const response = await request(app.getHttpServer())
        .post("/api/v1/teachers")
        .send(createTeacherDto);
      expect(response.status).toBe(201);
      expect(response.body).toEqual(mockTeacher);
    });

    it("should handle validation errors", async () => {
      const invalidTeacherDto = {
        name: "",
        school: "",
        teachingGrade: "",
        teachingClass: "",
      };

      const response = await request(app.getHttpServer())
        .post("/api/v1/teachers")
        .send(invalidTeacherDto);
      expect(response.status).toBe(400);
      expect(Array.isArray(response.body)).toBe(true);
    });
  });

  describe("PUT /api/v1/teachers/:id", () => {
    it("should update a teacher", async () => {
      const updateData = {
        name: "更新后的教师",
        school: "更新后的学校",
      };

      const mockUpdatedTeacher = {
        id: "T001",
        name: "更新后的教师",
        school: "更新后的学校",
        teachingGrade: "5年级",
        teachingClass: "1班",
      };

      mockTeacherService.update.mockResolvedValue(mockUpdatedTeacher);

      const response = await request(app.getHttpServer())
        .put("/api/v1/teachers/T001")
        .send(updateData);
      expect(response.status).toBe(200);
      expect(response.body).toEqual(mockUpdatedTeacher);
    });

    it("should handle teacher not found", async () => {
      mockTeacherService.update.mockResolvedValue(null);

      const response = await request(app.getHttpServer())
        .put("/api/v1/teachers/non-existent")
        .send({ name: "更新后的教师" });
      expect(response.status).toBe(404);
      expect(response.body).toHaveProperty("message", "教师不存在");
    });
  });

  describe("DELETE /api/v1/teachers/:id", () => {
    it("should delete a teacher", async () => {
      mockTeacherService.delete.mockResolvedValue({ message: "教师删除成功" });

      const response = await request(app.getHttpServer()).delete(
        "/api/v1/teachers/T001",
      );
      expect(response.status).toBe(200);
      expect(response.body).toHaveProperty("message", "教师删除成功");
    });

    it("should handle teacher not found", async () => {
      mockTeacherService.delete.mockResolvedValue({ message: "教师不存在" });

      const response = await request(app.getHttpServer()).delete(
        "/api/v1/teachers/non-existent",
      );
      expect(response.status).toBe(200);
      expect(response.body).toHaveProperty("message", "教师不存在");
    });
  });
});
