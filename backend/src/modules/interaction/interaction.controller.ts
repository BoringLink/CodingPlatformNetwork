import {
  Body,
  Controller,
  Get,
  Headers,
  HttpException,
  HttpStatus,
  Post,
  Query,
} from "@nestjs/common";
import { InteractionService } from "./interaction.service";
import {
  batchCreateInteractionsSchema,
  queryInteractionsSchema,
} from "./interaction.dto";

@Controller("api/v1/interactions")
export class InteractionController {
  constructor(private readonly interactionService: InteractionService) {}

  @Get()
  async findAll(
    @Query("scenario_code") scenarioCode?: string,
    @Query("session_id") sessionId?: string,
    @Query("source_node_id") sourceNodeId?: string,
    @Query("target_node_id") targetNodeId?: string,
    @Query("page") page?: string,
    @Query("page_size") pageSize?: string,
  ) {
    try {
      const query = queryInteractionsSchema.parse({
        scenarioCode,
        sessionId,
        sourceNodeId,
        targetNodeId,
        page,
        pageSize,
      });
      return this.interactionService.findAll(query);
    } catch (error: any) {
      throw new HttpException(
        error.errors || "VALIDATION_ERROR",
        HttpStatus.BAD_REQUEST,
      );
    }
  }

  @Post("batchCreate")
  async batchCreate(
    @Body() body: unknown,
    @Headers("idempotency-key") idempotencyKey?: string,
  ) {
    try {
      const dto = batchCreateInteractionsSchema.parse(body);
      return this.interactionService.batchCreate(dto, idempotencyKey);
    } catch (error: any) {
      throw new HttpException(
        error.errors || "VALIDATION_ERROR",
        HttpStatus.BAD_REQUEST,
      );
    }
  }
}
