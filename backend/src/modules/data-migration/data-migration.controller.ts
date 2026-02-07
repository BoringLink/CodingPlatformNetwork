import { Controller, Post, Body, HttpException, HttpStatus } from '@nestjs/common';
import { DataMigrationService } from './data-migration.service';
import { ImportDataDto, importDataSchema } from './data-migration.dto';

@Controller('api/v1/data-migration')
export class DataMigrationController {
  constructor(private readonly dataMigrationService: DataMigrationService) {}

  @Post('import')
  async importData(@Body() body: ImportDataDto) {
    try {
      const validatedData = importDataSchema.parse(body);
      // 这里可以根据fileType和fileUrl执行相应的导入逻辑
      const result = await this.dataMigrationService.importData(validatedData);
      return result;
    } catch (error) {
      throw new HttpException(error.errors || '请求参数错误', HttpStatus.BAD_REQUEST);
    }
  }
}