function getEnv(name: string, defaultValue: string): string {
  const value = process.env[name];
  if (!value || !value.trim()) {
    return defaultValue;
  }
  return value;
}

function getApiBaseUrl() {
  const serverSideBaseUrl = process.env.API_BASE_URL;
  if (typeof window === 'undefined' && serverSideBaseUrl && serverSideBaseUrl.trim()) {
    return serverSideBaseUrl;
  }

  return getEnv('NEXT_PUBLIC_API_BASE_URL', 'http://localhost:8000');
}

export function getWebRuntimeConfig() {
  return {
    apiBaseUrl: getApiBaseUrl(),
    orgId: getEnv('NEXT_PUBLIC_DEV_ORG_ID', '00000000-0000-0000-0000-000000000000'),
  };
}