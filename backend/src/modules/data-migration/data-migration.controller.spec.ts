import { Test, TestingModule } from '@nestjs/testing';
import { DataMigrationController } from './data-migration.controller';
import { DataMigrationService } from './data-migration.service';
import { HttpException, HttpStatus } from '@nestjs/common';
import { ImportDataDto } from './data-migration.dto';

describe('DataMigrationController', () => {
  let controller: DataMigrationController;
  let service: DataMigrationService;

  beforeEach(async () => {
    const module: TestingModule = await Test.createTestingModule({
      controllers: [DataMigrationController],
      providers: [
        {
          provide: DataMigrationService,
          useValue: {
            importData: jest.fn(),
          },
        },
      ],
    }).compile();

    controller = module.get<DataMigrationController>(DataMigrationController);
    service = module.get<DataMigrationService>(DataMigrationService);
  });

  describe('importData', () => {
    it('should import data with valid survey type', async () => {
      const importDto: ImportDataDto = {
        fileType: 'survey',
        fileUrl: 'https://example.com/survey.xls',
      };

      const mockResponse = {
        message: '数据导入成功',
        importedCount: 100,
        updatedCount: 20,
        errors: [],
      };

      jest.spyOn(service, 'importData').mockResolvedValue(mockResponse);

      const result = await controller.importData(importDto);

      expect(result).toEqual(mockResponse);
      expect(service.importData).toHaveBeenCalledWith(importDto);
    });

    it('should throw 400 error with invalid fileType', async () => {
      const invalidDto = {
        fileType: 'invalid', // 无效的fileType
        fileUrl: 'https://example.com/survey.xls',
      };

      await expect(controller.importData(invalidDto as any)).rejects.toThrow(HttpException);
      await expect(controller.importData(invalidDto as any)).rejects.toMatchObject({ status: HttpStatus.BAD_REQUEST });
    });

    it('should throw 400 error with missing fileUrl', async () => {
      const invalidDto = {
        fileType: 'survey',
        // 缺少 fileUrl
      };

      await expect(controller.importData(invalidDto as any)).rejects.toThrow(HttpException);
      await expect(controller.importData(invalidDto as any)).rejects.toMatchObject({ status: HttpStatus.BAD_REQUEST });
    });

    it('should throw 400 error with empty fileUrl', async () => {
      const invalidDto = {
        fileType: 'survey',
        fileUrl: '', // 空fileUrl
      };

      await expect(controller.importData(invalidDto as any)).rejects.toThrow(HttpException);
      await expect(controller.importData(invalidDto as any)).rejects.toMatchObject({ status: HttpStatus.BAD_REQUEST });
    });

    it('should handle import with errors', async () => {
      const importDto: ImportDataDto = {
        fileType: 'survey',
        fileUrl: 'https://example.com/survey.xls',
      };

      const mockResponse = {
        message: '数据导入成功',
        importedCount: 80,
        updatedCount: 10,
        errors: [
          '第5行：姓名不能为空',
          '第10行：成绩格式错误',
        ],
      };

      jest.spyOn(service, 'importData').mockResolvedValue(mockResponse);

      const result = await controller.importData(importDto);

      expect(result).toEqual(mockResponse);
      expect(result.errors).toHaveLength(2);
      expect(service.importData).toHaveBeenCalledWith(importDto);
    });

    it('should handle zero imported records', async () => {
      const importDto: ImportDataDto = {
        fileType: 'survey',
        fileUrl: 'https://example.com/empty.xls',
      };

      const mockResponse = {
        message: '数据导入成功',
        importedCount: 0,
        updatedCount: 0,
        errors: [],
      };

      jest.spyOn(service, 'importData').mockResolvedValue(mockResponse);

      const result = await controller.importData(importDto);

      expect(result).toEqual(mockResponse);
      expect(result.importedCount).toBe(0);
      expect(result.updatedCount).toBe(0);
      expect(service.importData).toHaveBeenCalledWith(importDto);
    });
  });
});