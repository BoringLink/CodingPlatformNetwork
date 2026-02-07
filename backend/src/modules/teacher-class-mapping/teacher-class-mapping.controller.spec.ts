import { Test, TestingModule } from '@nestjs/testing';
import { TeacherClassMappingController } from './teacher-class-mapping.controller';
import { TeacherClassMappingService } from './teacher-class-mapping.service';
import { PrismaService } from '../../shared/utils/prisma.service';
import { HttpException } from '@nestjs/common';

const mockTeacherClassMappingService = {
  findAll: jest.fn(),
  create: jest.fn(),
  delete: jest.fn(),
};

const mockPrismaService = {};

describe('TeacherClassMappingController', () => {
  let controller: TeacherClassMappingController;

  beforeEach(async () => {
    const module: TestingModule = await Test.createTestingModule({
      controllers: [TeacherClassMappingController],
      providers: [
        {
          provide: TeacherClassMappingService,
          useValue: mockTeacherClassMappingService,
        },
        {
          provide: PrismaService,
          useValue: mockPrismaService,
        },
      ],
    }).compile();

    controller = module.get<TeacherClassMappingController>(TeacherClassMappingController);
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  describe('findAll', () => {
    it('should return teacher-class mappings with query parameters', async () => {
      const mockMappings = [
        {
          id: '1',
          teacherId: 'T001',
          grade: '5年级',
          classId: '新五年级2班',
          createdAt: new Date(),
          updatedAt: new Date(),
        },
      ];
      mockTeacherClassMappingService.findAll.mockResolvedValue(mockMappings);

      const result = await controller.findAll('T001', '5年级', '新五年级2班');

      expect(result).toEqual({ data: mockMappings });
      expect(mockTeacherClassMappingService.findAll).toHaveBeenCalledWith({
        teacherId: 'T001',
        grade: '5年级',
        classId: '新五年级2班',
      });
    });

    it('should return teacher-class mappings without query parameters', async () => {
      const mockMappings = [];
      mockTeacherClassMappingService.findAll.mockResolvedValue(mockMappings);

      const result = await controller.findAll();

      expect(result).toEqual({ data: mockMappings });
      expect(mockTeacherClassMappingService.findAll).toHaveBeenCalledWith({});
    });
  });

  describe('create', () => {
    it('should create a teacher-class mapping with valid data', async () => {
      const createDto = {
        teacherId: 'T001',
        grade: '5年级',
        classId: '新五年级2班',
      };
      const mockCreatedMapping = {
        id: '1',
        ...createDto,
        createdAt: new Date(),
        updatedAt: new Date(),
      };
      mockTeacherClassMappingService.create.mockResolvedValue(mockCreatedMapping);

      const result = await controller.create(createDto);

      expect(result).toEqual(mockCreatedMapping);
      expect(mockTeacherClassMappingService.create).toHaveBeenCalledWith(createDto);
    });

    it('should throw BadRequestException with invalid data', async () => {
      const invalidDto = {
        teacherId: '',
        grade: '5年级',
        classId: '新五年级2班',
      };

      await expect(controller.create(invalidDto)).rejects.toThrow(HttpException);
    });
  });

  describe('delete', () => {
    it('should delete a teacher-class mapping successfully', async () => {
      const mockResponse = {
        message: '教师-班级关联删除成功',
      };
      mockTeacherClassMappingService.delete.mockResolvedValue(mockResponse);

      const result = await controller.delete('1');

      expect(result).toEqual(mockResponse);
      expect(mockTeacherClassMappingService.delete).toHaveBeenCalledWith('1');
    });

    it('should throw NotFoundException when mapping not found', async () => {
      mockTeacherClassMappingService.delete.mockRejectedValue(new Error());

      await expect(controller.delete('999')).rejects.toThrow(HttpException);
    });
  });
});
