import { z } from "zod";

export const createInteractionSessionSchema = z.object({
  scenarioCode: z.string().min(1),
  sessionName: z.string().min(1),
  occurredAt: z.string().datetime(),
  schoolId: z.string().min(1),
  gradeId: z.string().min(1),
  classId: z.string().min(1),
  meta: z.record(z.any()).optional().nullable(),
});

export const queryInteractionSessionSchema = z.object({
  scenarioCode: z.string().optional(),
  schoolId: z.string().optional(),
  gradeId: z.string().optional(),
  classId: z.string().optional(),
  from: z.string().datetime().optional(),
  to: z.string().datetime().optional(),
  page: z.coerce.number().int().min(1).default(1),
  pageSize: z.coerce.number().int().min(1).max(500).default(50),
});

export type CreateInteractionSessionDto = z.infer<
  typeof createInteractionSessionSchema
>;
export type QueryInteractionSessionDto = z.infer<
  typeof queryInteractionSessionSchema
>;
