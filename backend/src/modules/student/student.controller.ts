import { Controller, Get, Post, Put, Delete, Param, Query, Body, HttpException, HttpStatus } from '@nestjs/common';
import { StudentService } from './student.service';
import { CreateStudentDto, UpdateStudentDto, createStudentSchema, updateStudentSchema } from './student.dto';

@Controller('api/v1/students')
export class StudentController {
  constructor(private readonly studentService: StudentService) {}

  @Get()
  async findAll(
    @Query('school') school?: string,
    @Query('grade') grade?: string,
    @Query('class_id') classId?: string,
  ) {
    return this.studentService.findAll({ school, grade, classId });
  }

  @Get(':id')
  async findOne(@Param('id') id: string) {
    const student = await this.studentService.findOne(id);
    if (!student) {
      throw new HttpException('学生不存在', HttpStatus.NOT_FOUND);
    }
    return student;
  }

  @Post()
  async create(@Body() body: CreateStudentDto) {
    try {
      const validatedData = createStudentSchema.parse(body);
      return this.studentService.create(validatedData);
    } catch (error) {
      throw new HttpException(error.errors || '请求参数错误', HttpStatus.BAD_REQUEST);
    }
  }

  @Put(':id')
  async update(@Param('id') id: string, @Body() body: UpdateStudentDto) {
    try {
      const validatedData = updateStudentSchema.parse(body);
      const student = await this.studentService.update(id, validatedData);
      if (!student) {
        throw new HttpException('学生不存在', HttpStatus.NOT_FOUND);
      }
      return student;
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
      const result = await this.studentService.delete(id);
      return result;
    } catch (error) {
      throw new HttpException('学生不存在', HttpStatus.NOT_FOUND);
    }
  }
}