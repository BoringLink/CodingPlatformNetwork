import { Controller, Get, Post, Put, Delete, Param, Query, Body, HttpException, HttpStatus } from '@nestjs/common';
import { KnowledgeService } from './knowledge.service';
import { CreateKnowledgeDto, UpdateKnowledgeDto, createKnowledgeSchema, updateKnowledgeSchema } from './knowledge.dto';

@Controller('api/v1/knowledge-points')
export class KnowledgeController {
  constructor(private readonly knowledgeService: KnowledgeService) {}

  @Get()
  async findAll(
    @Query('grade') grade?: string,
    @Query('type') type?: string,
    @Query('parent_id') parentId?: string,
  ) {
    return this.knowledgeService.findAll({ grade, type, parentId });
  }

  @Get(':id')
  async findOne(@Param('id') id: string) {
    const knowledge = await this.knowledgeService.findOne(id);
    if (!knowledge) {
      throw new HttpException('知识点不存在', HttpStatus.NOT_FOUND);
    }
    return knowledge;
  }

  @Post()
  async create(@Body() body: CreateKnowledgeDto) {
    try {
      const validatedData = createKnowledgeSchema.parse(body);
      return this.knowledgeService.create(validatedData);
    } catch (error) {
      throw new HttpException(error.errors || '请求参数错误', HttpStatus.BAD_REQUEST);
    }
  }

  @Put(':id')
  async update(@Param('id') id: string, @Body() body: UpdateKnowledgeDto) {
    try {
      const validatedData = updateKnowledgeSchema.parse(body);
      const knowledge = await this.knowledgeService.update(id, validatedData);
      if (!knowledge) {
        throw new HttpException('知识点不存在', HttpStatus.NOT_FOUND);
      }
      return knowledge;
    } catch (error) {
      throw new HttpException(error.errors || '请求参数错误', HttpStatus.BAD_REQUEST);
    }
  }

  @Delete(':id')
  async delete(@Param('id') id: string) {
    try {
      return this.knowledgeService.delete(id);
    } catch {
      throw new HttpException('知识点不存在', HttpStatus.NOT_FOUND);
    }
  }
}