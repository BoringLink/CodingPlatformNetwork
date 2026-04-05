import { z } from "zod";

export const nodeTypeSchema = z.enum(["STUDENT", "TEACHER", "KNOWLEDGE"]);

export const createNodeSchema = z.object({
  nodeType: nodeTypeSchema,
  displayName: z.string().min(1),
  scenarioId: z.string().trim(),
  schoolId: z.string().trim().optional().nullable(),
  gradeId: z.string().trim().optional().nullable(),
  classId: z.string().trim().optional().nullable(),
  profile: z
    .object({
      learningStylePreference: z.string().optional().nullable(),
      personality: z.string().optional().nullable(),
      groupBehavior: z.string().optional().nullable(),
      teachingGrade: z.number().optional().nullable(),
      teachingClass: z.string().optional().nullable(),
      subject: z.string().optional().nullable(),
      content: z.string().optional(),
      knowledgeType: z.string().optional(),
      category: z.string().optional().nullable(),
      parentNodeId: z.string().optional().nullable(),
    })
    .optional(),
});

export const queryNodeSchema = z.object({
  nodeType: nodeTypeSchema.optional(),
  scenarioId: z.string().optional(),
  schoolId: z.string().optional(),
  gradeId: z.string().optional(),
  classId: z.string().optional(),
  page: z.coerce.number().int().min(1).default(1),
  pageSize: z.coerce.number().int().min(1).max(500).default(50),
});

export type CreateNodeDto = z.infer<typeof createNodeSchema>;
export type QueryNodeDto = z.infer<typeof queryNodeSchema>;
