import { getWebRuntimeConfig } from '@/lib/config';
import type {
  ApiResponse,
  IngestionJobCreate,
  IngestionJobRead,
  IntelReplayCreate,
  IntelRunCreate,
  IntelRunRead,
  NewsDocumentRead,
} from '@/lib/contracts/api';

type NewsQuery = {
  job_id?: string;
  q?: string;
  limit?: number;
  offset?: number;
};

class FinopsApiError extends Error {
  readonly statusCode: number;

  constructor(message: string, statusCode: number) {
    super(message);
    this.statusCode = statusCode;
  }
}

function buildUrl(path: string, query?: Record<string, string | number | undefined>) {
  const { apiBaseUrl } = getWebRuntimeConfig();
  const url = new URL(path, apiBaseUrl);
  if (query) {
    Object.entries(query).forEach(([key, value]) => {
      if (value !== undefined) {
        url.searchParams.set(key, String(value));
      }
    });
  }
  return url;
}

async function apiFetch<T>(
  path: string,
  init?: RequestInit,
  query?: Record<string, string | number | undefined>,
): Promise<T> {
  const { orgId } = getWebRuntimeConfig();
  const response = await fetch(buildUrl(path, query), {
    ...init,
    headers: {
      'Content-Type': 'application/json',
      'X-Org-Id': orgId,
      ...(init?.headers ?? {}),
    },
    cache: 'no-store',
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new FinopsApiError(errorText || 'Request failed', response.status);
  }

  return (await response.json()) as T;
}

export const finopsApiClient = {
  async createIngestionJob(payload: IngestionJobCreate): Promise<ApiResponse<IngestionJobRead>> {
    return apiFetch<ApiResponse<IngestionJobRead>>('/v1/ingestion/jobs', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  },

  async getIngestionJob(jobId: string): Promise<ApiResponse<IngestionJobRead>> {
    return apiFetch<ApiResponse<IngestionJobRead>>(`/v1/ingestion/jobs/${jobId}`);
  },

  async listNewsDocuments(query: NewsQuery = {}): Promise<ApiResponse<NewsDocumentRead[]>> {
    return apiFetch<ApiResponse<NewsDocumentRead[]>>('/v1/documents/news', undefined, query);
  },

  async createIntelRun(payload: IntelRunCreate): Promise<ApiResponse<IntelRunRead>> {
    return apiFetch<ApiResponse<IntelRunRead>>('/v1/intel/runs', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  },

  async getIntelRun(runId: string): Promise<ApiResponse<IntelRunRead>> {
    return apiFetch<ApiResponse<IntelRunRead>>(`/v1/intel/runs/${runId}`);
  },

  async replayIntelRun(runId: string, payload: IntelReplayCreate = {}): Promise<ApiResponse<IntelRunRead>> {
    return apiFetch<ApiResponse<IntelRunRead>>(`/v1/intel/runs/${runId}/replay`, {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  },
};

export { FinopsApiError };
