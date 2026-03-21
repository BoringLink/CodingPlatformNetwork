import { Module } from "@nestjs/common";
import { NodeController } from "./node.controller";
import { NodeService } from "./node.service";

@Module({
  controllers: [NodeController],
  providers: [NodeService],
  exports: [NodeService],
})
export class NodeModule {}
