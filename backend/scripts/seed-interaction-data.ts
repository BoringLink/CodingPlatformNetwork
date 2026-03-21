import 'dotenv/config';
import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();

async function main() {
  // 1. 查找一个有效的 scenario、school、grade、class、student 节点
  const scenario = await prisma.learningScenario.findFirst();
  const school = await prisma.school.findFirst();
    const grade = await prisma.grade.findFirst({ where: { schoolId: school?.id } });
    const schoolClass = await prisma.schoolClass.findFirst({ where: { gradeId: grade?.id } });

  // 2. 查找两个学生节点（用于交互）
    const students = await prisma.graphNode.findMany({
      where: {
        nodeType: 'STUDENT',
        schoolId: school?.id,
        gradeId: grade?.id,
        classId: schoolClass?.id,
      },
      take: 2,
    });

  if (!scenario || !school || !grade || !schoolClass || students.length < 2) {
    console.error('缺少基础数据，无法补交互会话和交互。');
    return;
  }

  // 3. 创建一个 interaction session
    const session = await prisma.interactionSession.create({
      data: {
        scenarioId: scenario.id,
        schoolId: school.id,
        gradeId: grade.id,
        classId: schoolClass.id,
        sessionName: '示例会话',
        occurredAt: new Date(),
      },
    });

  // 4. 创建一条交互
  await prisma.interaction.create({
    data: {
      sessionId: session.id,
      sourceNodeId: students[0].id,
      targetNodeId: students[1].id,
      interactionType: 'DISCUSS',
      strength: 1.0,
    },
  });

  console.log('已补齐一条交互会话和交互。');
}

main()
  .catch((e) => {
    console.error(e);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });
