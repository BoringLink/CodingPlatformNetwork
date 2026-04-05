import { BadRequestException, Controller, Get, Query } from "@nestjs/common";
import { OrgService } from "./org.service";

@Controller("api/v1/org")
export class OrgController {
  constructor(private readonly orgService: OrgService) {}

  @Get("schools")
  async getSchools() {
    return this.orgService.getSchools();
  }

  @Get("grades")
  async getGrades(
    @Query("school_id") schoolId?: string,
    @Query("school") school?: string,
  ) {
    if (!schoolId) {
      if (school) {
        throw new BadRequestException("仅支持 school_id 参数");
      }
      throw new BadRequestException("school_id 为必填参数");
    }

    return this.orgService.getGrades(schoolId);
  }

  @Get("classes")
  async getClasses(
    @Query("grade_id") gradeId?: string,
    @Query("grade") grade?: string,
  ) {
    if (!gradeId) {
      if (grade) {
        throw new BadRequestException("仅支持 grade_id 参数");
      }
      throw new BadRequestException("grade_id 为必填参数");
    }

    return this.orgService.getClasses(gradeId);
  }

  @Get("hierarchy")
  async getOrgHierarchy() {
    return this.orgService.getOrgHierarchy();
  }
}
