import { Controller, Get, Query } from '@nestjs/common';
import { GraphService } from './graph.service';

@Controller('api/v1/graph-data')
export class GraphController {
  constructor(private readonly graphService: GraphService) {}

  @Get()
  async getGraphData(
    @Query('scenario') scenario?: string,
    @Query('school') school?: string,
    @Query('grade') grade?: string,
    @Query('class_id') classId?: string,
  ) {
    return this.graphService.getGraphData({ scenario, school, grade, classId });
  }
}