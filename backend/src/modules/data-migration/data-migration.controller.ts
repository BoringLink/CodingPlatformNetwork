import { Controller, Post, Get, HttpException, HttpStatus } from '@nestjs/common';
import { DataMigrationService } from './data-migration.service';

@Controller('api/v1/data-migration')
export class DataMigrationController {
  constructor(private readonly dataMigrationService: DataMigrationService) {}

  @Post('migrate')
  async migrateData() {
    try {
      return await this.dataMigrationService.executeFullMigration();
    } catch (error) {
      throw new HttpException(error.message || '数据迁移失败', HttpStatus.INTERNAL_SERVER_ERROR);
    }
  }

  @Get('verify')
  async verifyMigration() {
    try {
      return await this.dataMigrationService.verifyMigration();
    } catch (error) {
      throw new HttpException(error.message || '验证迁移结果失败', HttpStatus.INTERNAL_SERVER_ERROR);
    }
  }
}