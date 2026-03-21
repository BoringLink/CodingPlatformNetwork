import {
  Controller,
  Get,
  Param,
  HttpException,
  HttpStatus,
} from "@nestjs/common";
import { StudentService } from "./student.service";

@Controller("api/v1/students")
export class StudentController {
  constructor(private readonly studentService: StudentService) {}

  @Get(":id/cognitive-template")
  async getCognitiveTemplate(@Param("id") id: string) {
    const result = await this.studentService.getLatestCognitiveTemplate(id);
    if (!result) {
      throw new HttpException("学生不存在", HttpStatus.NOT_FOUND);
    }
    return result;
  }
}
