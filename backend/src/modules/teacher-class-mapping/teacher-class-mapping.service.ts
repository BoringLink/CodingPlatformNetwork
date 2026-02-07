import { Injectable } from "@nestjs/common";
import { PrismaService } from "../../shared/utils/prisma.service";
import { CreateTeacherClassMappingDto } from "./teacher-class-mapping.dto";

@Injectable()
export class TeacherClassMappingService {
  constructor(private readonly prisma: PrismaService) {}

  async findAll(params: {
    teacherId?: string;
    grade?: string;
    classId?: string;
  }) {
    const { teacherId, grade, classId } = params;

    const where = {
      ...(teacherId && { teacherId }),
      ...(grade && { grade }),
      ...(classId && { classId }),
    };

    return this.prisma.teacherClassMapping.findMany({
      where,
      orderBy: { createdAt: "desc" },
    });
  }

  async create(data: CreateTeacherClassMappingDto) {
    return this.prisma.teacherClassMapping.create({
      data: {
        teacherId: data.teacherId,
        grade: data.grade,
        classId: data.classId,
      },
    });
  }

  async delete(id: string) {
    await this.prisma.teacherClassMapping.delete({ where: { id } });
    return { message: "教师-班级关联删除成功" };
  }
}
