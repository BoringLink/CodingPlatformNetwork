import { Module } from '@nestjs/common';
import { InteractionController } from './interaction.controller';
import { InteractionService } from './interaction.service';

@Module({
  controllers: [InteractionController],
  providers: [InteractionService],
  exports: [InteractionService],
})
export class InteractionModule {}