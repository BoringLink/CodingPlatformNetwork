import {
  Controller,
  Get,
  Post,
  Delete,
  Param,
  Query,
  Body,
  HttpException,
  HttpStatus,
} from "@nestjs/common";
import { TeacherClassMappingService } from "./teacher-class-mapping.service";
import {
  CreateTeacherClassMappingDto,
  createTeacherClassMappingSchema,
} from "./teacher-class-mapping.dto";

@Controller("api/v1/teacher-class-mappings")
export class TeacherClassMappingController {
  constructor(
    private readonly teacherClassMappingService: TeacherClassMappingService,
  ) {}

  @Get()
  async findAll(
    @Query("teacher_id") teacherId?: string,
    @Query("grade") grade?: string,
    @Query("class_id") classId?: string,
  ) {
    const mappings = await this.teacherClassMappingService.findAll({
      teacherId,
      grade,
      classId,
    });
    return { data: mappings };
  }

  @Post()
  async create(@Body() body: CreateTeacherClassMappingDto) {
    try {
      const validatedData = createTeacherClassMappingSchema.parse(body);
      return this.teacherClassMappingService.create(validatedData);
    } catch (error) {
      throw new HttpException(
        error.errors || "请求参数错误",
        HttpStatus.BAD_REQUEST,
      );
    }
  }

  @Delete(":id")
  async delete(@Param("id") id: string) {
    try {
      const result = await this.teacherClassMappingService.delete(id);
      return result;
    } catch {
      throw new HttpException("教师-班级关联不存在", HttpStatus.NOT_FOUND);
    }
  }
}
