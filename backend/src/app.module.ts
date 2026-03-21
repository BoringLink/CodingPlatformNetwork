import { Module } from "@nestjs/common";
import { ConfigModule } from "@nestjs/config";
import { StudentModule } from "./modules/student/student.module";
import { GraphModule } from "./modules/graph/graph.module";
import { ScenarioModule } from "./modules/scenario/scenario.module";
import { OrgModule } from "./modules/org/org.module";
import { NodeModule } from "./modules/node/node.module";
import { InteractionSessionModule } from "./modules/interaction-session/interaction-session.module";
import { InteractionModule } from "./modules/interaction/interaction.module";
import { PrismaModule } from "./shared/utils/prisma.module";

@Module({
  imports: [
    ConfigModule.forRoot({
      isGlobal: true,
      envFilePath: ".env",
    }),
    PrismaModule,
    ScenarioModule,
    OrgModule,
    StudentModule,
    NodeModule,
    InteractionSessionModule,
    InteractionModule,
    GraphModule,
  ],
  controllers: [],
  providers: [],
  exports: [],
})
export class AppModule {}
