import {
  Body,
  Controller,
  Get,
  HttpException,
  HttpStatus,
  Post,
  Query,
} from "@nestjs/common";
import { NodeService } from "./node.service";
import { createNodeSchema, queryNodeSchema } from "./node.dto";

@Controller("api/v1/nodes")
export class NodeController {
  constructor(private readonly nodeService: NodeService) {}

  @Get()
  async queryNodes(
    @Query("node_type") nodeType?: string,
    @Query("school") school?: string,
    @Query("grade") grade?: string,
    @Query("class_id") classId?: string,
    @Query("page") page?: string,
    @Query("page_size") pageSize?: string,
  ) {
    try {
      const query = queryNodeSchema.parse({
        nodeType,
        school,
        grade,
        classId,
        page,
        pageSize,
      });
      return this.nodeService.queryNodes(query);
    } catch (error: any) {
      throw new HttpException(
        error.errors || "VALIDATION_ERROR",
        HttpStatus.BAD_REQUEST,
      );
    }
  }

  @Post()
  async createNode(@Body() body: unknown) {
    try {
      const dto = createNodeSchema.parse(body);
      return this.nodeService.createNode(dto);
    } catch (error: any) {
      throw new HttpException(
        error.errors || "VALIDATION_ERROR",
        HttpStatus.BAD_REQUEST,
      );
    }
  }
}
