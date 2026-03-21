import 'dotenv/config';
import { PrismaClient } from '@prisma/client';
import { PrismaMssql } from '@prisma/adapter-mssql';

const databaseUrl = process.env.DATABASE_URL;
if (!databaseUrl) {
  throw new Error('DATABASE_URL is not set');
}
const adapter = new PrismaMssql(databaseUrl);
const prisma = new PrismaClient({ adapter });

async function checkSchoolSessions() {
  const schoolId = 'cmn02857n004koh9kopstwyy6';

  const school = await prisma.school.findUnique({ where: { id: schoolId } });
  console.log('School:', school);

  const sessions = await prisma.interactionSession.findMany({
    where: { schoolId },
    include: { scenario: true }
  });
  console.log(`\nSessions for school ${schoolId}:`, sessions.length);

  const nodes = await prisma.graphNode.findMany({
    where: { schoolId },
    take: 5
  });
  console.log(`\nNodes for school ${schoolId}:`, nodes.length);
  nodes.forEach(n => console.log(`  ${n.nodeType}: ${n.displayName}`));

  console.log('\n--- 所有有sessions的学校ID ---');
  const schoolsWithSessions = await prisma.interactionSession.findMany({
    select: { schoolId: true },
    distinct: ['schoolId']
  });
  schoolsWithSessions.forEach(s => console.log(`  ${s.schoolId}`));
}

checkSchoolSessions()
  .catch((e) => {
    console.error(e);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });