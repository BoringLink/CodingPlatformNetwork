import { BadRequestException, Injectable } from "@nestjs/common";
import { Prisma } from "@prisma/client";
import { PrismaService } from "../../shared/utils/prisma.service";
import {
  CreateInteractionSessionDto,
  QueryInteractionSessionDto,
} from "./interaction-session.dto";

@Injectable()
export class InteractionSessionService {
  constructor(private readonly prisma: PrismaService) {}

  async createSession(dto: CreateInteractionSessionDto) {
    const scenario = await this.prisma.learningScenario.findUnique({
      where: { code: dto.scenarioCode },
      select: { id: true },
    });

    if (!scenario) {
      throw new BadRequestException("SCENARIO_CODE_INVALID");
    }

    try {
      const session = await this.prisma.interactionSession.create({
        data: {
          scenarioId: scenario.id,
          sessionName: dto.sessionName,
          occurredAt: new Date(dto.occurredAt),
          schoolId: dto.schoolId,
          gradeId: dto.gradeId,
          classId: dto.classId,
        },
      });

      return {
        data: session,
        meta: null,
        error: null,
      };
    } catch (error) {
      if (error instanceof Error) {
        throw new BadRequestException(error.message);
      }
      throw error;
    }
  }

  async querySessions(query: QueryInteractionSessionDto) {
    const {
      scenarioCode,
      schoolId,
      gradeId,
      classId,
      from,
      to,
      page,
      pageSize,
    } = query;

    let scenarioId: string | undefined;
    if (scenarioCode) {
      const scenario = await this.prisma.learningScenario.findUnique({
        where: { code: scenarioCode },
        select: { id: true },
      });

      if (!scenario) {
        throw new BadRequestException("SCENARIO_CODE_INVALID");
      }
      scenarioId = scenario.id;
    }

    const where: Prisma.InteractionSessionWhereInput = {
      ...(scenarioId ? { scenarioId } : {}),
      ...(schoolId ? { schoolId } : {}),
      ...(gradeId ? { gradeId } : {}),
      ...(classId ? { classId } : {}),
      ...(from || to
        ? {
            occurredAt: {
              ...(from ? { gte: new Date(from) } : {}),
              ...(to ? { lte: new Date(to) } : {}),
            },
          }
        : {}),
    };

    const [items, total] = await this.prisma.$transaction([
      this.prisma.interactionSession.findMany({
        where,
        orderBy: { occurredAt: "desc" },
        skip: (page - 1) * pageSize,
        take: pageSize,
        include: {
          scenario: {
            select: {
              code: true,
              nameZh: true,
            },
          },
        },
      }),
      this.prisma.interactionSession.count({ where }),
    ]);

    return {
      data: items,
      meta: {
        page,
        pageSize,
        total,
      },
      error: null,
    };
  }
}
