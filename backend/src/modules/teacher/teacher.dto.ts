import { z } from 'zod';

export const createTeacherSchema = z.object({
  name: z.string().min(1, '姓名不能为空'),
  school: z.string().min(1, '学校名称不能为空'),
  teachingGrade: z.string().min(1, '教学年级不能为空'),
  teachingClass: z.string().min(1, '教学班级不能为空'),
});

export const updateTeacherSchema = z.object({
  name: z.string().min(1, '姓名不能为空').optional(),
  school: z.string().min(1, '学校名称不能为空').optional(),
  teachingGrade: z.string().min(1, '教学年级不能为空').optional(),
  teachingClass: z.string().min(1, '教学班级不能为空').optional(),
});

export type CreateTeacherDto = z.infer<typeof createTeacherSchema>;
export type UpdateTeacherDto = z.infer<typeof updateTeacherSchema>;