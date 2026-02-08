'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { api } from '@/lib/api/client';
import { NewsListResponseSchema } from '@/lib/api/schemas';
import { GlassCard } from '@/components/ui/glass-card';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { 
  Search, 
  Filter, 
  ExternalLink, 
  Calendar, 
  User, 
  Newspaper, 
  ChevronRight,
  TrendingUp,
  TrendingDown,
  Globe,
  Hash,
  Clock,
  LayoutList,
  Columns
} from 'lucide-react';
import { format } from 'date-fns';

export default function NewsPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedDocId, setSelectedDocId] = useState<string | null>(null);
  const [viewMode, setViewMode] = useState<'list' | 'grid'>('list');

  const { data, isLoading, isFetching } = useQuery({
    queryKey: ['news', 'terminal', searchQuery],
    queryFn: async () => {
      const response = await api.get('/v1/documents/news', { 
        params: { 
          limit: 50,
          q: searchQuery || undefined
        } 
      });
      return NewsListResponseSchema.parse(response);
    },
  });

  const selectedDoc = data?.data.find(d => d.id === selectedDocId);

  // Stable sentiment helper
  const getSentiment = (id: string) => {
    const charCodeSum = id.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0);
    return charCodeSum % 2 === 0 ? 'bullish' : 'bearish';
  };

  return (
    <div className="flex flex-col h-[calc(100vh-100px)] gap-4 py-4">
      {/* TERMINAL HEADER */}
      <div className="flex items-center justify-between px-2">
        <div className="flex items-center gap-4">
           <div className="h-10 w-10 rounded-xl bg-black dark:bg-zinc-900 flex items-center justify-center shadow-lg border border-white/10">
              <Newspaper className="h-5 w-5 text-white" />
           </div>
           <div>
              <h1 className="text-xl font-bold text-black dark:text-white tracking-tight">Intelligence Terminal</h1>
              <div className="flex items-center gap-2">
                 <Badge variant="outline" className="text-[8px] h-4 px-1.5 font-black uppercase text-blue-600 dark:text-blue-400 border-blue-100 dark:border-blue-900/50 bg-blue-50/50 dark:bg-blue-900/20">Verified Stream</Badge>
                 <span className="text-[10px] text-gray-400 dark:text-zinc-500 font-bold uppercase tracking-widest">{data?.data.length || 0} Objects Loaded</span>
              </div>
           </div>
        </div>

        <div className="flex items-center gap-2">
           <div className="relative w-80">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400 dark:text-zinc-500" />
              <Input 
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Query global signals..." 
                className="pl-10 h-10 border-none bg-white/40 dark:bg-zinc-900/40 glass-card shadow-sm rounded-xl focus-visible:ring-black dark:focus-visible:ring-white"
              />
           </div>
           <Button variant="outline" className="h-10 px-4 gap-2 text-xs font-bold uppercase tracking-wider border-none glass-card bg-white/40 dark:bg-zinc-900/40 hover:bg-white dark:hover:bg-zinc-800 transition-all text-gray-600 dark:text-zinc-400">
              <Filter className="h-4 w-4" />
              <span>Refine</span>
           </Button>
           <div className="h-10 border-l border-gray-100 dark:border-zinc-800 mx-2" />
           <div className="flex items-center bg-gray-100/50 dark:bg-zinc-900/50 rounded-xl p-1">
              <Button 
                variant="ghost" 
                size="icon" 
                onClick={() => setViewMode('list')}
                className={`h-8 w-8 rounded-lg ${viewMode === 'list' ? 'bg-white dark:bg-zinc-800 shadow-sm text-black dark:text-white' : 'text-gray-400 dark:text-zinc-600'}`}
              >
                 <LayoutList className="h-4 w-4" />
              </Button>
              <Button 
                variant="ghost" 
                size="icon" 
                onClick={() => setViewMode('grid')}
                className={`h-8 w-8 rounded-lg ${viewMode === 'grid' ? 'bg-white dark:bg-zinc-800 shadow-sm text-black dark:text-white' : 'text-gray-400 dark:text-zinc-600'}`}
              >
                 <Columns className="h-4 w-4" />
              </Button>
           </div>
        </div>
      </div>

      {/* MULTI-PANE WORKSPACE */}
      <div className="flex-1 flex gap-6 overflow-hidden min-h-0">
        
        {/* Left: Documents Ledger */}
        <div className="flex-1 flex flex-col gap-4 overflow-hidden">
           <GlassCard className="p-0 flex-1 flex flex-col overflow-hidden border-none shadow-xl">
              <div className="p-4 border-b border-[var(--line-soft)] bg-[var(--surface-1)]/60 backdrop-blur-md flex items-center justify-between">
                 <div className="flex items-center gap-2">
                    <Hash className="h-4 w-4 text-gray-400 dark:text-zinc-500" />
                    <span className="text-xs font-bold text-black dark:text-white uppercase tracking-widest">Master Signals Ledger</span>
                 </div>
                 {isFetching && <div className="h-1.5 w-1.5 rounded-full bg-blue-500 animate-pulse" />}
              </div>
              
              <div className="flex-1 overflow-y-auto divide-y divide-[var(--line-soft)] custom-scrollbar">
                 {isLoading ? (
                    Array.from({ length: 12 }).map((_, i) => (
                       <div key={i} className="p-4 animate-pulse flex gap-4">
                          <div className="h-8 w-8 rounded bg-[var(--surface-2)]" />
                          <div className="flex-1 space-y-2">
                             <div className="h-3 w-1/4 bg-[var(--surface-2)] rounded" />
                             <div className="h-4 w-full bg-[var(--surface-2)] rounded" />
                          </div>
                       </div>
                    ))
                 ) : data?.data.length === 0 ? (
                    <div className="flex flex-col items-center justify-center h-full p-20 opacity-20 dark:opacity-10 text-[var(--text-strong)]">
                       <Globe className="h-20 w-20 mb-4" />
                       <p className="font-black uppercase tracking-widest">No matching signals</p>
                    </div>
                 ) : (
                    data?.data.map((doc) => {
                       const sentiment = getSentiment(doc.id);
                       const active = selectedDocId === doc.id;
                       return (
                          <div 
                            key={doc.id}
                            onClick={() => setSelectedDocId(doc.id)}
                            className={`
                              p-4 flex items-start gap-4 cursor-pointer transition-all relative
                              ${active ? 'bg-blue-50/50 dark:bg-blue-950/20 shadow-inner border-l-4 border-blue-500' : 'hover:bg-[var(--surface-0)]'}
                            `}
                          >
                             <div className={`h-8 w-8 rounded-lg flex items-center justify-center border font-bold text-[10px] uppercase
                                ${sentiment === 'bullish' ? 'bg-emerald-50 dark:bg-emerald-900/30 border-emerald-100 dark:border-emerald-900/50 text-emerald-700 dark:text-emerald-400' : 'bg-red-50 dark:bg-red-900/30 border-red-100 dark:border-red-900/50 text-red-700 dark:text-red-400'}
                             `}>
                                {doc.source_provider.slice(0, 2)}
                             </div>
                             <div className="flex-1 min-w-0">
                                <div className="flex items-center justify-between mb-1">
                                   <div className="flex items-center gap-2">
                                      <span className="text-[10px] font-black text-gray-400 dark:text-zinc-500 uppercase tracking-tighter">{doc.source_provider}</span>
                                      <span className="text-[10px] text-gray-200 dark:text-zinc-800">•</span>
                                      <span className="text-[10px] font-bold text-gray-400 dark:text-zinc-500">
                                         {doc.published_at ? format(new Date(doc.published_at), 'HH:mm:ss') : '--:--:--'}
                                      </span>
                                   </div>
                                   {active && <Badge className="text-[8px] h-4 bg-blue-500 text-white border-none uppercase tracking-tighter">Active</Badge>}
                                </div>
                                <h3 className={`font-bold text-xs leading-snug mb-1 truncate ${active ? 'text-blue-900 dark:text-blue-400' : 'text-black dark:text-zinc-100'}`}>
                                   {doc.title}
                                </h3>
                                <div className="flex items-center gap-4">
                                   <div className="flex items-center gap-1">
                                      {sentiment === 'bullish' ? <TrendingUp className="h-3 w-3 text-emerald-500" /> : <TrendingDown className="h-3 w-3 text-red-500" />}
                                      <span className={`text-[10px] font-black uppercase ${sentiment === 'bullish' ? 'text-emerald-600 dark:text-emerald-400' : 'text-red-600 dark:text-red-400'}`}>{sentiment}</span>
                                   </div>
                                   <span className="text-[10px] font-bold text-gray-300 dark:text-zinc-700 uppercase tracking-widest font-mono">ID: {doc.id.slice(0, 8)}</span>
                                </div>
                             </div>
                             <ChevronRight className={`h-4 w-4 mt-4 transition-all ${active ? 'text-blue-500 translate-x-1' : 'text-gray-200 dark:text-zinc-800 group-hover:text-gray-400'}`} />
                          </div>
                       )
                    })
                 )}
              </div>
              <div className="p-3 bg-[var(--surface-0)] border-t border-[var(--line-soft)] flex items-center justify-between px-6">
                 <span className="text-[10px] font-bold text-gray-400 dark:text-zinc-600 uppercase tracking-widest italic font-mono text-[9px]">Terminal Ready • No Latency Detected</span>
                 <div className="flex items-center gap-2">
                    <span className="text-[10px] font-bold text-gray-400 dark:text-zinc-600 font-mono">Page 1 of 1</span>
                 </div>
              </div>
           </GlassCard>
        </div>

        {/* Right: Intelligence Inspector */}
        <div className={`
           w-[500px] flex flex-col gap-4 transition-all duration-500
           ${selectedDocId ? 'translate-x-0 opacity-100' : 'translate-x-20 opacity-0 hidden lg:flex'}
        `}>
           {selectedDoc ? (
              <GlassCard className="flex-1 flex flex-col p-0 overflow-hidden border-none shadow-2xl relative">
                 <div className="p-6 border-b border-[var(--line-soft)] bg-[var(--surface-1)]/80 backdrop-blur-md">
                    <div className="flex items-center justify-between mb-4">
                       <Badge variant="secondary" className="bg-black dark:bg-white text-white dark:text-black text-[9px] h-5 font-black uppercase tracking-widest px-2">Inspector v1</Badge>
                       <Button variant="ghost" size="icon" onClick={() => setSelectedDocId(null)} className="h-6 w-6 text-gray-400 dark:text-zinc-600 hover:text-black dark:hover:text-white">
                          <ChevronRight className="h-4 w-4 rotate-180" />
                       </Button>
                    </div>
                    <h2 className="text-xl font-bold text-black dark:text-white leading-tight mb-4 tracking-tight">
                       {selectedDoc.title}
                    </h2>
                    <div className="flex items-center gap-4">
                       <div className="flex flex-col">
                          <span className="text-[9px] font-black text-gray-300 dark:text-zinc-600 uppercase tracking-widest">Origin</span>
                          <span className="text-xs font-bold text-blue-600 dark:text-blue-400 uppercase tracking-tighter">{selectedDoc.source_provider}</span>
                       </div>
                       <div className="h-6 border-l border-[var(--line-soft)]" />
                       <div className="flex flex-col">
                          <span className="text-[9px] font-black text-gray-300 dark:text-zinc-600 uppercase tracking-widest">Timestamp</span>
                          <span className="text-xs font-bold text-black dark:text-white">
                             {selectedDoc.published_at ? format(new Date(selectedDoc.published_at), 'MMM d, yyyy HH:mm') : 'N/A'}
                          </span>
                       </div>
                    </div>
                 </div>

                 <div className="flex-1 p-8 overflow-y-auto space-y-8 custom-scrollbar">
                    <div className="space-y-4">
                       <div className="flex items-center gap-2">
                          <div className="h-1 w-8 bg-black dark:bg-white rounded-full" />
                          <h3 className="text-[10px] font-black text-black dark:text-white uppercase tracking-[0.2em]">Verified Abstract</h3>
                       </div>
                       <p className="text-base text-gray-600 dark:text-zinc-400 leading-relaxed font-medium">
                          {selectedDoc.snippet}
                       </p>
                    </div>

                    <div className="space-y-4">
                       <div className="flex items-center gap-2">
                          <div className="h-1 w-8 bg-blue-500 rounded-full" />
                          <h3 className="text-[10px] font-black text-blue-500 uppercase tracking-[0.2em]">Source Context</h3>
                       </div>
                       <div className="p-5 rounded-2xl bg-[var(--surface-0)] border border-[var(--line-soft)] space-y-4">
                          <div className="flex items-center justify-between">
                             <div className="flex items-center gap-2">
                                <Clock className="h-3 w-3 text-gray-400 dark:text-zinc-600" />
                                <span className="text-xs font-bold text-gray-500 dark:text-zinc-400 uppercase tracking-tighter">Canonical URL</span>
                             </div>
                             <a href={selectedDoc.source_url} target="_blank" rel="noopener noreferrer">
                                <Button size="sm" variant="outline" className="h-7 text-[9px] font-black uppercase tracking-widest gap-2 bg-white dark:bg-zinc-900 rounded-lg border-[var(--line-soft)] text-[var(--text-strong)] hover:bg-gray-50 dark:hover:bg-zinc-800">
                                   Explore Original <ExternalLink className="h-3 w-3" />
                                </Button>
                             </a>
                          </div>
                          <div className="text-[10px] font-mono text-gray-400 dark:text-zinc-600 break-all leading-relaxed bg-[var(--surface-1)]/50 p-3 rounded-xl border border-[var(--line-soft)]">
                             {selectedDoc.source_url}
                          </div>
                       </div>
                    </div>

                    <div className="space-y-4">
                       <div className="flex items-center gap-2">
                          <div className="h-1 w-8 bg-purple-500 rounded-full" />
                          <h3 className="text-[10px] font-black text-purple-500 uppercase tracking-[0.2em]">Normalization Metadata</h3>
                       </div>
                       <div className="grid grid-cols-2 gap-3">
                          <MetaItem label="Author" value={selectedDoc.author || 'System'} />
                          <MetaItem label="Language" value={selectedDoc.language || 'EN'} />
                          <MetaItem label="Version" value="2.0-vN" />
                          <MetaItem label="Hash" value={selectedDoc.id.slice(0, 12)} />
                       </div>
                    </div>
                 </div>
              </GlassCard>
           ) : (
              <div className="h-full flex flex-col items-center justify-center text-center p-12 opacity-30 dark:opacity-10">
                 <div className="h-24 w-24 rounded-full border-2 border-dashed border-gray-300 flex items-center justify-center mb-6">
                    <Search className="h-10 w-10 text-gray-400" />
                 </div>
                 <h3 className="text-lg font-black text-gray-400 uppercase tracking-widest text-[var(--text-strong)]">Inspector Idle</h3>
                 <p className="text-sm font-bold text-gray-400 mt-2 text-[var(--text-muted)]">Selection required for deep-dive analysis</p>
              </div>
           )}
        </div>
      </div>
    </div>
  );
}

function MetaItem({ label, value }: { label: string, value: string }) {
  return (
    <div className="p-3 rounded-xl bg-[var(--surface-1)]/50 border border-[var(--line-soft)]">
       <span className="block text-[8px] font-black text-gray-300 dark:text-zinc-700 uppercase tracking-widest mb-1">{label}</span>
       <span className="block text-xs font-bold text-black dark:text-white truncate uppercase tracking-tighter">{value}</span>
    </div>
  )
}
