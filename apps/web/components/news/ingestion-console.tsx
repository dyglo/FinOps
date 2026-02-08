'use client';

import { useState } from 'react';
import { useMutation, useQuery } from '@tanstack/react-query';
import { api } from '@/lib/api/client';
import { IngestionJobResponseSchema } from '@/lib/api/schemas';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Loader2, Play, RefreshCcw } from 'lucide-react';

export function IngestionConsole() {
  const [query, setQuery] = useState('NVIDIA earnings 2024');
  const [activeJobId, setActiveJobId] = useState<string | null>(null);

  const mutation = useMutation({
    mutationFn: async (searchQuery: string) => {
      const payload = {
        provider: 'tavily',
        resource: 'news_search',
        idempotency_key: crypto.randomUUID(),
        payload: { q: searchQuery },
      };
      const response = await api.post('/v1/ingestion/jobs', payload);
      return IngestionJobResponseSchema.parse(response);
    },
    onSuccess: (data) => {
      setActiveJobId(data.data.id);
    },
  });

  const { data: job, refetch } = useQuery({
    queryKey: ['ingestion-job', activeJobId],
    queryFn: async () => {
      const response = await api.get(`/v1/ingestion/jobs/${activeJobId}`);
      return IngestionJobResponseSchema.parse(response);
    },
    enabled: !!activeJobId,
    refetchInterval: (query) => {
      const status = query.state.data?.data.status;
      return status === 'completed' || status === 'failed' ? false : 3000;
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) {
      mutation.mutate(query);
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-xl font-bold">
          <Play className="h-5 w-5 text-emerald-500" />
          Data Ingestion
        </CardTitle>
        <CardDescription>Trigger news searches and track normalization status.</CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        <form onSubmit={handleSubmit} className="flex gap-2">
          <Input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Enter search query..."
            disabled={mutation.isPending}
            className="flex-1"
          />
          <Button type="submit" disabled={mutation.isPending}>
            {mutation.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : 'Run Ingestion'}
          </Button>
        </form>

        {job && (
          <div className="rounded-lg border border-[var(--line-soft)] bg-[var(--surface-0)] p-4 space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium">Job Status</span>
              <div className="flex items-center gap-2">
                {job.data.status !== 'completed' && job.data.status !== 'failed' && (
                   <Loader2 className="h-3 w-3 animate-spin text-[var(--text-muted)]" />
                )}
                <Badge 
                  variant={
                    job.data.status === 'completed' ? 'success' : 
                    job.data.status === 'failed' ? 'warning' : 'secondary'
                  }
                  className="capitalize"
                >
                  {job.data.status}
                </Badge>
              </div>
            </div>
            
            <div className="grid grid-cols-2 gap-4 text-[10px] uppercase tracking-wider text-[var(--text-muted)] font-bold">
              <div>
                <p>Raw Records</p>
                <p className="text-lg text-[var(--text-strong)] mt-1">{job.data.raw_record_count}</p>
              </div>
              <div>
                <p>Normalized</p>
                <p className="text-lg text-[var(--text-strong)] mt-1">{job.data.normalized_record_count}</p>
              </div>
            </div>

            {job.data.error_message && (
              <p className="text-xs text-red-500 bg-red-50 p-2 rounded border border-red-100">
                {job.data.error_message}
              </p>
            )}

            <div className="flex justify-between items-center pt-2">
              <span className="text-[10px] text-[var(--text-muted)]">ID: {job.data.id.slice(0, 8)}...</span>
              <Button size="sm" variant="ghost" onClick={() => refetch()} className="h-6 text-[10px]">
                <RefreshCcw className="h-3 w-3 mr-1" />
                Refresh
              </Button>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}