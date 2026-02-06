import { Injectable } from "@nestjs/common";
import { PrismaService } from "../../shared/utils/prisma.service";
import { CreateInteractionDto, UpdateInteractionDto } from "./interaction.dto";

@Injectable()
export class InteractionService {
  constructor(private prisma: PrismaService) {}

  async findAll(params: {
    sourceId?: string;
    targetId?: string;
    sourceType?: string;
    targetType?: string;
    type?: string;
  }) {
    const { sourceId, targetId, sourceType, targetType, type } = params;

    const where = {
      ...(sourceId && { sourceId }),
      ...(targetId && { targetId }),
      ...(sourceType && { sourceType }),
      ...(targetType && { targetType }),
      ...(type && { type }),
    };

    const interactions = await this.prisma.interaction.findMany({
      where,
      orderBy: { createdAt: "desc" },
    });

    return { data: interactions };
  }

  async findOne(id: string) {
    return this.prisma.interaction.findUnique({ where: { id } });
  }

  async create(data: CreateInteractionDto) {
    return this.prisma.interaction.create({
      data: {
        sourceId: data.sourceId,
        targetId: data.targetId,
        sourceType: data.sourceType,
        targetType: data.targetType,
        value: data.value,
        type: data.type,
        interactionType: data.interactionType || null,
      },
    });
  }

  async update(id: string, data: UpdateInteractionDto) {
    return this.prisma.interaction.update({
      where: { id },
      data,
    });
  }

  async delete(id: string) {
    await this.prisma.interaction.delete({ where: { id } });
    return { message: "交互删除成功" };
  }
}
