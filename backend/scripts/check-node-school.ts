import 'dotenv/config';
import { PrismaClient } from '@prisma/client';
import { PrismaMssql } from '@prisma/adapter-mssql';

const databaseUrl = process.env.DATABASE_URL;
if (!databaseUrl) {
  throw new Error('DATABASE_URL is not set');
}
const adapter = new PrismaMssql(databaseUrl);
const prisma = new PrismaClient({ adapter });

async function checkNodeSchoolRelation() {
  console.log('=== 节点与学校关联检查 ===\n');

  const sessions = await prisma.interactionSession.findMany({
    include: { scenario: true }
  });

  for (const session of sessions) {
    console.log(`Session: ${session.id}`);
    console.log(`  场景: ${session.scenario.code} (${session.scenario.nameZh})`);
    console.log(`  学校: ${session.schoolId}`);
    console.log(`  年级: ${session.gradeId}`);
    console.log(`  班级: ${session.classId}`);

    const interactions = await prisma.interaction.findMany({
      where: { sessionId: session.id },
      include: {
        sourceNode: { select: { id: true, nodeType: true, displayName: true, schoolId: true } },
        targetNode: { select: { id: true, nodeType: true, displayName: true, schoolId: true } }
      }
    });

    console.log(`  交互数: ${interactions.length}`);
    interactions.slice(0, 3).forEach(i => {
      console.log(`    ${i.sourceNode.nodeType} "${i.sourceNode.displayName}" -> ${i.targetNode.nodeType} "${i.targetNode.displayName}"`);
    });

    const schoolNodes = await prisma.graphNode.findMany({
      where: { schoolId: session.schoolId },
      select: { id: true, nodeType: true, displayName: true }
    });
    console.log(`  学校 ${session.schoolId} 下的节点: ${schoolNodes.length}`);
    schoolNodes.slice(0, 3).forEach(n => console.log(`    ${n.nodeType}: ${n.displayName}`));

    console.log();
  }
}

checkNodeSchoolRelation()
  .catch((e) => {
    console.error(e);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });