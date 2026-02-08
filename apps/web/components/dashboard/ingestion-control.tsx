'use client';

import { useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { api } from '@/lib/api/client';
import { IngestionJobResponseSchema } from '@/lib/api/schemas';
import { GlassCard } from '@/components/ui/glass-card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Database, Loader2, Play, CheckCircle2, AlertCircle } from 'lucide-react';

export function IngestionControl() {
  const [query, setQuery] = useState('');
  const [activeJobId, setActiveJobId] = useState<string | null>(null);
  const queryClient = useQueryClient();

  const mutation = useMutation({
    mutationFn: async (searchQuery: string) => {
      const payload = {
        provider: 'tavily',
        resource: 'news_search',
        idempotency_key: crypto.randomUUID(),
        payload: { query: searchQuery, max_results: 10 },
      };
      const response = await api.post('/v1/ingestion/jobs', payload);
      return IngestionJobResponseSchema.parse(response);
    },
    onSuccess: (data) => {
      setActiveJobId(data.data.id);
      setQuery('');
    },
  });

  const { data: job } = useQuery({
    queryKey: ['ingestion', 'job', activeJobId],
    queryFn: async () => {
      const response = await api.get(`/v1/ingestion/jobs/${activeJobId}`);
      return IngestionJobResponseSchema.parse(response);
    },
    enabled: !!activeJobId,
    refetchInterval: (query) => {
      const status = query.state.data?.data.status;
      if (status === 'completed' || status === 'failed') {
          // Invalidate news query to show fresh results
          queryClient.invalidateQueries({ queryKey: ['news'] });
          return false;
      }
      return 2000;
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) {
      mutation.mutate(query);
    }
  };

  return (
    <GlassCard variant="highlight" className="p-8">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 mb-6">
        <div className="flex items-center gap-3">
          <div className="h-10 w-10 rounded-full bg-emerald-100 flex items-center justify-center border border-emerald-200">
            <Database className="h-5 w-5 text-emerald-700" />
          </div>
          <div>
            <h3 className="text-lg font-bold text-emerald-950">Ingestion Control</h3>
            <p className="text-xs text-emerald-700/60 font-bold uppercase tracking-widest">Data Pipeline</p>
          </div>
        </div>
        
        {job && (
          <div className="flex items-center gap-3 bg-white/50 px-4 py-2 rounded-full border border-emerald-100/50">
             <span className="text-xs font-bold text-emerald-900">Job Status:</span>
             <Badge variant={
                job.data.status === 'completed' ? 'success' : 
                job.data.status === 'failed' ? 'destructive' : 'secondary'
             } className="capitalize flex items-center gap-1.5">
                {job.data.status === 'processing' && <Loader2 className="h-3 w-3 animate-spin" />}
                {job.data.status === 'completed' && <CheckCircle2 className="h-3 w-3" />}
                {job.data.status === 'failed' && <AlertCircle className="h-3 w-3" />}
                {job.data.status}
             </Badge>
             {job.data.normalized_record_count > 0 && (
                <span className="text-xs font-bold text-emerald-700 border-l border-emerald-200 pl-3">
                   {job.data.normalized_record_count} Records
                </span>
             )}
          </div>
        )}
      </div>

      <form onSubmit={handleSubmit} className="flex gap-3">
        <Input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="e.g. NVIDIA earnings report Q4 2025..."
          disabled={mutation.isPending}
          className="bg-white/80 border-emerald-200 focus-visible:ring-emerald-500 h-12 rounded-xl"
        />
        <Button 
          type="submit" 
          disabled={mutation.isPending || !query.trim()}
          className="bg-emerald-900 hover:bg-emerald-800 text-white btn-pill h-12 px-6"
        >
          {mutation.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : <Play className="h-4 w-4 fill-current" />}
          <span className="ml-2">Run Ingestion</span>
        </Button>
      </form>
    </GlassCard>
  );
}
