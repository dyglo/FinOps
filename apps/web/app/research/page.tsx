'use client';

import { useState } from 'react';
import { useMutation, useQuery } from '@tanstack/react-query';
import { api } from '@/lib/api/client';
import { IntelRunResponseSchema } from '@/lib/api/schemas';
import { GlassCard } from '@/components/ui/glass-card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Bot, Sparkles, Clock, ArrowRight, Loader2, FileText } from 'lucide-react';

export default function ResearchPage() {
  const [topic, setTopic] = useState('');
  
  const mutation = useMutation({
    mutationFn: async () => {
       const payload = {
          run_type: 'research_memo',
          model_name: 'gpt-4-turbo',
          prompt_version: 'v1',
          input_snapshot_uri: 's3://mock-bucket/snapshot.json',
          input_payload: { topic, timeframe: '1w' },
       };
       const response = await api.post('/v1/intel/runs', payload);
       return IntelRunResponseSchema.parse(response);
    }
  });

  // Mock previous runs for UI demonstration if no real runs exist yet
  const previousRuns = [
    { id: '1', topic: 'NVIDIA AI Chip Demand', status: 'completed', date: '2h ago' },
    { id: '2', topic: 'Oil Price Impact on Airlines', status: 'failed', date: '5h ago' },
    { id: '3', topic: 'Crypto Regulation 2026', status: 'processing', date: 'Just now' },
  ];

  return (
    <div className="flex flex-col gap-12 py-8 pb-20">
      <div className="text-center max-w-2xl mx-auto space-y-4">
         <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-purple-50 border border-purple-100 text-purple-700 text-xs font-bold uppercase tracking-widest">
            <Sparkles className="h-3 w-3" /> Agentic Intelligence
         </div>
         <h1 className="text-5xl font-bold text-black tracking-tight">Research Lab</h1>
         <p className="text-lg text-gray-500">
            Deploy autonomous agents to synthesize market data into actionable memos.
         </p>
      </div>

      <div className="grid lg:grid-cols-3 gap-8 items-start">
         {/* Configuration Card */}
         <GlassCard className="lg:col-span-2 p-10 space-y-8 relative overflow-hidden">
            <div className="absolute top-0 right-0 w-64 h-64 bg-purple-200 rounded-full blur-3xl opacity-20 -translate-y-1/2 translate-x-1/3" />
            
            <div className="flex items-center gap-4">
               <div className="h-14 w-14 rounded-2xl bg-black flex items-center justify-center text-white shadow-xl shadow-purple-900/10">
                  <Bot className="h-7 w-7" />
               </div>
               <div>
                  <h2 className="text-2xl font-bold text-black">New Research Run</h2>
                  <p className="text-sm text-gray-400 font-bold uppercase tracking-widest">Configure Agent Parameters</p>
               </div>
            </div>

            <div className="space-y-6">
               <div className="space-y-2">
                  <label className="text-sm font-bold text-gray-700 ml-1">Research Topic</label>
                  <Input 
                    value={topic}
                    onChange={(e) => setTopic(e.target.value)}
                    placeholder="e.g. Impact of interest rate cuts on REITs..." 
                    className="h-14 text-lg bg-white/50 border-purple-100 focus-visible:ring-purple-500 rounded-2xl"
                  />
               </div>

               <div className="grid grid-cols-2 gap-4">
                  <div className="p-4 rounded-xl border border-gray-100 bg-white/30 cursor-pointer hover:bg-white/50 transition-colors ring-1 ring-black ring-offset-2">
                     <div className="text-xs text-gray-400 font-bold uppercase mb-1">Mode</div>
                     <div className="font-bold text-black">Deep Dive</div>
                  </div>
                  <div className="p-4 rounded-xl border border-gray-100 bg-white/30 cursor-pointer hover:bg-white/50 transition-colors">
                     <div className="text-xs text-gray-400 font-bold uppercase mb-1">Timeframe</div>
                     <div className="font-bold text-black">Last 30 Days</div>
                  </div>
               </div>

               <Button 
                 onClick={() => mutation.mutate()}
                 disabled={mutation.isPending || !topic}
                 className="w-full h-14 text-lg bg-black hover:bg-zinc-800 text-white btn-pill shadow-xl shadow-black/10"
               >
                  {mutation.isPending ? (
                     <>
                        <Loader2 className="h-5 w-5 animate-spin mr-2" /> Initializing Agent...
                     </>
                  ) : (
                     <>
                        Start Analysis <ArrowRight className="h-5 w-5 ml-2" />
                     </>
                  )}
               </Button>
            </div>
         </GlassCard>

         {/* Recent Runs List */}
         <div className="space-y-6">
            <div className="flex items-center justify-between px-2">
               <h3 className="font-bold text-gray-500 uppercase tracking-widest text-sm">Recent Runs</h3>
            </div>
            
            {previousRuns.map((run) => (
               <GlassCard key={run.id} className="p-5 flex items-center gap-4 cursor-pointer hover:bg-white/80 transition-colors group">
                  <div className={`
                     h-10 w-10 rounded-full flex items-center justify-center border
                     ${run.status === 'completed' ? 'bg-emerald-50 border-emerald-100 text-emerald-600' : ''}
                     ${run.status === 'processing' ? 'bg-blue-50 border-blue-100 text-blue-600' : ''}
                     ${run.status === 'failed' ? 'bg-red-50 border-red-100 text-red-600' : ''}
                  `}>
                     {run.status === 'processing' ? <Loader2 className="h-5 w-5 animate-spin" /> : <FileText className="h-5 w-5" />}
                  </div>
                  <div className="flex-1 min-w-0">
                     <h4 className="font-bold text-sm text-black truncate group-hover:text-purple-700 transition-colors">{run.topic}</h4>
                     <div className="flex items-center gap-2 text-xs text-gray-400 font-medium mt-0.5">
                        <Clock className="h-3 w-3" /> {run.date}
                     </div>
                  </div>
                  <Badge variant={
                     run.status === 'completed' ? 'success' :
                     run.status === 'processing' ? 'secondary' : 'destructive'
                  } className="capitalize text-[10px] px-2">
                     {run.status}
                  </Badge>
               </GlassCard>
            ))}

            <div className="p-8 rounded-[32px] border border-dashed border-gray-200 flex flex-col items-center justify-center text-center space-y-2 opacity-60">
               <Bot className="h-8 w-8 text-gray-300" />
               <p className="text-sm font-bold text-gray-400">Agent Idle</p>
               <p className="text-xs text-gray-400">Ready for new tasks</p>
            </div>
         </div>
      </div>
    </div>
  );
}
