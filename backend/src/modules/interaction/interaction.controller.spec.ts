import { Test, TestingModule } from "@nestjs/testing";
import { INestApplication } from "@nestjs/common";
import * as request from "supertest";
import { InteractionController } from "./interaction.controller";
import { InteractionService } from "./interaction.service";
import { CreateInteractionDto } from "./interaction.dto";

const mockInteractionService = {
  findAll: jest.fn(),
  create: jest.fn(),
};

describe("InteractionController", () => {
  let app: INestApplication;

  beforeEach(async () => {
    const moduleFixture: TestingModule = await Test.createTestingModule({
      controllers: [InteractionController],
      providers: [
        {
          provide: InteractionService,
          useValue: mockInteractionService,
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

  describe("GET /api/v1/interactions", () => {
    it("should return an array of interactions", async () => {
      const mockInteractions = [
        {
          id: "I001",
          sourceId: "S001",
          targetId: "S002",
          sourceType: "STUDENT",
          targetType: "STUDENT",
          value: 1,
          type: "PLATFORM",
          interactionType: "like",
        },
      ];

      mockInteractionService.findAll.mockResolvedValue(mockInteractions);

      const response = await request(app.getHttpServer()).get(
        "/api/v1/interactions",
      );
      expect(response.status).toBe(200);
      expect(response.body).toEqual(mockInteractions);
    });

    it("should handle query parameters", async () => {
      const mockInteractions = [
        {
          id: "I001",
          sourceId: "S001",
          targetId: "K001",
          sourceType: "STUDENT",
          targetType: "KNOWLEDGE",
          value: 1.5,
          type: "PLATFORM",
        },
      ];

      mockInteractionService.findAll.mockResolvedValue(mockInteractions);

      const response = await request(app.getHttpServer())
        .get("/api/v1/interactions")
        .query({
          source_id: "S001",
          target_id: "K001",
          source_type: "STUDENT",
          target_type: "KNOWLEDGE",
          type: "PLATFORM",
        });
      expect(response.status).toBe(200);
      expect(response.body).toEqual(mockInteractions);
    });
  });

  describe("POST /api/v1/interactions", () => {
    it("should create a new interaction", async () => {
      const createInteractionDto: CreateInteractionDto = {
        sourceId: "S001",
        targetId: "K001",
        sourceType: "STUDENT",
        targetType: "KNOWLEDGE",
        value: 1.5,
        type: "PLATFORM",
        interactionType: "view",
      };

      const mockInteraction = {
        id: "I001",
        ...createInteractionDto,
      };

      mockInteractionService.create.mockResolvedValue(mockInteraction);

      const response = await request(app.getHttpServer())
        .post("/api/v1/interactions")
        .send(createInteractionDto);
      expect(response.status).toBe(201);
      expect(response.body).toEqual(mockInteraction);
    });

    it("should handle validation errors", async () => {
      const invalidInteractionDto = {
        sourceId: "",
        targetId: "",
        sourceType: "",
        targetType: "",
        value: 0,
        type: "",
      };

      const response = await request(app.getHttpServer())
        .post("/api/v1/interactions")
        .send(invalidInteractionDto);
      expect(response.status).toBe(400);
      expect(Array.isArray(response.body)).toBe(true);
    });
  });
});
