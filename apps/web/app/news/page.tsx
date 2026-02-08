'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { api } from '@/lib/api/client';
import { NewsListResponseSchema } from '@/lib/api/schemas';
import { GlassCard } from '@/components/ui/glass-card';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Search, Filter, ExternalLink, Calendar, User, Newspaper, ChevronRight } from 'lucide-react';
import { format } from 'date-fns';

export default function NewsPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedDocId, setSelectedDocId] = useState<string | null>(null);

  const { data, isLoading } = useQuery({
    queryKey: ['news', 'full', searchQuery],
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

  return (
    <div className="flex h-[calc(100vh-120px)] gap-6 py-6 pb-0">
      {/* Left Panel: List & Filters */}
      <div className="flex-1 flex flex-col gap-6 min-w-0">
        <div className="flex flex-col gap-2">
           <h1 className="text-4xl font-bold text-black tracking-tight">News Terminal</h1>
           <p className="text-gray-500">Global financial intelligence feed.</p>
        </div>

        <GlassCard className="p-4 flex gap-4 items-center">
           <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
              <Input 
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search headlines, tickers, or keywords..." 
                className="pl-10 h-10 border-gray-200 bg-white/50"
              />
           </div>
           <Button variant="outline" className="h-10 px-4 gap-2 text-gray-600 border-gray-200 bg-white/50">
              <Filter className="h-4 w-4" />
              <span>Filters</span>
           </Button>
        </GlassCard>

        <div className="flex-1 overflow-y-auto space-y-3 pr-2 custom-scrollbar pb-20">
           {isLoading ? (
             Array.from({ length: 8 }).map((_, i) => (
                <div key={i} className="h-24 rounded-2xl bg-gray-100 animate-pulse" />
             ))
           ) : data?.data.length === 0 ? (
             <div className="flex flex-col items-center justify-center h-64 text-gray-400">
                <Newspaper className="h-12 w-12 opacity-20 mb-4" />
                <p>No documents found matching your criteria.</p>
             </div>
           ) : (
             data?.data.map((doc) => (
                <div 
                  key={doc.id}
                  onClick={() => setSelectedDocId(doc.id)}
                  className={`
                    group p-5 rounded-2xl cursor-pointer transition-all border
                    ${selectedDocId === doc.id 
                      ? 'bg-white border-blue-200 shadow-lg ring-1 ring-blue-100' 
                      : 'bg-white/40 border-white/60 hover:bg-white hover:border-white hover:shadow-md'
                    }
                  `}
                >
                   <div className="flex justify-between items-start gap-4">
                      <div className="space-y-1">
                         <h3 className={`font-bold text-base leading-snug ${selectedDocId === doc.id ? 'text-blue-900' : 'text-black'}`}>
                           {doc.title}
                         </h3>
                         <div className="flex items-center gap-3 text-xs text-gray-400 font-medium">
                            <span className="flex items-center gap-1">
                               <Calendar className="h-3 w-3" />
                               {doc.published_at ? format(new Date(doc.published_at), 'MMM d, h:mm a') : 'Unknown Date'}
                            </span>
                            <span>•</span>
                            <span className="uppercase tracking-wider">{doc.source_provider}</span>
                         </div>
                      </div>
                      <ChevronRight className={`h-5 w-5 text-gray-300 transition-transform ${selectedDocId === doc.id ? 'rotate-90 text-blue-400' : 'group-hover:translate-x-1'}`} />
                   </div>
                   <p className="mt-3 text-sm text-gray-500 line-clamp-2 leading-relaxed opacity-90">
                      {doc.snippet}
                   </p>
                </div>
             ))
           )}
        </div>
      </div>

      {/* Right Panel: Details */}
      <div className={`
        w-[480px] flex-shrink-0 transition-all duration-500
        ${selectedDocId ? 'translate-x-0 opacity-100' : 'translate-x-20 opacity-0 hidden lg:block'}
      `}>
        {selectedDoc ? (
           <GlassCard className="h-full overflow-y-auto p-8 border-l border-white/60">
              <div className="space-y-6">
                 <div className="space-y-4 border-b border-gray-100 pb-6">
                    <Badge variant="secondary" className="uppercase tracking-widest text-[10px] px-2">
                       {selectedDoc.source_provider}
                    </Badge>
                    <h2 className="text-2xl font-bold text-black leading-tight">
                       {selectedDoc.title}
                    </h2>
                    <a 
                      href={selectedDoc.source_url} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-2 text-sm font-bold text-blue-600 hover:text-blue-700 hover:underline"
                    >
                       Read Original Source <ExternalLink className="h-4 w-4" />
                    </a>
                 </div>

                 <div className="space-y-4">
                    <h3 className="text-sm font-bold text-gray-400 uppercase tracking-widest">Summary Snippet</h3>
                    <p className="text-gray-700 leading-relaxed text-lg">
                       {selectedDoc.snippet}
                    </p>
                 </div>

                 <div className="space-y-4 pt-6">
                    <h3 className="text-sm font-bold text-gray-400 uppercase tracking-widest">Metadata</h3>
                    <div className="grid grid-cols-2 gap-4">
                       <div className="p-3 rounded-xl bg-gray-50 border border-gray-100">
                          <div className="text-xs text-gray-400 font-bold uppercase mb-1 flex items-center gap-1">
                             <User className="h-3 w-3" /> Author
                          </div>
                          <div className="text-sm font-bold text-gray-800 truncate">
                             {selectedDoc.author || 'N/A'}
                          </div>
                       </div>
                       <div className="p-3 rounded-xl bg-gray-50 border border-gray-100">
                          <div className="text-xs text-gray-400 font-bold uppercase mb-1">Language</div>
                          <div className="text-sm font-bold text-gray-800 uppercase">
                             {selectedDoc.language || 'EN'}
                          </div>
                       </div>
                       <div className="col-span-2 p-3 rounded-xl bg-gray-50 border border-gray-100">
                          <div className="text-xs text-gray-400 font-bold uppercase mb-1">Ingested At</div>
                          <div className="text-sm font-mono text-gray-600">
                             {selectedDoc.created_at}
                          </div>
                       </div>
                    </div>
                 </div>
              </div>
           </GlassCard>
        ) : (
           <div className="h-full flex flex-col items-center justify-center text-center p-8 opacity-40">
              <div className="h-32 w-32 rounded-full bg-gray-100 flex items-center justify-center mb-6">
                 <Newspaper className="h-12 w-12 text-gray-400" />
              </div>
              <h3 className="text-xl font-bold text-gray-400">Select an article</h3>
              <p className="text-gray-400 mt-2">View detailed analysis and metadata.</p>
           </div>
        )}
      </div>
    </div>
  );
}
