import { Module } from "@nestjs/common";
import { ConfigModule } from "@nestjs/config";
import { StudentModule } from "./modules/student/student.module";
import { TeacherModule } from "./modules/teacher/teacher.module";
import { KnowledgeModule } from "./modules/knowledge/knowledge.module";
import { InteractionModule } from "./modules/interaction/interaction.module";
import { DataMigrationModule } from "./modules/data-migration/data-migration.module";
import { GraphModule } from "./modules/graph/graph.module";

@Module({
  imports: [
    ConfigModule.forRoot({
      isGlobal: true,
      envFilePath: "../.env.local",
    }),
    StudentModule,
    TeacherModule,
    KnowledgeModule,
    InteractionModule,
    DataMigrationModule,
    GraphModule,
  ],
  controllers: [],
  providers: [],
})
export class AppModule {}
