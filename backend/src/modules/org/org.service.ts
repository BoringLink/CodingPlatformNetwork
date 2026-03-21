import { Injectable } from "@nestjs/common";
import { PrismaService } from "../../shared/utils/prisma.service";

@Injectable()
export class OrgService {
  constructor(private readonly prisma: PrismaService) {}

  async getSchools() {
    const schools = await this.prisma.school.findMany({
      select: { id: true, name: true },
      orderBy: { name: "asc" },
    });

    return {
      data: schools,
      meta: null,
      error: null,
    };
  }

  async getGrades(schoolId: string) {
    const grades = await this.prisma.grade.findMany({
      where: {
        schoolId,
      },
      select: {
        id: true,
        gradeName: true,
      },
      orderBy: { gradeName: "asc" },
    });

    return {
      data: grades,
      meta: null,
      error: null,
    };
  }

  async getClasses(gradeId: string) {
    const classes = await this.prisma.schoolClass.findMany({
      where: {
        gradeId,
      },
      select: {
        id: true,
        className: true,
      },
      orderBy: { className: "asc" },
    });

    return {
      data: classes,
      meta: null,
      error: null,
    };
  }
}
