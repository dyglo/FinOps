import { getWebRuntimeConfig } from '../config';

export type ApiRequestOptions = {
  orgId?: string;
  requestId?: string;
  params?: Record<string, string | number | undefined>;
};

class ApiError extends Error {
  constructor(public status: number, public statusText: string, public body: any) {
    super(`API Error: ${status} ${statusText}`);
  }
}

function getSettings() {
  if (typeof window === 'undefined') return {
    baseUrl: process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000',
    orgId: process.env.NEXT_PUBLIC_DEV_ORG_ID || '00000000-0000-0000-0000-000000000000'
  };

  const storedBaseUrl = localStorage.getItem('finops_api_url');
  const storedOrgId = localStorage.getItem('finops_org_id');
  const config = getWebRuntimeConfig();

  return {
    baseUrl: storedBaseUrl || config.apiBaseUrl,
    orgId: storedOrgId || config.orgId
  };
}

async function request<T>(
  path: string,
  method: 'GET' | 'POST' | 'PUT' | 'DELETE' = 'GET',
  body?: any,
  options?: ApiRequestOptions
): Promise<T> {
  const { baseUrl, orgId: defaultOrgId } = getSettings();
  const orgId = options?.orgId || defaultOrgId;
  const requestId = options?.requestId || crypto.randomUUID();

  const url = new URL(`${baseUrl}${path}`);
  if (options?.params) {
    Object.entries(options.params).forEach(([key, value]) => {
      if (value !== undefined) url.searchParams.append(key, String(value));
    });
  }

  const response = await fetch(url.toString(), {
    method,
    headers: {
      'Content-Type': 'application/json',
      'X-Org-Id': orgId,
      'X-Request-Id': requestId,
    },
    body: body ? JSON.stringify(body) : undefined,
  });

  if (!response.ok) {
    let errorBody;
    try {
      errorBody = await response.json();
    } catch {
      errorBody = await response.text();
    }
    throw new ApiError(response.status, response.statusText, errorBody);
  }

  return response.json() as Promise<T>;
}

export const api = {
  get: <T>(path: string, options?: ApiRequestOptions) => request<T>(path, 'GET', undefined, options),
  post: <T>(path: string, body: any, options?: ApiRequestOptions) => request<T>(path, 'POST', body, options),
};