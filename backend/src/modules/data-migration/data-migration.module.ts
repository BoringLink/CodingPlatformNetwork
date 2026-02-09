import { Module } from '@nestjs/common';
import { DataMigrationController } from './data-migration.controller';
import { DataMigrationService } from './data-migration.service';
import { PrismaService } from '../../shared/utils/prisma.service';

@Module({
  controllers: [DataMigrationController],
  providers: [DataMigrationService, PrismaService],
  exports: [DataMigrationService],
})
export class DataMigrationModule {}