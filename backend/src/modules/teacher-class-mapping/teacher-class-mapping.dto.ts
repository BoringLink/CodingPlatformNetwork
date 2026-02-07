import { z } from 'zod';

export const createTeacherClassMappingSchema = z.object({
  teacherId: z.string().min(1, '教师ID不能为空'),
  grade: z.string().min(1, '年级不能为空'),
  classId: z.string().min(1, '班级不能为空'),
});

export type CreateTeacherClassMappingDto = z.infer<typeof createTeacherClassMappingSchema>;
