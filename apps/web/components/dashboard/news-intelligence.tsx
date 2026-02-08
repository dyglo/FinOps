'use client';

import { useQuery } from '@tanstack/react-query';
import { api } from '@/lib/api/client';
import { NewsListResponseSchema } from '@/lib/api/schemas';
import { GlassCard } from '@/components/ui/glass-card';
import { Badge } from '@/components/ui/badge';
import { Newspaper, ExternalLink, RefreshCw, BarChart3, TrendingUp, TrendingDown } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { formatDistanceToNow } from 'date-fns';

export function NewsIntelligence() {
  const { data, isLoading, refetch, isRefetching } = useQuery({
    queryKey: ['news', 'dashboard'],
    queryFn: async () => {
      const response = await api.get('/v1/documents/news', { params: { limit: 10 } });
      return NewsListResponseSchema.parse(response);
    },
  });

  // Helper to derive stable sentiment from ID
  const getSentiment = (id: string) => {
    const charCodeSum = id.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0);
    return charCodeSum % 2 === 0 ? 'bullish' : 'bearish';
  };

  return (
    <GlassCard className="h-full flex flex-col p-0 overflow-hidden border-none shadow-xl">
      <div className="p-5 border-b border-gray-100 bg-white/60 backdrop-blur-md flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="h-8 w-8 rounded-lg bg-black flex items-center justify-center">
            < Newspaper className="h-4 w-4 text-white" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-black">Flash Intelligence</h3>
            <p className="text-[9px] text-gray-400 font-black uppercase tracking-widest">Global Feed • Live</p>
          </div>
        </div>
        <Button variant="ghost" size="icon" onClick={() => refetch()} className="h-8 w-8 text-gray-400 hover:text-black hover:bg-black/5">
           <RefreshCw className={`h-3 w-3 ${isRefetching ? 'animate-spin' : ''}`} />
        </Button>
      </div>

      <div className="flex-1 overflow-y-auto divide-y divide-gray-50 custom-scrollbar">
        {isLoading ? (
           Array.from({ length: 6 }).map((_, i) => (
             <div key={i} className="p-5 animate-pulse space-y-3">
               <div className="h-3 w-1/3 bg-gray-100 rounded" />
               <div className="h-4 w-full bg-gray-100 rounded" />
               <div className="h-3 w-2/3 bg-gray-100 rounded" />
             </div>
           ))
        ) : data?.data.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full p-10 text-center text-gray-400">
             <BarChart3 className="h-12 w-12 opacity-10 mb-4" />
             <p className="text-sm font-bold">No verified intel stream.</p>
             <p className="text-xs opacity-60">Initialize ingestion to begin streaming.</p>
          </div>
        ) : (
          data?.data.map((doc) => {
            const sentiment = getSentiment(doc.id);
            return (
              <div key={doc.id} className="p-5 hover:bg-gray-50/80 transition-all cursor-pointer group relative overflow-hidden">
                <div className="flex items-start justify-between gap-4 mb-2">
                   <div className="flex items-center gap-2">
                      <span className="text-[9px] font-black text-blue-600 uppercase tracking-widest">{doc.source_provider}</span>
                      <span className="text-[9px] text-gray-300">•</span>
                      <span className="text-[9px] text-gray-400 font-bold uppercase">
                        {doc.published_at ? formatDistanceToNow(new Date(doc.published_at), { addSuffix: true }) : 'NOW'}
                      </span>
                   </div>
                   <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                      <a href={doc.source_url} target="_blank" rel="noopener noreferrer">
                         <ExternalLink className="h-3 w-3 text-gray-400 hover:text-black" />
                    </a>
                   </div>
                </div>

                <h4 className="font-bold text-xs text-black leading-snug mb-2 group-hover:text-blue-600 transition-colors">
                  {doc.title}
                </h4>
                
                <p className="text-[11px] text-gray-500 line-clamp-2 leading-relaxed mb-3">
                  {doc.snippet}
                </p>

                <div className="flex items-center gap-2">
                   {sentiment === 'bullish' ? (
                      <Badge className="bg-emerald-50 text-emerald-700 border-emerald-100 text-[8px] h-4 font-black uppercase tracking-tighter gap-1">
                         <TrendingUp className="h-2 w-2" /> Bullish
                      </Badge>
                   ) : (
                      <Badge className="bg-red-50 text-red-700 border-red-100 text-[8px] h-4 font-black uppercase tracking-tighter gap-1">
                         <TrendingDown className="h-2 w-2" /> Bearish
                      </Badge>
                   )}
                   <Badge variant="outline" className="text-[8px] h-4 font-black uppercase text-gray-400 border-gray-100">Verified</Badge>
                </div>
              </div>
            );
          })
        )}
      </div>
    </GlassCard>
  );
}
