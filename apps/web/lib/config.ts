function getRequiredEnv(name: 'NEXT_PUBLIC_API_BASE_URL' | 'NEXT_PUBLIC_DEV_ORG_ID'): string {
  const value = process.env[name];
  if (!value || !value.trim()) {
    throw new Error(`Missing required environment variable: ${name}`);
  }
  return value;
}

function getApiBaseUrl() {
  const serverSideBaseUrl = process.env.API_BASE_URL;
  if (typeof window === 'undefined' && serverSideBaseUrl && serverSideBaseUrl.trim()) {
    return serverSideBaseUrl;
  }

  return getRequiredEnv('NEXT_PUBLIC_API_BASE_URL');
}

export function getWebRuntimeConfig() {
  return {
    apiBaseUrl: getApiBaseUrl(),
    orgId: getRequiredEnv('NEXT_PUBLIC_DEV_ORG_ID'),
  };
}
