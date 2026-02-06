import { Test, TestingModule } from '@nestjs/testing';
import { InteractionController } from './interaction.controller';
import { InteractionService } from './interaction.service';
import { HttpException, HttpStatus } from '@nestjs/common';
import { CreateInteractionDto } from './interaction.dto';

describe('InteractionController', () => {
  let controller: InteractionController;
  let service: InteractionService;

  beforeEach(async () => {
    const module: TestingModule = await Test.createTestingModule({
      controllers: [InteractionController],
      providers: [
        {
          provide: InteractionService,
          useValue: {
            findAll: jest.fn(),
            create: jest.fn(),
          },
        },
      ],
    }).compile();

    controller = module.get<InteractionController>(InteractionController);
    service = module.get<InteractionService>(InteractionService);
  });

  describe('findAll', () => {
    it('should return interactions list with no filters', async () => {
      const mockInteractions = [
        {
          id: 'I001',
          sourceId: 'S001',
          targetId: 'S002',
          sourceType: 'STUDENT',
          targetType: 'STUDENT',
          value: 1,
          type: 'PLATFORM',
          interactionType: 'like',
          createdAt: new Date(),
          updatedAt: new Date(),
        },
      ];

      jest.spyOn(service, 'findAll').mockResolvedValue({ data: mockInteractions });

      const result = await controller.findAll(
        undefined, undefined, undefined, undefined, undefined
      );

      expect(result).toEqual({ data: mockInteractions });
      expect(service.findAll).toHaveBeenCalledWith({
        sourceId: undefined,
        targetId: undefined,
        sourceType: undefined,
        targetType: undefined,
        type: undefined,
      });
    });

    it('should return interactions list with source_id filter', async () => {
      const mockInteractions = [
        {
          id: 'I001',
          sourceId: 'S001',
          targetId: 'S002',
          sourceType: 'STUDENT',
          targetType: 'STUDENT',
          value: 1,
          type: 'PLATFORM',
          interactionType: 'like',
          createdAt: new Date(),
          updatedAt: new Date(),
        },
      ];

      jest.spyOn(service, 'findAll').mockResolvedValue({ data: mockInteractions });

      const result = await controller.findAll(
        'S001', undefined, undefined, undefined, undefined
      );

      expect(result).toEqual({ data: mockInteractions });
      expect(service.findAll).toHaveBeenCalledWith({
        sourceId: 'S001',
        targetId: undefined,
        sourceType: undefined,
        targetType: undefined,
        type: undefined,
      });
    });

    it('should return interactions list with target_id filter', async () => {
      const mockInteractions = [
        {
          id: 'I001',
          sourceId: 'S001',
          targetId: 'K001',
          sourceType: 'STUDENT',
          targetType: 'KNOWLEDGE',
          value: 1.5,
          type: 'PLATFORM',
          interactionType: 'study',
          createdAt: new Date(),
          updatedAt: new Date(),
        },
      ];

      jest.spyOn(service, 'findAll').mockResolvedValue({ data: mockInteractions });

      const result = await controller.findAll(
        undefined, 'K001', undefined, undefined, undefined
      );

      expect(result).toEqual({ data: mockInteractions });
      expect(service.findAll).toHaveBeenCalledWith({
        sourceId: undefined,
        targetId: 'K001',
        sourceType: undefined,
        targetType: undefined,
        type: undefined,
      });
    });

    it('should return interactions list with source_type filter', async () => {
      const mockInteractions = [
        {
          id: 'I001',
          sourceId: 'S001',
          targetId: 'S002',
          sourceType: 'STUDENT',
          targetType: 'STUDENT',
          value: 1,
          type: 'PLATFORM',
          interactionType: 'like',
          createdAt: new Date(),
          updatedAt: new Date(),
        },
      ];

      jest.spyOn(service, 'findAll').mockResolvedValue({ data: mockInteractions });

      const result = await controller.findAll(
        undefined, undefined, 'STUDENT', undefined, undefined
      );

      expect(result).toEqual({ data: mockInteractions });
      expect(service.findAll).toHaveBeenCalledWith({
        sourceId: undefined,
        targetId: undefined,
        sourceType: 'STUDENT',
        targetType: undefined,
        type: undefined,
      });
    });

    it('should return interactions list with target_type filter', async () => {
      const mockInteractions = [
        {
          id: 'I001',
          sourceId: 'S001',
          targetId: 'K001',
          sourceType: 'STUDENT',
          targetType: 'KNOWLEDGE',
          value: 1.5,
          type: 'PLATFORM',
          interactionType: 'study',
          createdAt: new Date(),
          updatedAt: new Date(),
        },
      ];

      jest.spyOn(service, 'findAll').mockResolvedValue({ data: mockInteractions });

      const result = await controller.findAll(
        undefined, undefined, undefined, 'KNOWLEDGE', undefined
      );

      expect(result).toEqual({ data: mockInteractions });
      expect(service.findAll).toHaveBeenCalledWith({
        sourceId: undefined,
        targetId: undefined,
        sourceType: undefined,
        targetType: 'KNOWLEDGE',
        type: undefined,
      });
    });

    it('should return interactions list with type filter', async () => {
      const mockInteractions = [
        {
          id: 'I001',
          sourceId: 'S001',
          targetId: 'T001',
          sourceType: 'STUDENT',
          targetType: 'TEACHER',
          value: 2,
          type: 'PHYSICAL',
          interactionType: 'ask',
          createdAt: new Date(),
          updatedAt: new Date(),
        },
      ];

      jest.spyOn(service, 'findAll').mockResolvedValue({ data: mockInteractions });

      const result = await controller.findAll(
        undefined, undefined, undefined, undefined, 'PHYSICAL'
      );

      expect(result).toEqual({ data: mockInteractions });
      expect(service.findAll).toHaveBeenCalledWith({
        sourceId: undefined,
        targetId: undefined,
        sourceType: undefined,
        targetType: undefined,
        type: 'PHYSICAL',
      });
    });
  });

  describe('create', () => {
    it('should create interaction with valid data', async () => {
      const createDto: CreateInteractionDto = {
        sourceId: 'S001',
        targetId: 'K001',
        sourceType: 'STUDENT',
        targetType: 'KNOWLEDGE',
        value: 1.5,
        type: 'PLATFORM',
        interactionType: 'study',
      };

      const mockInteraction = {
        id: 'I002',
        sourceId: createDto.sourceId,
        targetId: createDto.targetId,
        sourceType: createDto.sourceType,
        targetType: createDto.targetType,
        value: createDto.value,
        type: createDto.type,
        interactionType: createDto.interactionType,
        createdAt: new Date(),
        updatedAt: new Date(),
      };

      jest.spyOn(service, 'create').mockResolvedValue(mockInteraction);

      const result = await controller.create(createDto);

      expect(result).toEqual(mockInteraction);
      expect(service.create).toHaveBeenCalledWith(createDto);
    });

    it('should throw 400 error with invalid data', async () => {
      const invalidDto = {
        sourceId: '', // 空sourceId
        targetId: 'K001',
        sourceType: 'STUDENT',
        targetType: 'KNOWLEDGE',
        value: 1.5,
        type: 'PLATFORM',
      };

      await expect(controller.create(invalidDto as any)).rejects.toThrow(HttpException);
      await expect(controller.create(invalidDto as any)).rejects.toMatchObject({ status: HttpStatus.BAD_REQUEST });
    });

    it('should throw 400 error with invalid sourceType', async () => {
      const invalidDto = {
        sourceId: 'S001',
        targetId: 'K001',
        sourceType: 'INVALID', // 无效的sourceType
        targetType: 'KNOWLEDGE',
        value: 1.5,
        type: 'PLATFORM',
      };

      await expect(controller.create(invalidDto as any)).rejects.toThrow(HttpException);
      await expect(controller.create(invalidDto as any)).rejects.toMatchObject({ status: HttpStatus.BAD_REQUEST });
    });

    it('should throw 400 error with invalid targetType', async () => {
      const invalidDto = {
        sourceId: 'S001',
        targetId: 'K001',
        sourceType: 'STUDENT',
        targetType: 'INVALID', // 无效的targetType
        value: 1.5,
        type: 'PLATFORM',
      };

      await expect(controller.create(invalidDto as any)).rejects.toThrow(HttpException);
      await expect(controller.create(invalidDto as any)).rejects.toMatchObject({ status: HttpStatus.BAD_REQUEST });
    });

    it('should throw 400 error with invalid type', async () => {
      const invalidDto = {
        sourceId: 'S001',
        targetId: 'K001',
        sourceType: 'STUDENT',
        targetType: 'KNOWLEDGE',
        value: 1.5,
        type: 'INVALID', // 无效的type
      };

      await expect(controller.create(invalidDto as any)).rejects.toThrow(HttpException);
      await expect(controller.create(invalidDto as any)).rejects.toMatchObject({ status: HttpStatus.BAD_REQUEST });
    });

    it('should throw 400 error with out-of-range value', async () => {
      const invalidDto = {
        sourceId: 'S001',
        targetId: 'K001',
        sourceType: 'STUDENT',
        targetType: 'KNOWLEDGE',
        value: 6, // 超出最大值5
        type: 'PLATFORM',
      };

      await expect(controller.create(invalidDto as any)).rejects.toThrow(HttpException);
      await expect(controller.create(invalidDto as any)).rejects.toMatchObject({ status: HttpStatus.BAD_REQUEST });
    });

    it('should throw 400 error with value below minimum', async () => {
      const invalidDto = {
        sourceId: 'S001',
        targetId: 'K001',
        sourceType: 'STUDENT',
        targetType: 'KNOWLEDGE',
        value: 0, // 低于最小值0.1
        type: 'PLATFORM',
      };

      await expect(controller.create(invalidDto as any)).rejects.toThrow(HttpException);
      await expect(controller.create(invalidDto as any)).rejects.toMatchObject({ status: HttpStatus.BAD_REQUEST });
    });
  });
});