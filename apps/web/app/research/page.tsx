'use client';

import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { api } from '@/lib/api/client';
import { IntelRunResponseSchema } from '@/lib/api/schemas';
import { GlassCard } from '@/components/ui/glass-card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { 
  Bot, 
  Sparkles, 
  Clock, 
  ArrowRight, 
  Loader2, 
  Zap,
  Cpu,
  BrainCircuit,
  Settings2,
  ListFilter
} from 'lucide-react';
import { format } from 'date-fns';

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

  // Using static ISO strings to avoid purity errors during render
  const previousRuns = [
    { id: '1', topic: 'NVIDIA AI Chip Demand Analysis', status: 'completed', date: '2026-02-08T12:00:00Z', model: 'GPT-4T' },
    { id: '2', topic: 'Oil Price Impact on Airlines Q1', status: 'failed', date: '2026-02-08T11:00:00Z', model: 'GPT-4T' },
    { id: '3', topic: 'Crypto Regulation 2026 Forecast', status: 'processing', date: '2026-02-08T13:45:00Z', model: 'Claude 3' },
  ];

  return (
    <div className="flex flex-col h-[calc(100vh-100px)] gap-4 py-4">
      {/* TERMINAL HEADER */}
      <div className="flex items-center justify-between px-2">
        <div className="flex items-center gap-4">
           <div className="h-10 w-10 rounded-xl bg-black dark:bg-zinc-900 flex items-center justify-center shadow-lg border border-white/10">
              <BrainCircuit className="h-5 w-5 text-white" />
           </div>
           <div>
              <h1 className="text-xl font-bold text-black dark:text-white tracking-tight">Research Lab</h1>
              <div className="flex items-center gap-2">
                 <Badge className="text-[8px] h-4 px-1.5 font-black uppercase bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-400 border-purple-200 dark:border-purple-900/50">Agentic Engine Online</Badge>
                 <span className="text-[10px] text-gray-400 dark:text-zinc-500 font-bold uppercase tracking-widest">v1.2.0 (Alpha)</span>
              </div>
           </div>
        </div>

        <div className="flex items-center gap-2">
           <Button variant="outline" className="h-10 px-4 gap-2 text-xs font-bold uppercase tracking-wider border-none glass-card bg-white/40 dark:bg-zinc-900/40 hover:bg-white dark:hover:bg-zinc-800 transition-all text-gray-600 dark:text-zinc-400">
              <Settings2 className="h-4 w-4" />
              <span>Engine Config</span>
           </Button>
        </div>
      </div>

      <div className="flex-1 flex gap-6 overflow-hidden min-h-0">
         {/* Left: Research Configuration */}
         <div className="flex-1 flex flex-col gap-6 overflow-hidden">
            <GlassCard className="p-10 space-y-10 relative overflow-hidden border-none shadow-xl bg-white/60 dark:bg-zinc-900/60">
               <div className="absolute top-0 right-0 w-80 h-80 bg-purple-200 dark:bg-purple-900/20 rounded-full blur-[120px] opacity-20 -translate-y-1/2 translate-x-1/3" />
               
               <div className="flex items-center gap-6">
                  <div className="h-16 w-16 rounded-[24px] bg-black dark:bg-zinc-800 flex items-center justify-center text-white shadow-2xl shadow-purple-900/20 border border-white/10">
                     <Bot className="h-8 w-8" />
                  </div>
                  <div>
                     <h2 className="text-3xl font-bold text-black dark:text-white tracking-tighter">New Research Mission</h2>
                     <p className="text-xs text-gray-400 dark:text-zinc-500 font-black uppercase tracking-[0.2em]">Deployment Specification</p>
                  </div>
               </div>

               <div className="space-y-8 max-w-3xl">
                  <div className="space-y-4">
                     <div className="flex items-center justify-between px-1">
                        <label className="text-[10px] font-black text-black dark:text-white uppercase tracking-[0.2em]">Research Objective</label>
                        <Badge variant="secondary" className="bg-gray-100 dark:bg-zinc-800 text-gray-400 dark:text-zinc-500 text-[8px] font-black uppercase">Required</Badge>
                     </div>
                     <Input 
                        value={topic}
                        onChange={(e) => setTopic(e.target.value)}
                        placeholder="e.g. Synthesize macro impact of Fed rate cuts on Tech equity risk premiums..." 
                        className="h-16 text-xl bg-white/50 dark:bg-black/40 border-gray-100 dark:border-zinc-800 focus-visible:ring-black dark:focus-visible:ring-white rounded-[24px] px-6 shadow-sm font-medium text-black dark:text-white"
                     />
                     <div className="flex gap-4">
                        <Badge variant="outline" className="border-gray-100 dark:border-zinc-800 text-gray-400 dark:text-zinc-500 py-1 cursor-pointer hover:border-black dark:hover:border-white transition-colors">&quot;NVIDIA earnings Q4 2025&quot;</Badge>
                        <Badge variant="outline" className="border-gray-100 dark:border-zinc-800 text-gray-400 dark:text-zinc-500 py-1 cursor-pointer hover:border-black dark:hover:border-white transition-colors">&quot;Oil market volatility Q1&quot;</Badge>
                     </div>
                  </div>

                  <div className="grid grid-cols-3 gap-4">
                     <ConfigModule label="Model" value="GPT-4 Turbo" icon={<Cpu className="h-3.5 w-3.5" />} active />
                     <ConfigModule label="Depth" value="Level 4 (High)" icon={<ListFilter className="h-3.5 w-3.5" />} />
                     <ConfigModule label="Outputs" value="Full Memo" icon={<Zap className="h-3.5 w-3.5" />} />
                  </div>

                  <Button 
                    onClick={() => mutation.mutate()}
                    disabled={mutation.isPending || !topic}
                    className="w-full h-16 text-lg bg-black dark:bg-white hover:bg-zinc-800 dark:hover:bg-zinc-200 text-white dark:text-black rounded-[24px] shadow-2xl shadow-black/20 group transition-all"
                  >
                     {mutation.isPending ? (
                        <>
                           <Loader2 className="h-5 w-5 animate-spin mr-3" /> Initializing Neural Pathways...
                        </>
                     ) : (
                        <>
                           Initialize Research Mission <ArrowRight className="h-5 w-5 ml-3 group-hover:translate-x-1 transition-transform" />
                        </>
                     )}
                  </Button>
               </div>
            </GlassCard>
            
            <div className="p-8 rounded-[40px] border-2 border-dashed border-gray-100 dark:border-zinc-800 flex flex-col items-center justify-center text-center space-y-3 opacity-40">
               <Zap className="h-10 w-10 text-gray-300 dark:text-zinc-700" />
               <p className="text-sm font-black uppercase tracking-widest text-gray-400 dark:text-zinc-600">Real-time Memo Generation Surface</p>
               <p className="text-xs font-bold text-gray-300 dark:text-zinc-700">Start a mission to visualize agentic synthesis</p>
            </div>
         </div>

         {/* Right: Mission History Ledger */}
         <div className="w-[400px] flex flex-col gap-4 overflow-hidden">
            <GlassCard className="p-0 flex-1 flex flex-col overflow-hidden border-none shadow-xl">
               <div className="p-4 border-b border-[var(--line-soft)] bg-[var(--surface-1)]/60 backdrop-blur-md flex items-center justify-between">
                  <div className="flex items-center gap-2">
                     <Clock className="h-4 w-4 text-gray-400 dark:text-zinc-500" />
                     <span className="text-xs font-bold text-black dark:text-white uppercase tracking-widest">Mission Ledger</span>
                  </div>
                  <Badge variant="outline" className="text-[9px] border-gray-100 dark:border-zinc-800 font-bold uppercase text-gray-400 dark:text-zinc-500 px-2 h-5">History</Badge>
               </div>
               
               <div className="flex-1 overflow-y-auto divide-y divide-[var(--line-soft)] custom-scrollbar">
                  {previousRuns.map((run) => (
                     <div key={run.id} className="p-5 flex items-start gap-4 cursor-pointer hover:bg-[var(--surface-0)] transition-all group border-l-4 border-transparent hover:border-black dark:hover:border-white">
                        <div className={`
                           h-10 w-10 rounded-xl flex items-center justify-center border-2
                           ${run.status === 'completed' ? 'bg-emerald-50 dark:bg-emerald-900/30 border-emerald-100 dark:border-emerald-900/50 text-emerald-600 dark:text-emerald-400' : ''}
                           ${run.status === 'processing' ? 'bg-blue-50 dark:bg-blue-900/30 border-blue-100 dark:border-blue-900/50 text-blue-600 dark:text-blue-400' : ''}
                           ${run.status === 'failed' ? 'bg-red-50 dark:bg-red-900/30 border-red-100 dark:border-red-900/50 text-red-600 dark:text-red-400' : ''}
                        `}>
                           {run.status === 'processing' ? <Loader2 className="h-5 w-5 animate-spin" /> : <Zap className="h-5 w-5" />}
                        </div>
                        <div className="flex-1 min-w-0 space-y-1">
                           <h4 className="font-bold text-sm text-black dark:text-white truncate group-hover:text-blue-700 dark:group-hover:text-blue-400 transition-colors">{run.topic}</h4>
                           <div className="flex items-center gap-3 text-[10px] text-gray-400 dark:text-zinc-500 font-bold uppercase tracking-tighter font-mono">
                              <span className="text-gray-300 dark:text-zinc-700">{run.model}</span>
                              <span className="text-gray-200 dark:text-zinc-800">•</span>
                              <span>{format(new Date(run.date), 'MMM d, HH:mm')}</span>
                           </div>
                        </div>
                        <Badge variant={
                           run.status === 'completed' ? 'success' :
                           run.status === 'processing' ? 'secondary' : 'destructive'
                        } className="capitalize text-[9px] h-5 px-1.5 font-black border-none">
                           {run.status}
                        </Badge>
                     </div>
                  ))}
               </div>
            </GlassCard>
         </div>
      </div>
    </div>
  );
}

function ConfigModule({ label, value, icon, active }: any) {
  return (
    <div className={`
       p-4 rounded-[24px] border-2 transition-all cursor-pointer
       ${active ? 'bg-black dark:bg-white border-black dark:border-white text-white dark:text-black shadow-xl' : 'bg-white/40 dark:bg-zinc-900/40 border-gray-50 dark:border-zinc-800 text-black dark:text-white hover:border-gray-200 dark:hover:border-zinc-700'}
    `}>
       <div className="flex items-center gap-2 mb-2">
          <div className={`h-6 w-6 rounded-lg flex items-center justify-center ${active ? 'bg-white/20 dark:bg-black/10' : 'bg-black/5 dark:bg-white/5'}`}>
             {icon}
          </div>
          <span className={`text-[9px] font-black uppercase tracking-[0.2em] ${active ? 'text-white/60 dark:text-black/60' : 'text-gray-300 dark:text-zinc-600'}`}>{label}</span>
       </div>
       <div className="text-xs font-bold truncate">{value}</div>
    </div>
  )
}