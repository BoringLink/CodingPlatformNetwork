import { BadRequestException, Injectable } from "@nestjs/common";
import { Prisma } from "@prisma/client";
import { PrismaService } from "../../shared/utils/prisma.service";
import {
  BatchCreateInteractionsDto,
  QueryInteractionsDto,
} from "./interaction.dto";

/**
 * 交互服务
 * 支持按场景隔离的交互管理和验证
 */

@Injectable()
export class InteractionService {
  private readonly recentIdempotency = new Map<string, number>();

  constructor(private prisma: PrismaService) {}

  async findAll(params: QueryInteractionsDto) {
    const {
      scenarioCode,
      sessionId,
      sourceNodeId,
      targetNodeId,
      page,
      pageSize,
    } = params;

    let sessionFilter: Prisma.InteractionWhereInput["session"] = undefined;
    if (scenarioCode) {
      const scenario = await this.prisma.learningScenario.findUnique({
        where: { code: scenarioCode },
        select: { id: true },
      });

      if (!scenario) {
        throw new BadRequestException("SCENARIO_CODE_INVALID");
      }

      sessionFilter = {
        scenarioId: scenario.id,
      };
    }

    const where: Prisma.InteractionWhereInput = {
      ...(sessionId ? { sessionId } : {}),
      ...(sourceNodeId ? { sourceNodeId } : {}),
      ...(targetNodeId ? { targetNodeId } : {}),
      ...(sessionFilter ? { session: sessionFilter } : {}),
    };

    const [interactions, total] = await this.prisma.$transaction([
      this.prisma.interaction.findMany({
        where,
        include: {
          session: {
            include: {
              scenario: {
                select: {
                  code: true,
                  nameZh: true,
                },
              },
            },
          },
        },
        orderBy: { createdAt: "desc" },
        skip: (page - 1) * pageSize,
        take: pageSize,
      }),
      this.prisma.interaction.count({ where }),
    ]);

    return {
      data: interactions,
      meta: {
        page,
        pageSize,
        total,
      },
      error: null,
    };
  }

  async batchCreate(data: BatchCreateInteractionsDto, idempotencyKey?: string) {
    if (!idempotencyKey) {
      throw new BadRequestException(
        "VALIDATION_ERROR: Idempotency-Key required",
      );
    }

    const now = Date.now();
    const duplicateWindowMs = 60 * 1000;
    const previous = this.recentIdempotency.get(idempotencyKey);
    if (previous && now - previous < duplicateWindowMs) {
      return {
        data: {
          createdCount: 0,
          duplicateCount: data.items.length,
        },
        meta: { idempotencyKey, duplicatedRequest: true },
        error: null,
      };
    }

    const session = await this.prisma.interactionSession.findUnique({
      where: { id: data.sessionId },
      select: { id: true, scenarioId: true },
    });

    if (!session) {
      throw new BadRequestException("SESSION_NOT_FOUND");
    }

    const nodeIds = Array.from(
      new Set(
        data.items.flatMap((item) => [item.sourceNodeId, item.targetNodeId]),
      ),
    );

    const nodes = await this.prisma.graphNode.findMany({
      where: { id: { in: nodeIds } },
      select: { id: true, scenarioId: true },
    });

    if (nodes.length !== nodeIds.length) {
      throw new BadRequestException("NODE_NOT_FOUND");
    }

    // 验证所有节点的场景ID与会话的场景ID一致
    for (const node of nodes) {
      if (node.scenarioId !== session.scenarioId) {
        throw new BadRequestException("NODE_SCENARIO_MISMATCH");
      }
    }

    let createdCount = 0;
    let duplicateCount = 0;

    for (const item of data.items) {
      try {
        await this.prisma.interaction.create({
          data: {
            sessionId: data.sessionId,
            sourceNodeId: item.sourceNodeId,
            targetNodeId: item.targetNodeId,
            interactionType: item.interactionType,
            strength: new Prisma.Decimal(item.strength),
            actionType: item.actionType ?? null,
            durationSec: item.durationSec ?? null,
          },
        });
        createdCount += 1;
      } catch (error: any) {
        if (error?.code === "P2002") {
          duplicateCount += 1;
          continue;
        }
        throw error;
      }
    }

    this.recentIdempotency.set(idempotencyKey, now);

    return {
      data: {
        createdCount,
        duplicateCount,
      },
      meta: { idempotencyKey, duplicatedRequest: false },
      error: null,
    };
  }

  // 仅保留最近请求窗口，避免内存持续增长。
  pruneIdempotencyCache() {
    const now = Date.now();
    for (const [key, ts] of this.recentIdempotency.entries()) {
      if (now - ts > 5 * 60 * 1000) {
        this.recentIdempotency.delete(key);
      }
    }
  }
}
