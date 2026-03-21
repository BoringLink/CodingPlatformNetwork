import * as fs from 'fs';
import * as path from 'path';
import 'dotenv/config';
import { PrismaClient } from '@prisma/client';
import { PrismaMssql } from '@prisma/adapter-mssql';

const databaseUrl = process.env.DATABASE_URL;
if (!databaseUrl) {
  throw new Error('DATABASE_URL is not set');
}
const adapter = new PrismaMssql(databaseUrl);
const prisma = new PrismaClient({ adapter });

interface TeacherData {
  name: string;
  teachingGrade: string;
  school: string;
  teachingClass: string;
}

async function loadTeachers(filePath: string): Promise<TeacherData[]> {
  const content = fs.readFileSync(filePath, 'utf-8');
  return JSON.parse(content) as TeacherData[];
}

async function findOrCreateSchool(schoolName: string): Promise<string> {
  let school = await prisma.school.findUnique({
    where: { name: schoolName },
  });

  if (!school) {
    school = await prisma.school.create({
      data: { name: schoolName },
    });
    console.log(`Created school: ${schoolName}`);
  }

  return school.id;
}

async function findOrCreateGrades(schoolId: string, gradeNames: string[]): Promise<string[]> {
  const gradeIds: string[] = [];

  for (const gradeName of gradeNames) {
    const normalizedGrade = gradeName.trim();
    if (!normalizedGrade) continue;

    let grade = await prisma.grade.findFirst({
      where: { schoolId, gradeName: normalizedGrade },
    });

    if (!grade) {
      grade = await prisma.grade.create({
        data: { schoolId, gradeName: normalizedGrade },
      });
      console.log(`Created grade: ${normalizedGrade} in school ${schoolId}`);
    }

    gradeIds.push(grade.id);
  }

  return gradeIds;
}

async function importTeachers(jsonPath: string) {
  const teachers = await loadTeachers(jsonPath);
  console.log(`Loaded ${teachers.length} teachers from ${jsonPath}`);

  const schoolCache = new Map<string, string>();
  const gradeCache = new Map<string, string[]>();

  for (const teacher of teachers) {
    let schoolId = schoolCache.get(teacher.school);
    if (!schoolId) {
      schoolId = await findOrCreateSchool(teacher.school);
      schoolCache.set(teacher.school, schoolId);
    }

    const gradeNames = teacher.teachingGrade.split(',').map(g => `${g}年级`);
    let gradeIds = gradeCache.get(teacher.school);
    if (!gradeIds) {
      gradeIds = await findOrCreateGrades(schoolId, gradeNames);
      gradeCache.set(teacher.school, gradeIds);
    }

    const displayName = teacher.name.trim() || 'Unknown Teacher';
    const existingNode = await prisma.graphNode.findFirst({
      where: {
        nodeType: 'TEACHER',
        displayName,
        schoolId,
      },
    });

    if (existingNode) {
      console.log(`Teacher node "${displayName}" already exists, skipping...`);
      continue;
    }

    const node = await prisma.graphNode.create({
      data: {
        nodeType: 'TEACHER',
        displayName,
        schoolId,
        gradeId: gradeIds[0] || null,
      },
    });

    await prisma.teacherProfile.create({
      data: {
        nodeId: node.id,
        teachingGrade: teacher.teachingGrade,
        teachingClass: teacher.teachingClass || null,
        subject: '信息技术',
      },
    });

    console.log(`Created teacher: ${displayName} in ${teacher.school}`);
  }

  console.log('Teacher import completed!');
}

const teachersPath = path.join(process.cwd(), '../Real Data', '教师列表_filtered.json');

importTeachers(teachersPath)
  .catch((e) => {
    console.error(e);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });