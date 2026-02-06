import { Injectable } from "@nestjs/common";
import { PrismaService } from "../../shared/utils/prisma.service";
import { CreateTeacherDto, UpdateTeacherDto } from "./teacher.dto";

@Injectable()
export class TeacherService {
  constructor(private prisma: PrismaService) {}

  async findAll(params: { school?: string }) {
    const { school } = params;

    const where = {
      ...(school && { school }),
    };

    return this.prisma.teacher.findMany({
      where,
      orderBy: { createdAt: "desc" },
    });
  }

  async findOne(id: string) {
    return this.prisma.teacher.findUnique({ where: { id } });
  }

  async create(data: CreateTeacherDto) {
    return this.prisma.teacher.create({
      data: {
        name: data.name,
        school: data.school,
        teachingGrade: data.teachingGrade,
        teachingClass: data.teachingClass,
      },
    });
  }

  async update(id: string, data: UpdateTeacherDto) {
    return this.prisma.teacher.update({
      where: { id },
      data,
    });
  }

  async delete(id: string) {
    await this.prisma.teacher.delete({ where: { id } });
    return { message: "教师删除成功" };
  }
}
