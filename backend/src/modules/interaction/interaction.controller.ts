import { Controller, Get, Post, Put, Delete, Param, Query, Body, HttpException, HttpStatus } from '@nestjs/common';
import { InteractionService } from './interaction.service';
import { CreateInteractionDto, UpdateInteractionDto, createInteractionSchema, updateInteractionSchema } from './interaction.dto';

@Controller('api/v1/interactions')
export class InteractionController {
  constructor(private readonly interactionService: InteractionService) {}

  @Get()
  async findAll(
    @Query('source_id') sourceId?: string,
    @Query('target_id') targetId?: string,
    @Query('source_type') sourceType?: string,
    @Query('target_type') targetType?: string,
    @Query('type') type?: string,
  ) {
    return this.interactionService.findAll({ sourceId, targetId, sourceType, targetType, type });
  }

  @Get(':id')
  async findOne(@Param('id') id: string) {
    const interaction = await this.interactionService.findOne(id);
    if (!interaction) {
      throw new HttpException('交互不存在', HttpStatus.NOT_FOUND);
    }
    return interaction;
  }

  @Post()
  async create(@Body() body: CreateInteractionDto) {
    try {
      const validatedData = createInteractionSchema.parse(body);
      return this.interactionService.create(validatedData);
    } catch (error) {
      throw new HttpException(error.errors || '请求参数错误', HttpStatus.BAD_REQUEST);
    }
  }

  @Put(':id')
  async update(@Param('id') id: string, @Body() body: UpdateInteractionDto) {
    try {
      const validatedData = updateInteractionSchema.parse(body);
      const interaction = await this.interactionService.update(id, validatedData);
      if (!interaction) {
        throw new HttpException('交互不存在', HttpStatus.NOT_FOUND);
      }
      return interaction;
    } catch (error) {
      throw new HttpException(error.errors || '请求参数错误', HttpStatus.BAD_REQUEST);
    }
  }

  @Delete(':id')
  async delete(@Param('id') id: string) {
    try {
      return this.interactionService.delete(id);
    } catch {
      throw new HttpException('交互不存在', HttpStatus.NOT_FOUND);
    }
  }
}