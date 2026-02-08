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

// Ingestion
export const IngestionJobReadSchema = z.object({
  id: z.string().uuid(),
  org_id: z.string().uuid(),
  provider: z.string(),
  resource: z.string(),
  status: z.enum(['pending', 'processing', 'completed', 'failed', 'queued']),
  idempotency_key: z.string(),
  payload: z.record(z.string(), z.unknown()),
  attempt_count: z.number(),
  error_message: z.string().nullable(),
  started_at: z.string().nullable(),
  completed_at: z.string().nullable(),
  raw_record_count: z.number(),
  normalized_record_count: z.number(),
  created_at: z.string(),
  updated_at: z.string(),
});

// Documents
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

// Market
export const TimeseriesPointReadSchema = z.object({
  symbol: z.string(),
  timestamp: z.string(),
  open: z.number(),
  high: z.number(),
  low: z.number(),
  close: z.number(),
  volume: z.number(),
});

// Intel
export const IntelRunReadSchema = z.object({
  id: z.string().uuid(),
  org_id: z.string().uuid(),
  run_type: z.string(),
  status: z.string(),
  model_name: z.string(),
  prompt_version: z.string(),
  input_snapshot_uri: z.string(),
  input_payload: z.record(z.string(), z.unknown()),
  graph_version: z.string(),
  execution_mode: z.string(),
  replay_source_run_id: z.string().nullable(),
  error_message: z.string().nullable(),
  completed_at: z.string().nullable(),
  output_payload: z.record(z.string(), z.unknown()),
  created_at: z.string(),
  updated_at: z.string(),
});

// Signals
export const SignalFeatureReadSchema = z.object({
  id: z.string().uuid(),
  org_id: z.string().uuid(),
  symbol: z.string(),
  signal_type: z.string(),
  value: z.number(),
  confidence: z.number(),
  timestamp: z.string(),
  metadata: z.record(z.string(), z.unknown()),
});

// System
export const SystemContextReadSchema = z.object({
    org_id: z.string(),
});


export const NewsListResponseSchema = createApiResponseSchema(z.array(NewsDocumentReadSchema));
export const IngestionJobResponseSchema = createApiResponseSchema(IngestionJobReadSchema);
export const MarketTimeseriesResponseSchema = createApiResponseSchema(z.array(TimeseriesPointReadSchema));
export const IntelRunResponseSchema = createApiResponseSchema(IntelRunReadSchema);
export const SignalListResponseSchema = createApiResponseSchema(z.array(SignalFeatureReadSchema));
export const SystemContextResponseSchema = createApiResponseSchema(SystemContextReadSchema);