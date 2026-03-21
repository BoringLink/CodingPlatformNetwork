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

interface KnowledgeData {
  id: number;
  content: string;
  knowledge_point: string;
  grade: string;
  type: string;
  parent_id: number | null;
  parent_name: string | null;
  related_knowledge_ids: number[];
  related_knowledge_names: string[];
}

async function loadKnowledge(filePath: string): Promise<KnowledgeData[]> {
  const content = fs.readFileSync(filePath, 'utf-8');
  return JSON.parse(content) as KnowledgeData[];
}

async function importKnowledge(jsonPath: string) {
  const knowledgeList = await loadKnowledge(jsonPath);
  console.log(`Loaded ${knowledgeList.length} knowledge items from ${jsonPath}`);

  const nodeIdMap = new Map<number, string>();
  const nameNodeMap = new Map<string, string>();

  for (const item of knowledgeList) {
    const displayName = item.knowledge_point || `知识点_${item.id}`;
    if (!displayName.trim()) continue;

    const existingNode = await prisma.graphNode.findFirst({
      where: {
        nodeType: 'KNOWLEDGE',
        displayName,
      },
    });

    if (existingNode) {
      console.log(`Knowledge node "${displayName}" already exists, skipping...`);
      nodeIdMap.set(item.id, existingNode.id);
      nameNodeMap.set(displayName, existingNode.id);
      continue;
    }

    let parentNodeId: string | null = null;
    if (item.parent_id && nameNodeMap.has(item.parent_name || '')) {
      parentNodeId = nameNodeMap.get(item.parent_name || '') || null;
    }

    const node = await prisma.graphNode.create({
      data: {
        nodeType: 'KNOWLEDGE',
        displayName,
      },
    });

    await prisma.knowledgeProfile.create({
      data: {
        nodeId: node.id,
        content: item.content || displayName,
        knowledgeType: item.type || 'GENERAL',
        category: item.grade ? `年级${item.grade}` : null,
        parentNodeId,
      },
    });

    nodeIdMap.set(item.id, node.id);
    nameNodeMap.set(displayName, node.id);
    console.log(`Created knowledge: ${displayName}`);
  }

  console.log('Knowledge import completed!');
}

const knowledgePath = path.join(process.cwd(), '../Real Data', '知识点.json');

importKnowledge(knowledgePath)
  .catch((e) => {
    console.error(e);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });