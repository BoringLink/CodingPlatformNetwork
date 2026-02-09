import { Module } from '@nestjs/common';
import { KnowledgeController } from './knowledge.controller';
import { KnowledgeService } from './knowledge.service';
import { PrismaService } from '../../shared/utils/prisma.service';

@Module({
  controllers: [KnowledgeController],
  providers: [KnowledgeService, PrismaService],
  exports: [KnowledgeService],
})
export class KnowledgeModule {}