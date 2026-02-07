import { Module } from "@nestjs/common";
import { ConfigModule } from "@nestjs/config";
import { StudentModule } from "./modules/student/student.module";
import { TeacherModule } from "./modules/teacher/teacher.module";
import { KnowledgeModule } from "./modules/knowledge/knowledge.module";
import { InteractionModule } from "./modules/interaction/interaction.module";
import { DataMigrationModule } from "./modules/data-migration/data-migration.module";
import { GraphModule } from "./modules/graph/graph.module";
import { TeacherClassMappingModule } from "./modules/teacher-class-mapping/teacher-class-mapping.module";
import { PrismaService } from "./shared/utils/prisma.service";

@Module({
  imports: [
    ConfigModule.forRoot({
      isGlobal: true,
      envFilePath: "../.env",
    }),
    StudentModule,
    TeacherModule,
    KnowledgeModule,
    InteractionModule,
    DataMigrationModule,
    GraphModule,
    TeacherClassMappingModule,
  ],
  controllers: [],
  providers: [PrismaService],
  exports: [PrismaService],
})
export class AppModule {}
