import { z } from 'zod';

export const importDataSchema = z.object({
  fileType: z.enum(['survey', 'json', 'excel'], { required_error: '文件类型必须是survey、json或excel' }).optional(),
  fileUrl: z.string().url('文件URL必须是有效的URL格式').optional(),
});

export type ImportDataDto = z.infer<typeof importDataSchema>;