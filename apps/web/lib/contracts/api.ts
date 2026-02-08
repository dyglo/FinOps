export type ApiResponse<T> = {
  data: T;
  error: string | null;
  meta: {
    request_id: string;
    org_id: string;
    ts: string;
    version: string;
  };
};

export type IngestionJobCreate = {
  provider: 'tavily';
  resource: 'news_search';
  idempotency_key: string;
  payload: Record<string, unknown>;
};

export type IngestionJobRead = {
  id: string;
  org_id: string;
  provider: string;
  resource: string;
  status: string;
  idempotency_key: string;
  payload: Record<string, unknown>;
  attempt_count: number;
  error_message: string | null;
  started_at: string | null;
  completed_at: string | null;
  raw_record_count: number;
  normalized_record_count: number;
  created_at: string;
  updated_at: string;
};

export type NewsDocumentRead = {
  id: string;
  org_id: string;
  job_id: string;
  source_provider: string;
  source_url: string;
  title: string;
  snippet: string;
  author: string | null;
  language: string | null;
  published_at: string | null;
  created_at: string;
};

export type IntelRunCreate = {
  run_type: string;
  model_name: string;
  prompt_version: string;
  input_snapshot_uri: string;
  input_payload: Record<string, unknown>;
  execution_mode?: 'live' | 'replay';
  replay_source_run_id?: string | null;
};

export type IntelReplayCreate = {
  model_name?: string;
  prompt_version?: string;
};

export type IntelRunRead = {
  id: string;
  org_id: string;
  run_type: string;
  status: string;
  model_name: string;
  prompt_version: string;
  input_snapshot_uri: string;
  input_payload: Record<string, unknown>;
  graph_version: string;
  execution_mode: string;
  replay_source_run_id: string | null;
  error_message: string | null;
  completed_at: string | null;
  output_payload: Record<string, unknown>;
  created_at: string;
  updated_at: string;
};
