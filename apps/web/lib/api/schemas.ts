import { z } from 'zod';

export const MetaEnvelopeSchema = z.object({
  request_id: z.string(),
  org_id: z.string(),
  ts: z.string(),
  version: z.string().optional(),
});

export function createApiResponseSchema<T extends z.ZodTypeAny>(dataSchema: T) {
  return z.object({
    data: dataSchema,
    meta: MetaEnvelopeSchema,
  });
}

export const IngestionJobReadSchema = z.object({
  id: z.string().uuid(),
  org_id: z.string().uuid(),
  provider: z.string(),
  resource: z.string(),
  status: z.enum(['pending', 'processing', 'completed', 'failed']),
  idempotency_key: z.string(),
  payload: z.record(z.unknown()),
  attempt_count: z.number(),
  error_message: z.string().nullable(),
  started_at: z.string().nullable(),
  completed_at: z.string().nullable(),
  raw_record_count: z.number(),
  normalized_record_count: z.number(),
  created_at: z.string(),
  updated_at: z.string(),
});

export const NewsDocumentReadSchema = z.object({
  id: z.string().uuid(),
  org_id: z.string().uuid(),
  job_id: z.string().uuid(),
  source_provider: z.string(),
  source_url: z.string(),
  title: z.string(),
  snippet: z.string(),
  author: z.string().nullable(),
  language: z.string().nullable(),
  published_at: z.string().nullable(),
  created_at: z.string(),
});

export const NewsListResponseSchema = createApiResponseSchema(z.array(NewsDocumentReadSchema));
export const IngestionJobResponseSchema = createApiResponseSchema(IngestionJobReadSchema);
