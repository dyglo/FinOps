'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { api } from '@/lib/api/client';
import { SystemContextResponseSchema } from '@/lib/api/schemas';
import { GlassCard } from '@/components/ui/glass-card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { getWebRuntimeConfig } from '@/lib/config';
import { Check, Loader2, Save, Server, Shield } from 'lucide-react';
import { Badge } from '@/components/ui/badge';

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

  const { data: health, refetch: refetchHealth, isFetching: isHealthChecking, isError } = useQuery({
    queryKey: ['system', 'context', apiUrl, orgId],
    queryFn: async () => {
       const response = await api.get('/v1/system/context', { orgId, params: {} });
       return SystemContextResponseSchema.parse(response);
    },
    enabled: false,
    retry: false
  });

  const handleSave = () => {
    localStorage.setItem('finops_api_url', apiUrl);
    localStorage.setItem('finops_org_id', orgId);
    setIsSaved(true);
    setTimeout(() => setIsSaved(false), 2000);
  };

  return (
    <div className="flex flex-col gap-12 py-10">
      <div className="space-y-4 text-center max-w-2xl mx-auto">
        <h1 className="text-5xl font-bold text-black dark:text-white tracking-tight transition-colors">System Configuration</h1>
        <p className="text-lg text-gray-500 dark:text-zinc-400 transition-colors">
          Manage your connection to the FinOps Intelligence Core.
        </p>
      </div>

      <div className="grid md:grid-cols-2 gap-8 max-w-5xl mx-auto w-full">
         <GlassCard className="space-y-8 p-10 border-none shadow-xl">
            <div className="flex items-center gap-4 mb-2">
               <div className="h-12 w-12 rounded-full bg-black dark:bg-zinc-800 flex items-center justify-center border border-white/10">
                  <Server className="h-6 w-6 text-white" />
               </div>
               <div>
                  <h2 className="text-xl font-bold text-black dark:text-white transition-colors">API Connection</h2>
                  <p className="text-xs text-gray-400 dark:text-zinc-600 font-black uppercase tracking-widest transition-colors">Base Endpoint</p>
               </div>
            </div>
            
            <div className="space-y-4">
              <label className="text-[10px] font-black text-black dark:text-zinc-500 uppercase tracking-[0.2em] ml-1 transition-colors">Core API URL</label>
              <Input 
                value={apiUrl} 
                onChange={(e) => setApiUrl(e.target.value)} 
                placeholder="http://localhost:8000"
                className="bg-white/50 dark:bg-black/40 border-gray-200 dark:border-zinc-800 h-12 rounded-xl text-black dark:text-white transition-colors"
              />
              <p className="text-xs text-gray-400 dark:text-zinc-600 px-1 transition-colors">
                The HTTP/HTTPS endpoint where the `api-core` container is reachable.
              </p>
            </div>

            <Button onClick={handleSave} className="w-full bg-black dark:bg-white text-white dark:text-black hover:bg-zinc-800 dark:hover:bg-zinc-200 btn-pill h-12 gap-2 transition-all">
              {isSaved ? <Check className="h-4 w-4" /> : <Save className="h-4 w-4" />}
              {isSaved ? 'Configuration Saved' : 'Save Changes'}
            </Button>
         </GlassCard>

         <GlassCard className="space-y-8 p-10 border-none shadow-xl">
            <div className="flex items-center gap-4 mb-2">
               <div className="h-12 w-12 rounded-full bg-emerald-100 dark:bg-emerald-900/30 flex items-center justify-center border border-emerald-200 dark:border-emerald-900/50">
                  <Shield className="h-6 w-6 text-emerald-700 dark:text-emerald-400" />
               </div>
               <div>
                  <h2 className="text-xl font-bold text-black dark:text-white transition-colors">Tenant Identity</h2>
                  <p className="text-xs text-gray-400 dark:text-zinc-600 font-black uppercase tracking-widest transition-colors">Security Context</p>
               </div>
            </div>

            <div className="space-y-4">
              <label className="text-[10px] font-black text-black dark:text-zinc-500 uppercase tracking-[0.2em] ml-1 transition-colors">Organization ID (UUID)</label>
              <Input 
                value={orgId} 
                onChange={(e) => setOrgId(e.target.value)} 
                placeholder="00000000-0000-0000-0000-000000000000"
                className="bg-white/50 dark:bg-black/40 border-gray-200 dark:border-zinc-800 h-12 rounded-xl font-mono text-sm text-black dark:text-white transition-colors"
              />
               <p className="text-xs text-gray-400 dark:text-zinc-600 px-1 transition-colors">
                This ID is sent in the `X-Org-Id` header for data isolation.
              </p>
            </div>

             <div className="pt-2">
               <div className="flex items-center justify-between p-4 rounded-xl bg-gray-50 dark:bg-zinc-900/50 border border-gray-100 dark:border-zinc-800 transition-colors">
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-bold text-gray-500 dark:text-zinc-600 transition-colors">Status:</span>
                    {health ? (
                       <Badge variant="success" className="bg-emerald-100 dark:bg-emerald-900/30 text-emerald-800 dark:text-emerald-400 border-emerald-200 dark:border-emerald-900/50 border-none transition-colors">Online</Badge>
                    ) : isError ? (
                       <Badge variant="warning" className="bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-400 border-red-200 dark:border-red-900/50 border-none transition-colors">Unreachable</Badge>
                    ) : (
                       <Badge variant="secondary" className="bg-gray-200 dark:bg-zinc-800 text-gray-600 dark:text-zinc-400 border-none transition-colors">Unknown</Badge>
                    )}
                  </div>
                  <Button 
                    variant="ghost" 
                    size="sm" 
                    onClick={() => refetchHealth()}
                    disabled={isHealthChecking}
                    className="text-[10px] font-black uppercase tracking-[0.2em] text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300 hover:bg-blue-50 dark:hover:bg-blue-900/20 transition-colors"
                  >
                    {isHealthChecking ? <Loader2 className="h-3 w-3 animate-spin mr-1" /> : null}
                    Test Continuity
                  </Button>
               </div>
             </div>
         </GlassCard>
      </div>
    </div>
  );
}
