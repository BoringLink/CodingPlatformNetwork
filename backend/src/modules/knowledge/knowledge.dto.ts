import { z } from 'zod';

export const createKnowledgeSchema = z.object({
  content: z.string().min(1, '知识点内容不能为空'),
  knowledgePoint: z.string().min(1, '知识点标识不能为空'),
  grade: z.string().min(1, '年级不能为空'),
  type: z.enum(['知识单元', '知识点'], { required_error: '知识点类型必须是知识单元或知识点' }),
  parentId: z.string().optional(),
  parentName: z.string().optional(),
  relatedKnowledgeIds: z.array(z.string()).optional(),
  relatedKnowledgeNames: z.array(z.string()).optional(),
});

export const updateKnowledgeSchema = z.object({
  content: z.string().min(1, '知识点内容不能为空').optional(),
  knowledgePoint: z.string().min(1, '知识点标识不能为空').optional(),
  grade: z.string().min(1, '年级不能为空').optional(),
  type: z.enum(['知识单元', '知识点'], { required_error: '知识点类型必须是知识单元或知识点' }).optional(),
  parentId: z.string().optional(),
  parentName: z.string().optional(),
  relatedKnowledgeIds: z.array(z.string()).optional(),
  relatedKnowledgeNames: z.array(z.string()).optional(),
});

export type CreateKnowledgeDto = z.infer<typeof createKnowledgeSchema>;
export type UpdateKnowledgeDto = z.infer<typeof updateKnowledgeSchema>;