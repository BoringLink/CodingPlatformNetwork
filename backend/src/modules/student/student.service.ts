import { Injectable } from "@nestjs/common";
import { PrismaService } from "../../shared/utils/prisma.service";
import { CreateStudentDto, UpdateStudentDto } from "./student.dto";

@Injectable()
export class StudentService {
  constructor(private prisma: PrismaService) {}

  async findAll(params: { school?: string; grade?: string; classId?: string }) {
    const { school, grade, classId } = params;

    const where = {
      ...(school && { school }),
      ...(grade && { grade }),
      ...(classId && { classId }),
    };

    return this.prisma.student.findMany({
      where,
      orderBy: { createdAt: "desc" },
    });
  }

  async findOne(id: string) {
    return this.prisma.student.findUnique({ where: { id } });
  }

  async create(data: CreateStudentDto) {
    return this.prisma.student.create({
      data: {
        name: data.name,
        school: data.school,
        grade: data.grade,
        classId: data.classId,
        knowledgeReserve: data.knowledgeReserve,
        learningEngagement: data.learningEngagement,
        cognitiveLoad: data.cognitiveLoad,
        learningMotivation: data.learningMotivation,
        computationalThinking: data.computationalThinking,
        humanAiTrust: data.humanAiTrust,
        learningMethod: data.learningMethod,
        learningAttitude: data.learningAttitude,
      },
    });
  }

  async update(id: string, data: UpdateStudentDto) {
    return this.prisma.student.update({
      where: { id },
      data,
    });
  }

  async delete(id: string) {
    await this.prisma.student.delete({ where: { id } });
    return { message: "学生删除成功" };
  }

  // 获取所有可用的学校列表
  async getSchools() {
    const students = await this.prisma.student.findMany({
      distinct: ['school'],
      select: { school: true },
      where: { school: { not: '' } },
    });
    return students.map(student => student.school).filter(Boolean);
  }

  // 根据学校获取年级列表
  async getGradesBySchool(school: string) {
    const students = await this.prisma.student.findMany({
      distinct: ['grade'],
      select: { grade: true },
      where: { school, grade: { not: '' } },
    });
    return students.map(student => student.grade).filter(Boolean);
  }

  // 根据学校和年级获取班级列表
  async getClassesBySchoolAndGrade(school: string, grade: string) {
    const students = await this.prisma.student.findMany({
      distinct: ['classId'],
      select: { classId: true },
      where: { school, grade, classId: { not: '' } },
    });
    return students.map(student => student.classId).filter(Boolean);
  }
}
