import { z } from 'zod';

export const createInteractionSchema = z.object({
  sourceId: z.string().min(1, '源节点ID不能为空'),
  targetId: z.string().min(1, '目标节点ID不能为空'),
  sourceType: z.enum(['STUDENT', 'TEACHER', 'KNOWLEDGE'], { required_error: '源节点类型必须是STUDENT、TEACHER或KNOWLEDGE' }),
  targetType: z.enum(['STUDENT', 'TEACHER', 'KNOWLEDGE'], { required_error: '目标节点类型必须是STUDENT、TEACHER或KNOWLEDGE' }),
  value: z.number().min(0.1).max(5, '交互值必须在0.1-5之间'),
  type: z.enum(['PHYSICAL', 'PLATFORM'], { required_error: '交互类型必须是PHYSICAL或PLATFORM' }),
  interactionType: z.string().optional(),
});

export const updateInteractionSchema = z.object({
  sourceId: z.string().min(1, '源节点ID不能为空').optional(),
  targetId: z.string().min(1, '目标节点ID不能为空').optional(),
  sourceType: z.enum(['STUDENT', 'TEACHER', 'KNOWLEDGE'], { required_error: '源节点类型必须是STUDENT、TEACHER或KNOWLEDGE' }).optional(),
  targetType: z.enum(['STUDENT', 'TEACHER', 'KNOWLEDGE'], { required_error: '目标节点类型必须是STUDENT、TEACHER或KNOWLEDGE' }).optional(),
  value: z.number().min(0.1).max(5, '交互值必须在0.1-5之间').optional(),
  type: z.enum(['PHYSICAL', 'PLATFORM'], { required_error: '交互类型必须是PHYSICAL或PLATFORM' }).optional(),
  interactionType: z.string().optional(),
});

export type CreateInteractionDto = z.infer<typeof createInteractionSchema>;
export type UpdateInteractionDto = z.infer<typeof updateInteractionSchema>;