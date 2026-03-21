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

interface CognitiveDimensionConfig {
  code: string;
  name: string;
  category: string;
  minScore: number;
  maxScore: number;
  sortOrder: number;
  description: string;
}

async function loadDimensions(): Promise<CognitiveDimensionConfig[]> {
  const configPath = path.join(__dirname, '../config/cognitive-dimensions.json');
  const content = fs.readFileSync(configPath, 'utf-8');
  return JSON.parse(content) as CognitiveDimensionConfig[];
}

async function seedCognitiveDimensions() {
  const dimensions = await loadDimensions();

  console.log(`Loaded ${dimensions.length} cognitive dimensions from config`);

  for (const dim of dimensions) {
    const existing = await prisma.cognitiveDimensionDef.findUnique({
      where: { dimensionCode: dim.code },
    });

    if (existing) {
      console.log(`Dimension "${dim.code}" already exists, skipping...`);
      continue;
    }

    await prisma.cognitiveDimensionDef.create({
      data: {
        dimensionCode: dim.code,
        dimensionNameZh: dim.name,
        categoryName: dim.category,
        minScore: dim.minScore,
        maxScore: dim.maxScore,
        sortOrder: dim.sortOrder,
        isActive: true,
      },
    });

    console.log(`Created dimension: ${dim.code} - ${dim.name}`);
  }

  console.log('Cognitive dimensions seeding completed!');
}

seedCognitiveDimensions()
  .catch((e) => {
    console.error(e);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });