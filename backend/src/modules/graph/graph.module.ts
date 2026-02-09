import { Module } from '@nestjs/common';
import { GraphController } from './graph.controller';
import { GraphService } from './graph.service';
import { PrismaService } from '../../shared/utils/prisma.service';

@Module({
  controllers: [GraphController],
  providers: [GraphService, PrismaService],
  exports: [GraphService],
})
export class GraphModule {}