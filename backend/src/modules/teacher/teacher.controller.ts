import { Controller, Get, Post, Put, Delete, Param, Query, Body, HttpException, HttpStatus } from '@nestjs/common';
import { TeacherService } from './teacher.service';
import { CreateTeacherDto, UpdateTeacherDto, createTeacherSchema, updateTeacherSchema } from './teacher.dto';

@Controller('api/v1/teachers')
export class TeacherController {
  constructor(private readonly teacherService: TeacherService) {}

  @Get()
  async findAll(
    @Query('school') school?: string,
  ) {
    return this.teacherService.findAll({ school });
  }

  @Get(':id')
  async findOne(@Param('id') id: string) {
    const teacher = await this.teacherService.findOne(id);
    if (!teacher) {
      throw new HttpException('教师不存在', HttpStatus.NOT_FOUND);
    }
    return teacher;
  }

  @Post()
  async create(@Body() body: CreateTeacherDto) {
    try {
      const validatedData = createTeacherSchema.parse(body);
      return this.teacherService.create(validatedData);
    } catch (error) {
      throw new HttpException(error.errors || '请求参数错误', HttpStatus.BAD_REQUEST);
    }
  }

  @Put(':id')
  async update(@Param('id') id: string, @Body() body: UpdateTeacherDto) {
    try {
      const validatedData = updateTeacherSchema.parse(body);
      const teacher = await this.teacherService.update(id, validatedData);
      if (!teacher) {
        throw new HttpException('教师不存在', HttpStatus.NOT_FOUND);
      }
      return teacher;
    } catch (error) {
      if (error instanceof HttpException) {
        throw error;
      }
      throw new HttpException(error.errors || '请求参数错误', HttpStatus.BAD_REQUEST);
    }
  }

  @Delete(':id')
  async delete(@Param('id') id: string) {
    try {
      const result = await this.teacherService.delete(id);
      return result;
    } catch {
      throw new HttpException('教师不存在', HttpStatus.NOT_FOUND);
    }
  }
}