import 'dotenv/config';
import { PrismaClient } from '@prisma/client';
import { PrismaMssql } from '@prisma/adapter-mssql';

const databaseUrl = process.env.DATABASE_URL;
if (!databaseUrl) {
  throw new Error('DATABASE_URL is not set');
}
const adapter = new PrismaMssql(databaseUrl);
const prisma = new PrismaClient({ adapter });

async function checkDataConsistency() {
  console.log('=== 数据库数据一致性检查 ===\n');

  const schools = await prisma.school.findMany({ take: 5 });
  console.log('Schools (前5个):');
  schools.forEach(s => console.log(`  ID: ${s.id}, Name: ${s.name}`));

  const sessions = await prisma.interactionSession.findMany({ take: 5 });
  console.log('\nSessions (前5个):');
  sessions.forEach(s => console.log(`  ID: ${s.id}, schoolId: ${s.schoolId}, scenarioId: ${s.scenarioId}`));

  console.log('\n检查: session.schoolId 是否在 schools 中...');
  const sessionSchoolIds = new Set(sessions.map(s => s.schoolId));
  const schoolIds = new Set(schools.map(s => s.id));

  let matchCount = 0;
  for (const sid of sessionSchoolIds) {
    if (schoolIds.has(sid)) {
      matchCount++;
    } else {
      console.log(`  Session schoolId "${sid}" NOT in schools table!`);
    }
  }
  console.log(`  匹配: ${matchCount}/${sessionSchoolIds.size}`);

  console.log('\n检查: scenarioId 是否在 learningScenarios 中...');
  const scenarioIds = new Set(sessions.map(s => s.scenarioId));
  const scenarios = await prisma.learningScenario.findMany({ select: { id: true, code: true } });
  const validScenarioIds = new Set(scenarios.map(s => s.id));

  for (const sid of scenarioIds) {
    if (!validScenarioIds.has(sid)) {
      console.log(`  Session scenarioId "${sid}" NOT in learningScenarios!`);
    }
  }

  console.log('\n统计:');
  console.log(`  Schools: ${await prisma.school.count()}`);
  console.log(`  Grades: ${await prisma.grade.count()}`);
  console.log(`  Classes: ${await prisma.schoolClass.count()}`);
  console.log(`  Nodes: ${await prisma.graphNode.count()}`);
  console.log(`  Sessions: ${await prisma.interactionSession.count()}`);
  console.log(`  Interactions: ${await prisma.interaction.count()}`);

  const nodeTypes = await prisma.graphNode.groupBy({
    by: ['nodeType'],
    _count: { id: true },
  });
  console.log('\n节点类型分布:');
  nodeTypes.forEach(n => console.log(`  ${n.nodeType}: ${n._count.id}`));
}

checkDataConsistency()
  .catch((e) => {
    console.error(e);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });