import {
  Body,
  Controller,
  Get,
  HttpException,
  HttpStatus,
  Post,
  Query,
} from "@nestjs/common";
import {
  createInteractionSessionSchema,
  queryInteractionSessionSchema,
} from "./interaction-session.dto";
import { InteractionSessionService } from "./interaction-session.service";

@Controller("api/v1/interaction-sessions")
export class InteractionSessionController {
  constructor(
    private readonly interactionSessionService: InteractionSessionService,
  ) {}

  @Post()
  async createSession(@Body() body: unknown) {
    try {
      const dto = createInteractionSessionSchema.parse(body);
      return this.interactionSessionService.createSession(dto);
    } catch (error: any) {
      throw new HttpException(
        error.errors || "VALIDATION_ERROR",
        HttpStatus.BAD_REQUEST,
      );
    }
  }

  @Get()
  async querySessions(
    @Query("scenario_code") scenarioCode?: string,
    @Query("school_id") schoolId?: string,
    @Query("grade_id") gradeId?: string,
    @Query("class_id") classId?: string,
    @Query("school") school?: string,
    @Query("grade") grade?: string,
    @Query("from") from?: string,
    @Query("to") to?: string,
    @Query("page") page?: string,
    @Query("page_size") pageSize?: string,
  ) {
    try {
      const query = queryInteractionSessionSchema.parse({
        scenarioCode,
        schoolId: schoolId ?? school,
        gradeId: gradeId ?? grade,
        classId,
        from,
        to,
        page,
        pageSize,
      });
      return this.interactionSessionService.querySessions(query);
    } catch (error: any) {
      throw new HttpException(
        error.errors || "VALIDATION_ERROR",
        HttpStatus.BAD_REQUEST,
      );
    }
  }
}
