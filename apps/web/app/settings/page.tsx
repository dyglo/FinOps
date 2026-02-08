'use client';

import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { getWebRuntimeConfig } from '@/lib/config';

export default function SettingsPage() {
  const [apiUrl, setApiUrl] = useState(() => {
    if (typeof window !== 'undefined') {
      return localStorage.getItem('finops_api_url') || getWebRuntimeConfig().apiBaseUrl;
    }
    return '';
  });

  const [orgId, setOrgId] = useState(() => {
    if (typeof window !== 'undefined') {
      return localStorage.getItem('finops_org_id') || getWebRuntimeConfig().orgId;
    }
    return '';
  });

  const [isSaved, setIsSaved] = useState(false);

  const handleSave = () => {
    localStorage.setItem('finops_api_url', apiUrl);
    localStorage.setItem('finops_org_id', orgId);
    setIsSaved(true);
    setTimeout(() => setIsSaved(false), 2000);
    window.location.reload();
  };

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <header>
        <h1 className="text-3xl font-bold text-[var(--text-strong)]">Settings</h1>
        <p className="text-[var(--text-muted)] mt-2">Configure your developer environment and tenant settings.</p>
      </header>

      <Card>
        <CardHeader>
          <CardTitle>API Configuration</CardTitle>
          <CardDescription>Set the base URL for the FinOps API and your organization ID.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <label className="text-sm font-medium">API Base URL</label>
            <Input 
              value={apiUrl} 
              onChange={(e) => setApiUrl(e.target.value)} 
              placeholder="http://localhost:8000"
            />
          </div>
          <div className="space-y-2">
            <label className="text-sm font-medium">Organization ID (X-Org-Id)</label>
            <Input 
              value={orgId} 
              onChange={(e) => setOrgId(e.target.value)} 
              placeholder="00000000-0000-0000-0000-000000000000"
            />
          </div>
          <Button onClick={handleSave} className="w-full">
            {isSaved ? 'Saved!' : 'Save Configuration'}
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}
