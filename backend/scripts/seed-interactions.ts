import 'dotenv/config';
import { PrismaClient } from '@prisma/client';
import { PrismaMssql } from '@prisma/adapter-mssql';
import { faker } from '@faker-js/faker';

const databaseUrl = process.env.DATABASE_URL;
if (!databaseUrl) {
  throw new Error('DATABASE_URL is not set');
}
const adapter = new PrismaMssql(databaseUrl);
const prisma = new PrismaClient({ adapter });

const INTERACTION_TYPES = ['DISCUSS', 'COLLABORATE', 'ASK', 'ANSWER', 'EVALUATE', 'SHARE'];
const ACTION_TYPES = ['TEXT', 'VOICE', 'VIDEO', 'IMAGE', 'FILE'];
const SCENARIO_NAMES = ['AI答疑小组', '协作编程', '知识点讨论', '项目实践', '同伴互评'];

interface NodePair {
  sourceId: string;
  targetId: string;
  sourceType: string;
  targetType: string;
}

async function getRandomNodes(count: number, nodeType?: string): Promise<string[]> {
  const nodes = await prisma.graphNode.findMany({
    where: nodeType ? { nodeType } : undefined,
    select: { id: true },
    take: count * 3,
  });
  return faker.helpers.arrayElements(nodes.map(n => n.id), count);
}

async function createNodePairs(students: string[], teachers: string[], knowledge: string[]): Promise<NodePair[]> {
  const pairs: NodePair[] = [];

  for (let i = 0; i < students.length - 1; i++) {
    if (faker.datatype.boolean()) {
      pairs.push({
        sourceId: students[i],
        targetId: students[i + 1],
        sourceType: 'STUDENT',
        targetType: 'STUDENT',
      });
    }
  }

  if (teachers.length > 0 && students.length > 0) {
    const randomStudent = faker.helpers.arrayElement(students);
    const randomTeacher = faker.helpers.arrayElement(teachers);
    pairs.push({
      sourceId: randomStudent,
      targetId: randomTeacher,
      sourceType: 'STUDENT',
      targetType: 'TEACHER',
    });
  }

  if (knowledge.length > 0 && students.length > 0) {
    const randomStudent = faker.helpers.arrayElement(students);
    const randomKnowledge = faker.helpers.arrayElement(knowledge);
    pairs.push({
      sourceId: randomStudent,
      targetId: randomKnowledge,
      sourceType: 'STUDENT',
      targetType: 'KNOWLEDGE',
    });
  }

  return pairs;
}

async function seedInteractions() {
  const scenarios = await prisma.learningScenario.findMany({ where: { isActive: true } });
  if (scenarios.length === 0) {
    console.error('No active scenarios found. Please run seed-scenarios.ts first.');
    return;
  }

  const schools = await prisma.school.findMany({ take: 10 });
  if (schools.length === 0) {
    console.error('No schools found.');
    return;
  }

  console.log(`Found ${scenarios.length} scenarios, ${schools.length} schools`);

  const students = await getRandomNodes(100, 'STUDENT');
  const teachers = await getRandomNodes(20, 'TEACHER');
  const knowledge = await getRandomNodes(30, 'KNOWLEDGE');

  console.log(`Nodes - Students: ${students.length}, Teachers: ${teachers.length}, Knowledge: ${knowledge.length}`);

  let sessionCount = 0;
  let interactionCount = 0;

  for (const school of schools) {
    const grades = await prisma.grade.findMany({ where: { schoolId: school.id }, take: 3 });
    if (grades.length === 0) continue;

    for (const grade of grades) {
      const classes = await prisma.schoolClass.findMany({ where: { gradeId: grade.id }, take: 2 });
      const schoolStudents = students.slice(0, faker.number.int({ min: 5, max: 15 }));

      for (const schoolClass of classes) {
        const scenario = faker.helpers.arrayElement(scenarios);
        const sessionName = faker.helpers.arrayElement(SCENARIO_NAMES);

        const occurredAt = faker.date.recent({ days: 30 });

        const session = await prisma.interactionSession.create({
          data: {
            scenarioId: scenario.id,
            schoolId: school.id,
            gradeId: grade.id,
            classId: schoolClass.id,
            sessionName: `${sessionName}_${faker.string.alphanumeric(4)}`,
            occurredAt,
          },
        });
        sessionCount++;

        const pairs = await createNodePairs(schoolStudents, teachers, knowledge);

        for (const pair of pairs) {
          const interactionType = faker.helpers.arrayElement(INTERACTION_TYPES);
          const actionType = faker.helpers.arrayElement(ACTION_TYPES);
          const strength = faker.number.float({ min: 0.1, max: 1.0, fractionDigits: 4 });

          try {
            await prisma.interaction.create({
              data: {
                sessionId: session.id,
                sourceNodeId: pair.sourceId,
                targetNodeId: pair.targetId,
                interactionType,
                actionType,
                durationSec: faker.number.int({ min: 30, max: 3600 }),
                strength,
              },
            });
            interactionCount++;
          } catch (error) {
            // Skip duplicates due to unique constraint
          }
        }

        if (sessionCount % 10 === 0) {
          console.log(`Created ${sessionCount} sessions, ${interactionCount} interactions...`);
        }
      }
    }
  }

  console.log(`\nSeeding completed!`);
  console.log(`Total sessions created: ${sessionCount}`);
  console.log(`Total interactions created: ${interactionCount}`);
}

seedInteractions()
  .catch((e) => {
    console.error(e);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });