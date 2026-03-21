import { Module } from "@nestjs/common";
import { InteractionSessionController } from "./interaction-session.controller";
import { InteractionSessionService } from "./interaction-session.service";

@Module({
  controllers: [InteractionSessionController],
  providers: [InteractionSessionService],
  exports: [InteractionSessionService],
})
export class InteractionSessionModule {}
