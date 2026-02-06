import { Test, TestingModule } from "@nestjs/testing";
import { GraphController } from "./graph.controller";
import { GraphService } from "./graph.service";

describe("GraphController", () => {
  let controller: GraphController;
  let service: GraphService;

  beforeEach(async () => {
    const module: TestingModule = await Test.createTestingModule({
      controllers: [GraphController],
      providers: [
        {
          provide: GraphService,
          useValue: {
            getGraphData: jest.fn(),
          },
        },
      ],
    }).compile();

    controller = module.get<GraphController>(GraphController);
    service = module.get<GraphService>(GraphService);
  });

  describe("getGraphData", () => {
    it("should return complete graph data with no filters", async () => {
      const mockGraphData = {
        nodes: [
          {
            id: "S001",
            type: "STUDENT",
            name: "陆雨欣",
            group: 3,
            val: 8,
            studentProfile: {
              school: "湖州市爱山小学教育集团常溪小学",
              grade: "5年级",
              classId: "新五年级2班",
              knowledgeReserve: 5,
              learningEngagement: 5,
              cognitiveLoad: 3,
              learningMotivation: 5,
              computationalThinking: 4,
              humanAiTrust: 3,
              learningMethod: 5,
              learningAttitude: 5,
            },
          },
          {
            id: "T001",
            type: "TEACHER",
            name: "教师 A",
            group: 1,
            val: 25,
            teacherProfile: {
              school: "湖州市爱山小学教育集团常溪小学",
              teachingGrade: "5年级",
              teachingClass: "新五年级2班",
            },
          },
          {
            id: "K001",
            type: "KNOWLEDGE",
            name: "插入图片",
            group: 2,
            val: 15,
            knowledgeProfile: {
              content:
                '将光标定位到要插入图片的位置，点击"插入"选项卡，点击"图片"按钮，选择本地图片上传。',
              type: "知识点",
              parentId: "K002",
              parentName: "Word操作基础",
              relatedKnowledgeIds: ["K003", "K004"],
              relatedKnowledgeNames: ["设置字体", "设置段落"],
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

      jest.spyOn(service, "getGraphData").mockResolvedValue(mockGraphData);

      const result = await controller.getGraphData(
        undefined,
        undefined,
        undefined,
        undefined,
      );

      expect(result).toEqual(mockGraphData);
      expect(service.getGraphData).toHaveBeenCalledWith({
        scenario: undefined,
        school: undefined,
        grade: undefined,
        classId: undefined,
      });
    });

    it("should return graph data with school filter", async () => {
      const mockGraphData = {
        nodes: [
          {
            id: "S001",
            type: "STUDENT",
            name: "陆雨欣",
            group: 3,
            val: 8,
            studentProfile: {
              school: "湖州市爱山小学教育集团常溪小学",
              grade: "5年级",
              classId: "新五年级2班",
              knowledgeReserve: 5,
              learningEngagement: 5,
              cognitiveLoad: 3,
              learningMotivation: 5,
              computationalThinking: 4,
              humanAiTrust: 3,
              learningMethod: 5,
              learningAttitude: 5,
            },
          },
        ],
        links: [],
      };

      jest.spyOn(service, "getGraphData").mockResolvedValue(mockGraphData);

      const result = await controller.getGraphData(
        undefined,
        "湖州市爱山小学教育集团常溪小学",
        undefined,
        undefined,
      );

      expect(result).toEqual(mockGraphData);
      expect(service.getGraphData).toHaveBeenCalledWith({
        scenario: undefined,
        school: "湖州市爱山小学教育集团常溪小学",
        grade: undefined,
        classId: undefined,
      });
    });

    it("should return graph data with grade filter", async () => {
      const mockGraphData = {
        nodes: [
          {
            id: "S001",
            type: "STUDENT",
            name: "陆雨欣",
            group: 3,
            val: 8,
            studentProfile: {
              school: "湖州市爱山小学教育集团常溪小学",
              grade: "5年级",
              classId: "新五年级2班",
              knowledgeReserve: 5,
              learningEngagement: 5,
              cognitiveLoad: 3,
              learningMotivation: 5,
              computationalThinking: 4,
              humanAiTrust: 3,
              learningMethod: 5,
              learningAttitude: 5,
            },
          },
          {
            id: "K001",
            type: "KNOWLEDGE",
            name: "插入图片",
            group: 2,
            val: 15,
            knowledgeProfile: {
              content:
                '将光标定位到要插入图片的位置，点击"插入"选项卡，点击"图片"按钮，选择本地图片上传。',
              type: "知识点",
              parentId: "K002",
              parentName: "Word操作基础",
              relatedKnowledgeIds: ["K003", "K004"],
              relatedKnowledgeNames: ["设置字体", "设置段落"],
            },
          },
        ],
        links: [
          {
            source: "S001",
            target: "K001",
            value: 1.5,
            type: "PLATFORM",
          },
        ],
      };

      jest.spyOn(service, "getGraphData").mockResolvedValue(mockGraphData);

      const result = await controller.getGraphData(
        undefined,
        undefined,
        "5年级",
        undefined,
      );

      expect(result).toEqual(mockGraphData);
      expect(service.getGraphData).toHaveBeenCalledWith({
        scenario: undefined,
        school: undefined,
        grade: "5年级",
        classId: undefined,
      });
    });

    it("should return graph data with class filter", async () => {
      const mockGraphData = {
        nodes: [
          {
            id: "S001",
            type: "STUDENT",
            name: "陆雨欣",
            group: 3,
            val: 8,
            studentProfile: {
              school: "湖州市爱山小学教育集团常溪小学",
              grade: "5年级",
              classId: "新五年级2班",
              knowledgeReserve: 5,
              learningEngagement: 5,
              cognitiveLoad: 3,
              learningMotivation: 5,
              computationalThinking: 4,
              humanAiTrust: 3,
              learningMethod: 5,
              learningAttitude: 5,
            },
          },
        ],
        links: [],
      };

      jest.spyOn(service, "getGraphData").mockResolvedValue(mockGraphData);

      const result = await controller.getGraphData(
        undefined,
        undefined,
        undefined,
        "新五年级2班",
      );

      expect(result).toEqual(mockGraphData);
      expect(service.getGraphData).toHaveBeenCalledWith({
        scenario: undefined,
        school: undefined,
        grade: undefined,
        classId: "新五年级2班",
      });
    });

    it("should return graph data with scenario filter", async () => {
      const mockGraphData = {
        nodes: [
          {
            id: "S001",
            type: "STUDENT",
            name: "陆雨欣",
            group: 3,
            val: 8,
            studentProfile: {
              school: "湖州市爱山小学教育集团常溪小学",
              grade: "5年级",
              classId: "新五年级2班",
              knowledgeReserve: 5,
              learningEngagement: 5,
              cognitiveLoad: 3,
              learningMotivation: 5,
              computationalThinking: 4,
              humanAiTrust: 3,
              learningMethod: 5,
              learningAttitude: 5,
            },
          },
        ],
        links: [],
      };

      jest.spyOn(service, "getGraphData").mockResolvedValue(mockGraphData);

      const result = await controller.getGraphData(
        "COLLABORATIVE",
        undefined,
        undefined,
        undefined,
      );

      expect(result).toEqual(mockGraphData);
      expect(service.getGraphData).toHaveBeenCalledWith({
        scenario: "COLLABORATIVE",
        school: undefined,
        grade: undefined,
        classId: undefined,
      });
    });

    it("should validate node structure for STUDENT type", async () => {
      const mockGraphData = {
        nodes: [
          {
            id: "S001",
            type: "STUDENT",
            name: "陆雨欣",
            group: 3,
            val: 8,
            studentProfile: {
              gender: "女",
              school: "湖州市爱山小学教育集团常溪小学",
              grade: "5年级",
              classId: "新五年级2班",
              knowledgeReserve: 5,
              learningEngagement: 5,
              cognitiveLoad: 3,
              learningMotivation: 5,
              computationalThinking: 4,
              humanAiTrust: 3,
              learningMethod: 5,
              learningAttitude: 5,
            },
          },
        ],
        links: [],
      };

      jest.spyOn(service, "getGraphData").mockResolvedValue(mockGraphData);

      const result = await controller.getGraphData();

      expect(result.nodes).toHaveLength(1);
      expect(result.nodes[0]).toHaveProperty("id");
      expect(result.nodes[0]).toHaveProperty("type", "STUDENT");
      expect(result.nodes[0]).toHaveProperty("name");
      expect(result.nodes[0]).toHaveProperty("group");
      expect(result.nodes[0]).toHaveProperty("val");
      expect(result.nodes[0]).toHaveProperty("studentProfile");
      expect(result.nodes[0].studentProfile).toHaveProperty("school");
      expect(result.nodes[0].studentProfile).toHaveProperty("grade");
      expect(result.nodes[0].studentProfile).toHaveProperty("classId");
      expect(result.nodes[0].studentProfile).toHaveProperty("knowledgeReserve");
      expect(result.nodes[0].studentProfile).toHaveProperty(
        "learningEngagement",
      );
    });

    it("should validate node structure for TEACHER type", async () => {
      const mockGraphData = {
        nodes: [
          {
            id: "T001",
            type: "TEACHER",
            name: "教师 A",
            group: 1,
            val: 25,
            teacherProfile: {
              school: "湖州市爱山小学教育集团常溪小学",
              teachingGrade: "5年级",
              teachingClass: "新五年级2班",
            },
          },
        ],
        links: [],
      };

      jest.spyOn(service, "getGraphData").mockResolvedValue(mockGraphData);

      const result = await controller.getGraphData();

      expect(result.nodes).toHaveLength(1);
      expect(result.nodes[0]).toHaveProperty("id");
      expect(result.nodes[0]).toHaveProperty("type", "TEACHER");
      expect(result.nodes[0]).toHaveProperty("name");
      expect(result.nodes[0]).toHaveProperty("group");
      expect(result.nodes[0]).toHaveProperty("val");
      expect(result.nodes[0]).toHaveProperty("teacherProfile");
      expect(result.nodes[0].teacherProfile).toHaveProperty("school");
      expect(result.nodes[0].teacherProfile).toHaveProperty("teachingGrade");
      expect(result.nodes[0].teacherProfile).toHaveProperty("teachingClass");
    });

    it("should validate node structure for KNOWLEDGE type", async () => {
      const mockGraphData = {
        nodes: [
          {
            id: "K001",
            type: "KNOWLEDGE",
            name: "插入图片",
            group: 2,
            val: 15,
            knowledgeProfile: {
              content:
                '将光标定位到要插入图片的位置，点击"插入"选项卡，点击"图片"按钮，选择本地图片上传。',
              type: "知识点",
              parentId: "K002",
              parentName: "Word操作基础",
              relatedKnowledgeIds: ["K003", "K004"],
              relatedKnowledgeNames: ["设置字体", "设置段落"],
            },
          },
        ],
        links: [],
      };

      jest.spyOn(service, "getGraphData").mockResolvedValue(mockGraphData);

      const result = await controller.getGraphData();

      expect(result.nodes).toHaveLength(1);
      expect(result.nodes[0]).toHaveProperty("id");
      expect(result.nodes[0]).toHaveProperty("type", "KNOWLEDGE");
      expect(result.nodes[0]).toHaveProperty("name");
      expect(result.nodes[0]).toHaveProperty("group");
      expect(result.nodes[0]).toHaveProperty("val");
      expect(result.nodes[0]).toHaveProperty("knowledgeProfile");
      expect(result.nodes[0].knowledgeProfile).toHaveProperty("content");
      expect(result.nodes[0].knowledgeProfile).toHaveProperty("type");
      expect(result.nodes[0].knowledgeProfile).toHaveProperty("parentId");
      expect(result.nodes[0].knowledgeProfile).toHaveProperty("parentName");
      expect(result.nodes[0].knowledgeProfile).toHaveProperty(
        "relatedKnowledgeIds",
      );
      expect(result.nodes[0].knowledgeProfile).toHaveProperty(
        "relatedKnowledgeNames",
      );
    });

    it("should validate link structure", async () => {
      const mockGraphData = {
        nodes: [],
        links: [
          {
            source: "S001",
            target: "T001",
            value: 2,
            type: "PHYSICAL",
          },
        ],
      };

      jest.spyOn(service, "getGraphData").mockResolvedValue(mockGraphData);

      const result = await controller.getGraphData();

      expect(result.links).toHaveLength(1);
      expect(result.links[0]).toHaveProperty("source");
      expect(result.links[0]).toHaveProperty("target");
      expect(result.links[0]).toHaveProperty("value");
      expect(result.links[0]).toHaveProperty("type");
    });
  });
});
