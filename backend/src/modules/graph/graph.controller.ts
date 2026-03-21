import { BadRequestException, Controller, Get, Query } from "@nestjs/common";
import { GraphService } from "./graph.service";

@Controller("api/v1/graph-data")
export class GraphController {
  constructor(private readonly graphService: GraphService) {}

  @Get()
  async getGraphData(
    @Query("scenario_code") scenarioCode?: string,
    @Query("school_id") schoolId?: string,
    @Query("grade_id") gradeId?: string,
    @Query("class_id") classId?: string,
    @Query("school") school?: string,
    @Query("grade") grade?: string,
    @Query("from") from?: string,
    @Query("to") to?: string,
  ) {
    if (!schoolId && school) {
      throw new BadRequestException("仅支持 school_id 参数");
    }
    if (!gradeId && grade) {
      throw new BadRequestException("仅支持 grade_id 参数");
    }

    return this.graphService.getGraphData({
      scenarioCode,
      schoolId,
      gradeId,
      classId,
      from,
      to,
    });
  }

  @Get("scenario-stats")
  async getScenarioStats(
    @Query("school_id") schoolId?: string,
    @Query("grade_id") gradeId?: string,
    @Query("class_id") classId?: string,
    @Query("school") school?: string,
    @Query("grade") grade?: string,
    @Query("from") from?: string,
    @Query("to") to?: string,
  ) {
    if (!schoolId && school) {
      throw new BadRequestException("仅支持 school_id 参数");
    }
    if (!gradeId && grade) {
      throw new BadRequestException("仅支持 grade_id 参数");
    }

    return this.graphService.getScenarioStats({
      schoolId,
      gradeId,
      classId,
      from,
      to,
    });
  }
}
