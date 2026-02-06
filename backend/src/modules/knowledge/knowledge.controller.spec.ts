import { Test, TestingModule } from "@nestjs/testing";
import { KnowledgeController } from "./knowledge.controller";
import { KnowledgeService } from "./knowledge.service";
import { HttpException, HttpStatus } from "@nestjs/common";
import { CreateKnowledgeDto, UpdateKnowledgeDto } from "./knowledge.dto";

describe("KnowledgeController", () => {
  let controller: KnowledgeController;
  let service: KnowledgeService;

  beforeEach(async () => {
    const module: TestingModule = await Test.createTestingModule({
      controllers: [KnowledgeController],
      providers: [
        {
          provide: KnowledgeService,
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

    controller = module.get<KnowledgeController>(KnowledgeController);
    service = module.get<KnowledgeService>(KnowledgeService);
  });

  describe("findAll", () => {
    it("should return knowledge points list with no filters", async () => {
      const mockKnowledgePoints = [
        {
          id: "K001",
          content:
            '将光标定位到要插入图片的位置，点击"插入"选项卡，点击"图片"按钮，选择本地图片上传。',
          knowledgePoint: "insert_image",
          grade: "5年级",
          type: "知识点",
          parentId: "K002",
          parentName: "Word操作基础",
          relatedKnowledgeIds: [],
          relatedKnowledgeNames: [],
          createdAt: new Date(),
          updatedAt: new Date(),
        },
      ];

      jest.spyOn(service, "findAll").mockResolvedValue(mockKnowledgePoints);

      const result = await controller.findAll(undefined, undefined, undefined);

      expect(result).toEqual(mockKnowledgePoints);
      expect(service.findAll).toHaveBeenCalledWith({
        grade: undefined,
        type: undefined,
        parentId: undefined,
      });
    });

    it("should return knowledge points list with grade filter", async () => {
      const mockKnowledgePoints = [
        {
          id: "K001",
          content:
            '将光标定位到要插入图片的位置，点击"插入"选项卡，点击"图片"按钮，选择本地图片上传。',
          knowledgePoint: "insert_image",
          grade: "5年级",
          type: "知识点",
          parentId: "K002",
          parentName: "Word操作基础",
          relatedKnowledgeIds: [],
          relatedKnowledgeNames: [],
          createdAt: new Date(),
          updatedAt: new Date(),
        },
      ];

      jest.spyOn(service, "findAll").mockResolvedValue(mockKnowledgePoints);

      const result = await controller.findAll("5年级", undefined, undefined);

      expect(result).toEqual(mockKnowledgePoints);
      expect(service.findAll).toHaveBeenCalledWith({
        grade: "5年级",
        type: undefined,
        parentId: undefined,
      });
    });

    it("should return knowledge points list with type filter", async () => {
      const mockKnowledgePoints = [
        {
          id: "K001",
          content:
            '将光标定位到要插入图片的位置，点击"插入"选项卡，点击"图片"按钮，选择本地图片上传。',
          knowledgePoint: "insert_image",
          grade: "5年级",
          type: "知识点",
          parentId: "K002",
          parentName: "Word操作基础",
          relatedKnowledgeIds: [],
          relatedKnowledgeNames: [],
          createdAt: new Date(),
          updatedAt: new Date(),
        },
      ];

      jest.spyOn(service, "findAll").mockResolvedValue(mockKnowledgePoints);

      const result = await controller.findAll(undefined, "知识点", undefined);

      expect(result).toEqual(mockKnowledgePoints);
      expect(service.findAll).toHaveBeenCalledWith({
        grade: undefined,
        type: "知识点",
        parentId: undefined,
      });
    });

    it("should return knowledge points list with parentId filter", async () => {
      const mockKnowledgePoints = [
        {
          id: "K001",
          content:
            '将光标定位到要插入图片的位置，点击"插入"选项卡，点击"图片"按钮，选择本地图片上传。',
          knowledgePoint: "insert_image",
          grade: "5年级",
          type: "知识点",
          parentId: "K002",
          parentName: "Word操作基础",
          relatedKnowledgeIds: ["K003", "K004"],
          relatedKnowledgeNames: ["设置字体", "设置段落"],
          createdAt: new Date(),
          updatedAt: new Date(),
        },
      ];

      jest.spyOn(service, "findAll").mockResolvedValue(mockKnowledgePoints);

      const result = await controller.findAll(undefined, undefined, "K002");

      expect(result).toEqual(mockKnowledgePoints);
      expect(service.findAll).toHaveBeenCalledWith({
        grade: undefined,
        type: undefined,
        parentId: "K002",
      });
    });
  });

  describe("findOne", () => {
    it("should return knowledge point by id", async () => {
      const mockKnowledgePoint = {
        id: "K001",
        content:
          '将光标定位到要插入图片的位置，点击"插入"选项卡，点击"图片"按钮，选择本地图片上传。',
        knowledgePoint: "insert_image",
        grade: "5年级",
        type: "知识点",
        parentId: "K002",
        parentName: "Word操作基础",
        relatedKnowledgeIds: ["K003", "K004"],
        relatedKnowledgeNames: ["设置字体", "设置段落"],
        createdAt: new Date(),
        updatedAt: new Date(),
      };

      jest.spyOn(service, "findOne").mockResolvedValue(mockKnowledgePoint);

      const result = await controller.findOne("K001");

      expect(result).toEqual(mockKnowledgePoint);
      expect(service.findOne).toHaveBeenCalledWith("K001");
    });

    it("should throw 404 error when knowledge point not found", async () => {
      jest.spyOn(service, "findOne").mockResolvedValue(null);

      await expect(controller.findOne("K999")).rejects.toThrow(HttpException);
      await expect(controller.findOne("K999")).rejects.toThrow("知识点不存在");
      await expect(controller.findOne("K999")).rejects.toMatchObject({
        status: HttpStatus.NOT_FOUND,
      });
    });
  });

  describe("create", () => {
    it("should create knowledge point with valid data", async () => {
      const createDto: CreateKnowledgeDto = {
        content: "设置文档页面大小为A4，页边距为上下2.54cm，左右3.17cm。",
        knowledgePoint: "page_setup",
        grade: "5年级",
        type: "知识点",
        parentId: "K002",
        parentName: "Word操作基础",
        relatedKnowledgeIds: ["K003", "K004"],
        relatedKnowledgeNames: ["设置字体", "设置段落"],
      };

      const mockKnowledgePoint = {
        id: "K002",
        content: createDto.content,
        knowledgePoint: createDto.knowledgePoint,
        grade: createDto.grade,
        type: createDto.type,
        parentId: createDto.parentId,
        parentName: createDto.parentName,
        relatedKnowledgeIds: createDto.relatedKnowledgeIds,
        relatedKnowledgeNames: createDto.relatedKnowledgeNames,
        createdAt: new Date(),
        updatedAt: new Date(),
      };

      jest.spyOn(service, "create").mockResolvedValue(mockKnowledgePoint);

      const result = await controller.create(createDto);

      expect(result).toEqual(mockKnowledgePoint);
      expect(service.create).toHaveBeenCalledWith(createDto);
    });

    it("should throw 400 error with invalid data", async () => {
      const invalidDto = {
        content: "", // 空内容
        knowledgePoint: "page_setup",
        grade: "5年级",
        type: "知识点",
        parentId: "K002",
        parentName: "Word操作基础",
        relatedKnowledgeIds: ["K003", "K004"],
        relatedKnowledgeNames: ["设置字体", "设置段落"],
      };

      await expect(controller.create(invalidDto as any)).rejects.toThrow(
        HttpException,
      );
      await expect(controller.create(invalidDto as any)).rejects.toMatchObject({
        status: HttpStatus.BAD_REQUEST,
      });
    });

    it("should throw 400 error with invalid type", async () => {
      const invalidDto = {
        content: "设置文档页面大小为A4，页边距为上下2.54cm，左右3.17cm。",
        knowledgePoint: "page_setup",
        grade: "5年级",
        type: "无效类型", // 无效类型
        parentId: "K002",
        parentName: "Word操作基础",
        relatedKnowledgeIds: ["K003", "K004"],
        relatedKnowledgeNames: ["设置字体", "设置段落"],
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
    it("should update knowledge point with valid data", async () => {
      const updateDto: UpdateKnowledgeDto = {
        content:
          '设置文档页面大小为A4，页边距为上下2.54cm，左右3.17cm。可通过"页面布局"选项卡进行设置。',
        knowledgePoint: "page_setup",
        grade: "5年级",
        type: "知识点",
        parentId: "K002",
        parentName: "Word操作基础",
        relatedKnowledgeIds: ["K003", "K004"],
        relatedKnowledgeNames: ["设置字体", "设置段落"],
      };

      const mockKnowledgePoint = {
        id: "K001",
        content: updateDto.content,
        knowledgePoint: updateDto.knowledgePoint,
        grade: updateDto.grade,
        type: updateDto.type,
        parentId: updateDto.parentId,
        parentName: updateDto.parentName,
        relatedKnowledgeIds: updateDto.relatedKnowledgeIds,
        relatedKnowledgeNames: updateDto.relatedKnowledgeNames,
        createdAt: new Date(),
        updatedAt: new Date(),
      };

      jest.spyOn(service, "update").mockResolvedValue(mockKnowledgePoint);

      const result = await controller.update("K001", updateDto);

      expect(result).toEqual(mockKnowledgePoint);
      expect(service.update).toHaveBeenCalledWith("K001", updateDto);
    });

    it("should throw 404 error when knowledge point not found", async () => {
      const updateDto: UpdateKnowledgeDto = {
        content: "更新后的内容",
        knowledgePoint: "page_setup",
        grade: "5年级",
        type: "知识点",
        parentId: "K002",
        parentName: "Word操作基础",
        relatedKnowledgeIds: ["K003", "K004"],
        relatedKnowledgeNames: ["设置字体", "设置段落"],
      };

      jest.spyOn(service, "update").mockResolvedValue(null);

      await expect(controller.update("K999", updateDto)).rejects.toThrow(
        HttpException,
      );
      await expect(controller.update("K999", updateDto)).rejects.toThrow(
        "知识点不存在",
      );
      await expect(controller.update("K999", updateDto)).rejects.toMatchObject({
        status: HttpStatus.NOT_FOUND,
      });
    });

    it("should throw 400 error with invalid data", async () => {
      const invalidDto = {
        content: "", // 空内容
        knowledgePoint: "page_setup",
        grade: "5年级",
        type: "知识点",
        parentId: "K002",
        parentName: "Word操作基础",
        relatedKnowledgeIds: ["K003", "K004"],
        relatedKnowledgeNames: ["设置字体", "设置段落"],
      };

      await expect(
        controller.update("K001", invalidDto as any),
      ).rejects.toThrow(HttpException);
      await expect(
        controller.update("K001", invalidDto as any),
      ).rejects.toMatchObject({ status: HttpStatus.BAD_REQUEST });
    });
  });

  describe("delete", () => {
    it("should delete knowledge point successfully", async () => {
      const mockResponse = { message: "知识点删除成功" };

      jest.spyOn(service, "delete").mockResolvedValue(mockResponse);

      const result = await controller.delete("K001");

      expect(result).toEqual(mockResponse);
      expect(service.delete).toHaveBeenCalledWith("K001");
    });

    it("should throw 404 error when knowledge point not found", async () => {
      jest
        .spyOn(service, "delete")
        .mockRejectedValue(new Error("知识点不存在"));

      await expect(controller.delete("K999")).rejects.toThrow(HttpException);
      await expect(controller.delete("K999")).rejects.toThrow("知识点不存在");
      await expect(controller.delete("K999")).rejects.toMatchObject({
        status: HttpStatus.NOT_FOUND,
      });
    });
  });
});
