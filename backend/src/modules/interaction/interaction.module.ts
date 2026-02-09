import { Module } from '@nestjs/common';
import { InteractionController } from './interaction.controller';
import { InteractionService } from './interaction.service';
import { PrismaService } from '../../shared/utils/prisma.service';

@Module({
  controllers: [InteractionController],
  providers: [InteractionService, PrismaService],
  exports: [InteractionService],
})
export class InteractionModule {}