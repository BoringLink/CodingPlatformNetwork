import { z } from 'zod';

export const createStudentSchema = z.object({
  name: z.string().min(1, '姓名不能为空'),
  school: z.string().min(1, '学校名称不能为空'),
  grade: z.string().min(1, '年级不能为空'),
  classId: z.string().min(1, '班级不能为空'),
  knowledgeReserve: z.number().min(1).max(5),
  learningEngagement: z.number().min(1).max(5),
  cognitiveLoad: z.number().min(1).max(5),
  learningMotivation: z.number().min(1).max(5),
  computationalThinking: z.number().min(1).max(5),
  humanAiTrust: z.number().min(1).max(5),
  learningMethod: z.number().min(1).max(5),
  learningAttitude: z.number().min(1).max(5),
});

export const updateStudentSchema = z.object({
  name: z.string().min(1, '姓名不能为空').optional(),
  school: z.string().min(1, '学校名称不能为空').optional(),
  grade: z.string().min(1, '年级不能为空').optional(),
  classId: z.string().min(1, '班级不能为空').optional(),
  knowledgeReserve: z.number().min(1).max(5).optional(),
  learningEngagement: z.number().min(1).max(5).optional(),
  cognitiveLoad: z.number().min(1).max(5).optional(),
  learningMotivation: z.number().min(1).max(5).optional(),
  computationalThinking: z.number().min(1).max(5).optional(),
  humanAiTrust: z.number().min(1).max(5).optional(),
  learningMethod: z.number().min(1).max(5).optional(),
  learningAttitude: z.number().min(1).max(5).optional(),
});

export type CreateStudentDto = z.infer<typeof createStudentSchema>;
export type UpdateStudentDto = z.infer<typeof updateStudentSchema>;