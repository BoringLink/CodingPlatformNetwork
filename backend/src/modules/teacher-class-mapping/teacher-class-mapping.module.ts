import { Module } from '@nestjs/common';
import { TeacherClassMappingController } from './teacher-class-mapping.controller';
import { TeacherClassMappingService } from './teacher-class-mapping.service';
import { PrismaService } from '../../shared/utils/prisma.service';

@Module({
  controllers: [TeacherClassMappingController],
  providers: [TeacherClassMappingService, PrismaService],
  exports: [TeacherClassMappingService],
})
export class TeacherClassMappingModule {}
