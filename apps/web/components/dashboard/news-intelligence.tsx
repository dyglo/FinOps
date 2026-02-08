'use client';

import { useQuery } from '@tanstack/react-query';
import { api } from '@/lib/api/client';
import { NewsListResponseSchema } from '@/lib/api/schemas';
import { GlassCard } from '@/components/ui/glass-card';
import { Badge } from '@/components/ui/badge';
import { Newspaper, ExternalLink, RefreshCw } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { formatDistanceToNow } from 'date-fns';
import Image from 'next/image';

export function NewsIntelligence() {
  const { data, isLoading, refetch, isRefetching } = useQuery({
    queryKey: ['news', 'dashboard'],
    queryFn: async () => {
      const response = await api.get('/v1/documents/news', { params: { limit: 5 } });
      return NewsListResponseSchema.parse(response);
    },
  });

  return (
    <GlassCard className="h-full flex flex-col p-8">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className="h-10 w-10 rounded-full bg-purple-100 flex items-center justify-center">
            <Newspaper className="h-5 w-5 text-purple-600" />
          </div>
          <div>
            <h3 className="text-lg font-bold text-black">News Intelligence</h3>
            <p className="text-xs text-gray-400 font-bold uppercase tracking-widest">Latest Signals</p>
          </div>
        </div>
        <Button variant="ghost" size="icon" onClick={() => refetch()} className="h-8 w-8 text-gray-400 hover:text-black">
           <RefreshCw className={`h-4 w-4 ${isRefetching ? 'animate-spin' : ''}`} />
        </Button>
      </div>

      <div className="flex-1 space-y-4 overflow-y-auto pr-2 custom-scrollbar">
        {isLoading ? (
           Array.from({ length: 3 }).map((_, i) => (
             <div key={i} className="animate-pulse flex gap-4 p-4 rounded-2xl bg-white/40 border border-white/50">
               <div className="h-10 w-10 rounded-full bg-gray-200" />
               <div className="flex-1 space-y-2">
                 <div className="h-4 w-3/4 bg-gray-200 rounded" />
                 <div className="h-3 w-full bg-gray-200 rounded" />
               </div>
             </div>
           ))
        ) : data?.data.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-40 text-gray-400 text-sm">
             <p>No intelligence found.</p>
             <p className="text-xs opacity-60">Run an ingestion job to populate.</p>
          </div>
        ) : (
          data?.data.map((doc) => (
            <div key={doc.id} className="group relative flex gap-4 p-4 rounded-2xl bg-white/40 border border-white/50 hover:bg-white/80 transition-all">
              <div className="flex-shrink-0">
                 <div className="h-10 w-10 rounded-full bg-gray-100 flex items-center justify-center border border-white overflow-hidden">
                    {/* Placeholder or provider logo */}
                    <span className="text-xs font-bold uppercase text-gray-500">{doc.source_provider.slice(0, 2)}</span>
                 </div>
              </div>
              <div className="flex-1 min-w-0">
                 <div className="flex items-center justify-between gap-2 mb-1">
                    <h4 className="font-bold text-sm text-black truncate">{doc.title}</h4>
                    <span className="text-[10px] text-gray-400 whitespace-nowrap">
                      {doc.published_at ? formatDistanceToNow(new Date(doc.published_at), { addSuffix: true }) : 'Just now'}
                    </span>
                 </div>
                 <p className="text-xs text-gray-500 line-clamp-2 leading-relaxed mb-2">
                    {doc.snippet}
                 </p>
                 <div className="flex items-center justify-between">
                    <Badge variant="secondary" className="bg-white text-gray-600 text-[10px] px-2 py-0.5 border border-gray-100">
                       {doc.source_provider}
                    </Badge>
                    <a href={doc.source_url} target="_blank" rel="noopener noreferrer" className="opacity-0 group-hover:opacity-100 transition-opacity">
                       <ExternalLink className="h-3 w-3 text-gray-400 hover:text-blue-500" />
                    </a>
                 </div>
              </div>
            </div>
          ))
        )}
      </div>
    </GlassCard>
  );
}
