import { Injectable } from "@nestjs/common";
import { PrismaService } from "../../shared/utils/prisma.service";

@Injectable()
export class ScenarioService {
  constructor(private readonly prisma: PrismaService) {}

  async findAll() {
    const scenarios = await this.prisma.learningScenario.findMany({
      where: { isActive: true },
      orderBy: [{ sortOrder: "asc" }, { createdAt: "asc" }],
      select: {
        code: true,
        nameZh: true,
        sortOrder: true,
        isActive: true,
      },
    });

    return {
      data: scenarios,
      meta: null,
      error: null,
    };
  }
}
