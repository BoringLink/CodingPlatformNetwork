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

interface ScenarioConfig {
  code: string;
  name: string;
  sortOrder: number;
}

async function loadScenarios(): Promise<ScenarioConfig[]> {
  const configPath = path.join(__dirname, '../config/learning-scenarios.json');
  const content = fs.readFileSync(configPath, 'utf-8');
  return JSON.parse(content) as ScenarioConfig[];
}

async function seedScenarios() {
  const scenarios = await loadScenarios();

  console.log(`Loaded ${scenarios.length} scenarios from config`);

  for (const scenario of scenarios) {
    const existing = await prisma.learningScenario.findUnique({
      where: { code: scenario.code },
    });

    if (existing) {
      console.log(`Scenario "${scenario.code}" already exists, skipping...`);
      continue;
    }

    await prisma.learningScenario.create({
      data: {
        code: scenario.code,
        nameZh: scenario.name,
        sortOrder: scenario.sortOrder,
        isActive: true,
      },
    });

    console.log(`Created scenario: ${scenario.code} - ${scenario.name}`);
  }

  console.log('Seeding completed!');
}

seedScenarios()
  .catch((e) => {
    console.error(e);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });