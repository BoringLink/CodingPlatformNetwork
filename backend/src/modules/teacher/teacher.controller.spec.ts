import { Test, TestingModule } from "@nestjs/testing";
import { TeacherController } from "./teacher.controller";
import { TeacherService } from "./teacher.service";
import { HttpException, HttpStatus } from "@nestjs/common";
import { CreateTeacherDto, UpdateTeacherDto } from "./teacher.dto";

describe("TeacherController", () => {
  let controller: TeacherController;
  let service: TeacherService;

  beforeEach(async () => {
    const module: TestingModule = await Test.createTestingModule({
      controllers: [TeacherController],
      providers: [
        {
          provide: TeacherService,
          useValue: {
            findAll: jest.fn(),
            findOne: jest.fn(),
            create: jest.fn(),
            update: jest.fn(),
            delete: jest.fn(),
          },
        },
      ],
    }).compile();

    controller = module.get<TeacherController>(TeacherController);
    service = module.get<TeacherService>(TeacherService);
  });

  describe("findAll", () => {
    it("should return teachers list with no filters", async () => {
      const mockTeachers = [
        {
          id: "T001",
          name: "杨逸",
          school: "浙江小虫科技有限公司",
          teachingGrade: "5年级",
          teachingClass: "2班",
          createdAt: new Date(),
          updatedAt: new Date(),
        },
      ];

      jest.spyOn(service, "findAll").mockResolvedValue(mockTeachers);

      const result = await controller.findAll(undefined);

      expect(result).toEqual(mockTeachers);
      expect(service.findAll).toHaveBeenCalledWith({ school: undefined });
    });

    it("should return teachers list with school filter", async () => {
      const mockTeachers = [
        {
          id: "T001",
          name: "杨逸",
          school: "浙江小虫科技有限公司",
          teachingGrade: "5年级",
          teachingClass: "2班",
          createdAt: new Date(),
          updatedAt: new Date(),
        },
      ];

      jest.spyOn(service, "findAll").mockResolvedValue(mockTeachers);

      const result = await controller.findAll("浙江小虫科技有限公司");

      expect(result).toEqual(mockTeachers);
      expect(service.findAll).toHaveBeenCalledWith({
        school: "浙江小虫科技有限公司",
      });
    });
  });

  describe("findOne", () => {
    it("should return teacher by id", async () => {
      const mockTeacher = {
        id: "T001",
        name: "杨逸",
        school: "浙江小虫科技有限公司",
        teachingGrade: "5年级",
        teachingClass: "2班",
        createdAt: new Date(),
        updatedAt: new Date(),
      };

      jest.spyOn(service, "findOne").mockResolvedValue(mockTeacher);

      const result = await controller.findOne("T001");

      expect(result).toEqual(mockTeacher);
      expect(service.findOne).toHaveBeenCalledWith("T001");
    });

    it("should throw 404 error when teacher not found", async () => {
      jest.spyOn(service, "findOne").mockResolvedValue(null);

      await expect(controller.findOne("T999")).rejects.toThrow(HttpException);
      await expect(controller.findOne("T999")).rejects.toThrow("教师不存在");
      await expect(controller.findOne("T999")).rejects.toMatchObject({
        status: HttpStatus.NOT_FOUND,
      });
    });
  });

  describe("create", () => {
    it("should create teacher with valid data", async () => {
      const createDto: CreateTeacherDto = {
        name: "张三",
        school: "杭州市文澜实验学校",
        teachingGrade: "4年级",
        teachingClass: "1班",
      };

      const mockTeacher = {
        id: "T002",
        name: createDto.name,
        school: createDto.school,
        teachingGrade: createDto.teachingGrade,
        teachingClass: createDto.teachingClass,
        createdAt: new Date(),
        updatedAt: new Date(),
      };

      jest.spyOn(service, "create").mockResolvedValue(mockTeacher);

      const result = await controller.create(createDto);

      expect(result).toEqual(mockTeacher);
      expect(service.create).toHaveBeenCalledWith(createDto);
    });

    it("should throw 400 error with invalid data", async () => {
      const invalidDto = {
        name: "", // 空姓名
        school: "杭州市文澜实验学校",
        teachingGrade: "4年级",
        teachingClass: "1班",
      };

      await expect(controller.create(invalidDto as any)).rejects.toThrow(
        HttpException,
      );
      await expect(controller.create(invalidDto as any)).rejects.toMatchObject({
        status: HttpStatus.BAD_REQUEST,
      });
    });

    it("should throw 400 error with missing required fields", async () => {
      const invalidDto = {
        name: "张三",
        school: "杭州市文澜实验学校",
        // 缺少 teachingGrade
        teachingClass: "1班",
      };

      await expect(controller.create(invalidDto as any)).rejects.toThrow(
        HttpException,
      );
      await expect(controller.create(invalidDto as any)).rejects.toMatchObject({
        status: HttpStatus.BAD_REQUEST,
      });
    });
  });

  describe("update", () => {
    it("should update teacher with valid data", async () => {
      const updateDto: UpdateTeacherDto = {
        name: "李四",
        school: "杭州市文澜实验学校",
        teachingGrade: "4年级",
        teachingClass: "1班",
      };

      const mockTeacher = {
        id: "T001",
        name: updateDto.name,
        school: updateDto.school,
        teachingGrade: updateDto.teachingGrade,
        teachingClass: updateDto.teachingClass,
        createdAt: new Date(),
        updatedAt: new Date(),
      };

      jest.spyOn(service, "update").mockResolvedValue(mockTeacher);

      const result = await controller.update("T001", updateDto);

      expect(result).toEqual(mockTeacher);
      expect(service.update).toHaveBeenCalledWith("T001", updateDto);
    });

    it("should throw 404 error when teacher not found", async () => {
      const updateDto: UpdateTeacherDto = {
        name: "李四",
        school: "杭州市文澜实验学校",
        teachingGrade: "4年级",
        teachingClass: "1班",
      };

      jest.spyOn(service, "update").mockResolvedValue(null);

      await expect(controller.update("T999", updateDto)).rejects.toThrow(
        HttpException,
      );
      await expect(controller.update("T999", updateDto)).rejects.toThrow(
        "教师不存在",
      );
      await expect(controller.update("T999", updateDto)).rejects.toMatchObject({
        status: HttpStatus.NOT_FOUND,
      });
    });

    it("should throw 400 error with invalid data", async () => {
      const invalidDto = {
        name: "", // 空姓名
        school: "杭州市文澜实验学校",
        teachingGrade: "4年级",
        teachingClass: "1班",
      };

      await expect(
        controller.update("T001", invalidDto as any),
      ).rejects.toThrow(HttpException);
      await expect(
        controller.update("T001", invalidDto as any),
      ).rejects.toMatchObject({ status: HttpStatus.BAD_REQUEST });
    });
  });

  describe("delete", () => {
    it("should delete teacher successfully", async () => {
      const mockResponse = { message: "教师删除成功" };

      jest.spyOn(service, "delete").mockResolvedValue(mockResponse);

      const result = await controller.delete("T001");

      expect(result).toEqual(mockResponse);
      expect(service.delete).toHaveBeenCalledWith("T001");
    });

    it("should throw 404 error when teacher not found", async () => {
      jest.spyOn(service, "delete").mockRejectedValue(new Error("教师不存在"));

      await expect(controller.delete("T999")).rejects.toThrow(HttpException);
      await expect(controller.delete("T999")).rejects.toThrow("教师不存在");
      await expect(controller.delete("T999")).rejects.toMatchObject({
        status: HttpStatus.NOT_FOUND,
      });
    });
  });
});
