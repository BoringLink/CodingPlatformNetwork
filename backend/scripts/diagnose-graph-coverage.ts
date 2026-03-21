import "dotenv/config";
import { PrismaService } from "../src/shared/utils/prisma.service";

type CliFilters = {
  scenarioCode?: string;
  schoolId?: string;
  gradeId?: string;
  classId?: string;
};

type ComboRow = {
  scenarioId: string;
  schoolId: string | null;
  gradeId: string | null;
  classId: string | null;
  sessionCount: number;
  interactionCount: number;
};

function parseArgs(): CliFilters {
  const args = process.argv.slice(2);
  const filters: CliFilters = {};

  for (let i = 0; i < args.length; i += 1) {
    const token = args[i];
    const next = args[i + 1];

    if (token === "--scenario_code" && next) {
      filters.scenarioCode = next;
      i += 1;
      continue;
    }
    if (token === "--school_id" && next) {
      filters.schoolId = next;
      i += 1;
      continue;
    }
    if (token === "--grade_id" && next) {
      filters.gradeId = next;
      i += 1;
      continue;
    }
    if (token === "--class_id" && next) {
      filters.classId = next;
      i += 1;
      continue;
    }
  }

  return filters;
}

function printUsage() {
  console.log("Usage:");
  console.log("  pnpm ts-node scripts/diagnose-graph-coverage.ts");
  console.log(
    "  pnpm ts-node scripts/diagnose-graph-coverage.ts --scenario_code ONLINE_COURSE --school_id <id> --grade_id <id> --class_id <id>",
  );
}

async function printOverview(prisma: PrismaService): Promise<void> {
  const [scenarioCount, schoolCount, gradeCount, classCount, nodeCount, sessionCount, interactionCount] =
    await Promise.all([
      prisma.learningScenario.count(),
      prisma.school.count(),
      prisma.grade.count(),
      prisma.schoolClass.count(),
      prisma.graphNode.count(),
      prisma.interactionSession.count(),
      prisma.interaction.count(),
    ]);

  const sessionsWithInteractions = await prisma.$queryRawUnsafe<
    Array<{ value: number }>
  >(
    "SELECT COUNT(DISTINCT sessionId) AS value FROM interactions",
  );

  const nodeTypeBreakdown = await prisma.graphNode.groupBy({
    by: ["nodeType"],
    _count: { _all: true },
  });

  const topCombos = await prisma.$queryRawUnsafe<ComboRow[]>(`
    SELECT TOP 10
      s.scenarioId,
      s.schoolId,
      s.gradeId,
      s.classId,
      COUNT(DISTINCT s.id) AS sessionCount,
      COUNT(i.id) AS interactionCount
    FROM interaction_sessions s
    LEFT JOIN interactions i ON i.sessionId = s.id
    GROUP BY s.scenarioId, s.schoolId, s.gradeId, s.classId
    ORDER BY COUNT(i.id) DESC, COUNT(DISTINCT s.id) DESC
  `);

  const scenarioIds = [...new Set(topCombos.map((row) => row.scenarioId))];
  const scenarioMap = new Map<string, string>();
  if (scenarioIds.length > 0) {
    const scenarios = await prisma.learningScenario.findMany({
      where: { id: { in: scenarioIds } },
      select: { id: true, code: true },
    });
    scenarios.forEach((item) => scenarioMap.set(item.id, item.code));
  }

  console.log("\n=== Graph Data Coverage Overview ===");
  console.log(`scenarios: ${scenarioCount}`);
  console.log(`schools: ${schoolCount}, grades: ${gradeCount}, classes: ${classCount}`);
  console.log(`nodes: ${nodeCount}, sessions: ${sessionCount}, interactions: ${interactionCount}`);
  console.log(`sessions with interactions: ${sessionsWithInteractions[0]?.value ?? 0}`);

  console.log("\nNode type breakdown:");
  nodeTypeBreakdown.forEach((item) => {
    console.log(`- ${item.nodeType}: ${item._count._all}`);
  });

  console.log("\nTop scenario/org combinations by interaction volume:");
  if (topCombos.length === 0) {
    console.log("- no session data");
  } else {
    topCombos.forEach((row, idx) => {
      const scenarioCode = scenarioMap.get(row.scenarioId) ?? row.scenarioId;
      console.log(
        `${idx + 1}. scenario=${scenarioCode}, school_id=${row.schoolId}, grade_id=${row.gradeId}, class_id=${row.classId}, sessions=${row.sessionCount}, interactions=${row.interactionCount}`,
      );
    });
  }
}

async function diagnoseFilters(prisma: PrismaService, filters: CliFilters): Promise<void> {
  let scenarioId: string | undefined;

  if (filters.scenarioCode) {
    const scenario = await prisma.learningScenario.findUnique({
      where: { code: filters.scenarioCode },
      select: { id: true },
    });

    if (!scenario) {
      console.log(`\nDiagnosis result: scenario_code not found -> ${filters.scenarioCode}`);
      return;
    }

    scenarioId = scenario.id;
  }

  const where = {
    ...(scenarioId ? { scenarioId } : {}),
    ...(filters.schoolId ? { schoolId: filters.schoolId } : {}),
    ...(filters.gradeId ? { gradeId: filters.gradeId } : {}),
    ...(filters.classId ? { classId: filters.classId } : {}),
  };

  const sessions = await prisma.interactionSession.findMany({
    where,
    select: { id: true },
  });

  console.log("\n=== Filtered Diagnosis ===");
  console.log(`filters: ${JSON.stringify(filters)}`);
  console.log(`matched sessions: ${sessions.length}`);

  if (sessions.length === 0) {
    console.log("reason: no interaction_sessions match this filter set");
    return;
  }

  const sessionIds = sessions.map((item) => item.id);

  const interactions = await prisma.interaction.findMany({
    where: { sessionId: { in: sessionIds } },
    select: { id: true, sourceNodeId: true, targetNodeId: true, sessionId: true },
  });

  console.log(`matched interactions: ${interactions.length}`);

  if (interactions.length === 0) {
    console.log("reason: sessions exist but no interactions under these sessions");
    return;
  }

  const nodeIds = new Set<string>();
  interactions.forEach((item) => {
    nodeIds.add(item.sourceNodeId);
    nodeIds.add(item.targetNodeId);
  });

  const nodes = await prisma.graphNode.findMany({
    where: { id: { in: Array.from(nodeIds) } },
    select: { id: true, nodeType: true },
  });

  const nodeTypeCount = new Map<string, number>();
  nodes.forEach((n) => {
    nodeTypeCount.set(n.nodeType, (nodeTypeCount.get(n.nodeType) ?? 0) + 1);
  });

  const missingNodeCount = nodeIds.size - nodes.length;

  console.log(`distinct nodes referenced: ${nodeIds.size}`);
  console.log(`distinct nodes resolved: ${nodes.length}`);
  console.log(`missing nodes (should be 0): ${missingNodeCount}`);
  console.log("node type distribution:");
  ["STUDENT", "TEACHER", "KNOWLEDGE"].forEach((type) => {
    console.log(`- ${type}: ${nodeTypeCount.get(type) ?? 0}`);
  });

  if ((nodeTypeCount.get("KNOWLEDGE") ?? 0) === 0) {
    console.log("warning: no KNOWLEDGE nodes in this slice; resource generation may fail");
  }

  const sampleSession = sessions[0];
  console.log(`sample session id: ${sampleSession.id}`);
  console.log("diagnosis: filtered graph should be non-empty if API uses same filters");
}

async function main() {
  const filters = parseArgs();
  const prisma = new PrismaService();
  await prisma.$connect();

  try {
    await printOverview(prisma);

    if (
      filters.scenarioCode ||
      filters.schoolId ||
      filters.gradeId ||
      filters.classId
    ) {
      await diagnoseFilters(prisma, filters);
    } else {
      console.log("\nNo filter args provided; overview completed.");
      printUsage();
    }
  } finally {
    await prisma.$disconnect();
  }
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
