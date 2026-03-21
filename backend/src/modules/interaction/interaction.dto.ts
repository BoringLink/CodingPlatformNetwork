import { z } from "zod";

export const batchCreateInteractionsSchema = z.object({
  sessionId: z.string().min(1),
  items: z
    .array(
      z.object({
        sourceNodeId: z.string().min(1),
        targetNodeId: z.string().min(1),
        interactionType: z.enum(["PHYSICAL", "PLATFORM"]),
        strength: z.number().min(0),
        actionType: z.string().optional().nullable(),
        durationSec: z.number().int().min(0).optional().nullable(),
      }),
    )
    .min(1),
});

export const queryInteractionsSchema = z.object({
  scenarioCode: z.string().optional(),
  sessionId: z.string().optional(),
  sourceNodeId: z.string().optional(),
  targetNodeId: z.string().optional(),
  page: z.coerce.number().int().min(1).default(1),
  pageSize: z.coerce.number().int().min(1).max(500).default(50),
});

export type BatchCreateInteractionsDto = z.infer<
  typeof batchCreateInteractionsSchema
>;
export type QueryInteractionsDto = z.infer<typeof queryInteractionsSchema>;
