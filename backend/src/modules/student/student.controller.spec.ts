import { Test, TestingModule } from '@nestjs/testing';
import { StudentController } from './student.controller';
import { StudentService } from './student.service';
import { HttpException, HttpStatus } from '@nestjs/common';
import { CreateStudentDto, UpdateStudentDto } from './student.dto';

describe('StudentController', () => {
  let controller: StudentController;
  let service: StudentService;

  beforeEach(async () => {
    const module: TestingModule = await Test.createTestingModule({
      controllers: [StudentController],
      providers: [
        {
          provide: StudentService,
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

    controller = module.get<StudentController>(StudentController);
    service = module.get<StudentService>(StudentService);
  });

  describe('findAll', () => {
    it('should return students list with no filters', async () => {
      const mockStudents = [
        {
          id: 'S001',
          name: '陆雨欣',
          school: '湖州市爱山小学教育集团常溪小学',
          grade: '5年级',
          classId: '新五年级2班',
          knowledgeReserve: 5,
          learningEngagement: 5,
          cognitiveLoad: 3,
          learningMotivation: 5,
          computationalThinking: 4,
          humanAiTrust: 3,
          learningMethod: 5,
          learningAttitude: 5,
          createdAt: new Date(),
          updatedAt: new Date(),
        },
      ];

      jest.spyOn(service, 'findAll').mockResolvedValue(mockStudents);

      const result = await controller.findAll(undefined, undefined, undefined);

      expect(result).toEqual(mockStudents);
      expect(service.findAll).toHaveBeenCalledWith({ school: undefined, grade: undefined, classId: undefined });
    });

    it('should return students list with school filter', async () => {
      const mockStudents = [
        {
          id: 'S001',
          name: '陆雨欣',
          school: '湖州市爱山小学教育集团常溪小学',
          grade: '5年级',
          classId: '新五年级2班',
          knowledgeReserve: 5,
          learningEngagement: 5,
          cognitiveLoad: 3,
          learningMotivation: 5,
          computationalThinking: 4,
          humanAiTrust: 3,
          learningMethod: 5,
          learningAttitude: 5,
          createdAt: new Date(),
          updatedAt: new Date(),
        },
      ];

      jest.spyOn(service, 'findAll').mockResolvedValue(mockStudents);

      const result = await controller.findAll('湖州市爱山小学教育集团常溪小学', undefined, undefined);

      expect(result).toEqual(mockStudents);
      expect(service.findAll).toHaveBeenCalledWith({ school: '湖州市爱山小学教育集团常溪小学', grade: undefined, classId: undefined });
    });

    it('should return students list with grade and class filters', async () => {
      const mockStudents = [
        {
          id: 'S001',
          name: '陆雨欣',
          school: '湖州市爱山小学教育集团常溪小学',
          grade: '5年级',
          classId: '新五年级2班',
          knowledgeReserve: 5,
          learningEngagement: 5,
          cognitiveLoad: 3,
          learningMotivation: 5,
          computationalThinking: 4,
          humanAiTrust: 3,
          learningMethod: 5,
          learningAttitude: 5,
          createdAt: new Date(),
          updatedAt: new Date(),
        },
      ];

      jest.spyOn(service, 'findAll').mockResolvedValue(mockStudents);

      const result = await controller.findAll(undefined, '5年级', '新五年级2班');

      expect(result).toEqual(mockStudents);
      expect(service.findAll).toHaveBeenCalledWith({ school: undefined, grade: '5年级', classId: '新五年级2班' });
    });
  });

  describe('findOne', () => {
    it('should return student by id', async () => {
      const mockStudent = {
        id: 'S001',
        name: '陆雨欣',
        school: '湖州市爱山小学教育集团常溪小学',
        grade: '5年级',
        classId: '新五年级2班',
        knowledgeReserve: 5,
        learningEngagement: 5,
        cognitiveLoad: 3,
        learningMotivation: 5,
        computationalThinking: 4,
        humanAiTrust: 3,
        learningMethod: 5,
        learningAttitude: 5,
        createdAt: new Date(),
        updatedAt: new Date(),
      };

      jest.spyOn(service, 'findOne').mockResolvedValue(mockStudent);

      const result = await controller.findOne('S001');

      expect(result).toEqual(mockStudent);
      expect(service.findOne).toHaveBeenCalledWith('S001');
    });

    it('should throw 404 error when student not found', async () => {
      jest.spyOn(service, 'findOne').mockResolvedValue(null);

      await expect(controller.findOne('S999')).rejects.toThrow(HttpException);
      await expect(controller.findOne('S999')).rejects.toThrow('学生不存在');
      await expect(controller.findOne('S999')).rejects.toMatchObject({ status: HttpStatus.NOT_FOUND });
    });
  });

  describe('create', () => {
    it('should create student with valid data', async () => {
      const createDto: CreateStudentDto = {
        name: '张三',
        school: '杭州市文澜实验学校',
        grade: '4年级',
        classId: '四年级10班',
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
        id: 'S002',
        name: createDto.name,
        school: createDto.school,
        grade: createDto.grade,
        classId: createDto.classId,
        knowledgeReserve: createDto.knowledgeReserve,
        learningEngagement: createDto.learningEngagement,
        cognitiveLoad: createDto.cognitiveLoad,
        learningMotivation: createDto.learningMotivation,
        computationalThinking: createDto.computationalThinking,
        humanAiTrust: createDto.humanAiTrust,
        learningMethod: createDto.learningMethod,
        learningAttitude: createDto.learningAttitude,
        createdAt: new Date(),
        updatedAt: new Date(),
      };

      jest.spyOn(service, 'create').mockResolvedValue(mockStudent);

      const result = await controller.create(createDto);

      expect(result).toEqual(mockStudent);
      expect(service.create).toHaveBeenCalledWith(createDto);
    });

    it('should throw 400 error with invalid data', async () => {
      const invalidDto = {
        name: '', // 空姓名
        school: '杭州市文澜实验学校',
        grade: '4年级',
        classId: '四年级10班',
        knowledgeReserve: 4,
        learningEngagement: 4,
        cognitiveLoad: 3,
        learningMotivation: 4,
        computationalThinking: 3,
        humanAiTrust: 4,
        learningMethod: 3,
        learningAttitude: 4,
      };

      await expect(controller.create(invalidDto as any)).rejects.toThrow(HttpException);
      await expect(controller.create(invalidDto as any)).rejects.toMatchObject({ status: HttpStatus.BAD_REQUEST });
    });



    it('should throw 400 error with out-of-range values', async () => {
      const invalidDto = {
        name: '张三',
        school: '杭州市文澜实验学校',
        grade: '4年级',
        classId: '四年级10班',
        knowledgeReserve: 6, // 超出最大值5
        learningEngagement: 0, // 低于最小值1
        cognitiveLoad: 3,
        learningMotivation: 4,
        computationalThinking: 3,
        humanAiTrust: 4,
        learningMethod: 3,
        learningAttitude: 4,
      };

      await expect(controller.create(invalidDto as any)).rejects.toThrow(HttpException);
      await expect(controller.create(invalidDto as any)).rejects.toMatchObject({ status: HttpStatus.BAD_REQUEST });
    });
  });

  describe('update', () => {
    it('should update student with valid data', async () => {
      const updateDto: UpdateStudentDto = {
        knowledgeReserve: 5,
        learningEngagement: 5,
      };

      const mockStudent = {
        id: 'S001',
        name: '陆雨欣',
        school: '湖州市爱山小学教育集团常溪小学',
        grade: '5年级',
        classId: '新五年级2班',
        knowledgeReserve: 5,
        learningEngagement: 5,
        cognitiveLoad: 3,
        learningMotivation: 5,
        computationalThinking: 4,
        humanAiTrust: 3,
        learningMethod: 5,
        learningAttitude: 5,
        createdAt: new Date(),
        updatedAt: new Date(),
      };

      jest.spyOn(service, 'update').mockResolvedValue(mockStudent);

      const result = await controller.update('S001', updateDto);

      expect(result).toEqual(mockStudent);
      expect(service.update).toHaveBeenCalledWith('S001', updateDto);
    });

    it('should throw 404 error when student not found', async () => {
      const updateDto: UpdateStudentDto = {
        knowledgeReserve: 5,
      };

      jest.spyOn(service, 'update').mockResolvedValue(null);

      await expect(controller.update('S999', updateDto)).rejects.toThrow(HttpException);
      await expect(controller.update('S999', updateDto)).rejects.toThrow('学生不存在');
      await expect(controller.update('S999', updateDto)).rejects.toMatchObject({ status: HttpStatus.NOT_FOUND });
    });

    it('should throw 400 error with invalid data', async () => {
      const invalidDto = {
        knowledgeReserve: 6, // 超出最大值5
      };

      await expect(controller.update('S001', invalidDto as any)).rejects.toThrow(HttpException);
      await expect(controller.update('S001', invalidDto as any)).rejects.toMatchObject({ status: HttpStatus.BAD_REQUEST });
    });
  });

  describe('delete', () => {
    it('should delete student successfully', async () => {
      const mockResponse = { message: '学生删除成功' };

      jest.spyOn(service, 'delete').mockResolvedValue(mockResponse);

      const result = await controller.delete('S001');

      expect(result).toEqual(mockResponse);
      expect(service.delete).toHaveBeenCalledWith('S001');
    });

    it('should throw 404 error when student not found', async () => {
      jest.spyOn(service, 'delete').mockRejectedValue(new Error('学生不存在'));

      await expect(controller.delete('S999')).rejects.toThrow(HttpException);
      await expect(controller.delete('S999')).rejects.toThrow('学生不存在');
      await expect(controller.delete('S999')).rejects.toMatchObject({ status: HttpStatus.NOT_FOUND });
    });
  });
});