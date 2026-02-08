'use client';

import { NewsIntelligence } from '@/components/dashboard/news-intelligence';
import { IngestionControl } from '@/components/dashboard/ingestion-control';
import { GlassCard } from '@/components/ui/glass-card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { 
  Terminal, 
  ShieldCheck, 
  Zap,
  LayoutGrid,
  ListFilter,
  ArrowUpRight,
  ArrowDownRight,
  Search,
  Activity,
  Waves,
  Globe,
  PieChart
} from 'lucide-react';
import { Input } from '@/components/ui/input';

export default function DashboardPage() {
  return (
    <div className="flex flex-col gap-6 py-4 pb-20">
      {/* TERMINAL HEADER & COMMAND BAR */}
      <div className="flex flex-col md:flex-row items-center justify-between gap-4">
        <div className="flex items-center gap-4">
           <div className="h-10 w-10 rounded-xl bg-black dark:bg-zinc-900 flex items-center justify-center shadow-lg shadow-black/20 border border-white/10">
              <Terminal className="h-5 w-5 text-white" />
           </div>
           <div>
              <h1 className="text-xl font-bold text-black dark:text-white tracking-tight text-[var(--text-strong)]">FinOps Terminal</h1>
              <div className="flex items-center gap-2">
                 <Badge variant="success" className="text-[8px] h-4 px-1.5 font-black uppercase">System Live</Badge>
                 <span className="text-[10px] text-gray-400 dark:text-zinc-500 font-bold uppercase tracking-widest text-[var(--text-muted)]">v2.0.4-alpha</span>
              </div>
           </div>
        </div>

        <div className="flex-1 max-w-xl relative">
           <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400 dark:text-zinc-500" />
           <Input 
             placeholder="Search markets, intelligence, or run command (/) ..." 
             className="pl-10 h-10 bg-white/40 dark:bg-zinc-900/40 border-gray-200 dark:border-zinc-800 rounded-xl glass-card border-none shadow-sm focus-visible:ring-black dark:focus-visible:ring-white"
           />
        </div>

        <div className="flex items-center gap-3">
           <div className="flex flex-col items-end px-3 border-r border-gray-100 dark:border-zinc-800">
              <span className="text-[9px] font-black text-gray-400 dark:text-zinc-500 uppercase tracking-tighter">AI Latency</span>
              <span className="text-xs font-bold text-emerald-600 dark:text-emerald-400 font-mono">12ms</span>
           </div>
           <div className="flex flex-col items-end px-3">
              <span className="text-[9px] font-black text-gray-400 dark:text-zinc-500 uppercase tracking-tighter">API Health</span>
              <span className="text-xs font-bold text-blue-600 dark:text-blue-400 font-mono">99.9%</span>
           </div>
        </div>
      </div>

      {/* PROPRIETARY METRICS ROW */}
      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
         <MetricItem label="Alpha Score" value="84.2" change="+2.4" icon={<Zap className="h-3 w-3 text-amber-500" />} />
         <MetricItem label="Signal Flow" value="High" change="Active" icon={<Waves className="h-3 w-3 text-blue-500" />} />
         <MetricItem label="Market Vol" value="12.4%" change="-0.5" icon={<Activity className="h-3 w-3 text-emerald-500" />} />
         <MetricItem label="Global Cov." value="92" change="+4" icon={<Globe className="h-3 w-3 text-purple-500" />} />
         <MetricItem label="Sector Bias" value="Tech" change="Long" icon={<PieChart className="h-3 w-3 text-rose-500" />} />
         <MetricItem label="Intel Depth" value="Lvl 4" change="Deep" icon={<ShieldCheck className="h-3 w-3 text-sky-500" />} />
      </div>

      {/* MAIN WORKSPACE GRID */}
      <div className="grid lg:grid-cols-12 gap-6 h-full">
         
         {/* LEFT COLUMN: Intelligence Workspace */}
         <div className="lg:col-span-8 space-y-6">
            
            <div className="flex items-center justify-between px-2">
               <div className="flex items-center gap-2">
                  <LayoutGrid className="h-4 w-4 text-gray-400 dark:text-zinc-500" />
                  <h2 className="text-sm font-black uppercase tracking-[0.2em] text-gray-500 dark:text-zinc-400">Intelligence Workspace</h2>
               </div>
               <div className="flex items-center gap-2">
                  <Badge variant="outline" className="text-[10px] h-6 px-3 rounded-md bg-white dark:bg-zinc-900 border-gray-100 dark:border-zinc-800 font-bold uppercase text-gray-400 dark:text-zinc-500">Real-time Feed</Badge>
                  <Button variant="ghost" size="icon" className="h-6 w-6 text-gray-400 dark:text-zinc-500"><ListFilter className="h-3 w-3" /></Button>
               </div>
            </div>

            <IngestionControl />

            {/* Live Signals Ledger */}
            <GlassCard className="p-0 overflow-hidden min-h-[500px] border-none shadow-xl">
               <div className="p-5 border-b border-[var(--line-soft)] bg-[var(--surface-1)]/60 backdrop-blur-md flex items-center justify-between">
                  <div className="flex items-center gap-2">
                     <Zap className="h-4 w-4 text-amber-500" />
                     <span className="text-sm font-bold text-black dark:text-white">Live Signals Ledger</span>
                  </div>
                  <div className="flex items-center gap-2">
                     <Badge className="text-[9px] bg-black dark:bg-white text-white dark:text-black border-none h-5 font-black uppercase tracking-widest px-2">42 New Signals</Badge>
                  </div>
               </div>
               <div className="divide-y divide-[var(--line-soft)] overflow-y-auto max-h-[600px] custom-scrollbar">
                  <SignalRow ticker="NVDA" signal="Institutional Inflow" impact="High" confidence="94%" age="2m ago" color="emerald" />
                  <SignalRow ticker="AAPL" signal="Supply Chain Anomaly" impact="Med" confidence="82%" age="12m ago" color="amber" />
                  <SignalRow ticker="TSLA" signal="Regulatory Headwind" impact="High" confidence="78%" age="24m ago" color="red" />
                  <SignalRow ticker="MSFT" signal="Cloud Expansion" impact="Low" confidence="91%" age="45m ago" color="emerald" />
                  <SignalRow ticker="AMD" signal="Bullish Divergence" impact="Med" confidence="85%" age="1h ago" color="emerald" />
                  <SignalRow ticker="BTC" signal="Whale Transaction" impact="High" confidence="98%" age="2h ago" color="blue" />
                  <SignalRow ticker="AMZN" signal="Margin Expansion" impact="Med" confidence="88%" age="3h ago" color="emerald" />
                  <SignalRow ticker="GOOGL" signal="AI Monetization" impact="High" confidence="92%" age="4h ago" color="emerald" />
                  <SignalRow ticker="META" signal="Ad Revenue Surge" impact="High" confidence="95%" age="5h ago" color="emerald" />
               </div>
               <div className="p-4 bg-[var(--surface-0)] border-t border-[var(--line-soft)] text-center">
                  <Button variant="ghost" className="text-[10px] font-black uppercase tracking-widest text-gray-400 dark:text-zinc-500 hover:text-black dark:hover:text-white transition-colors">
                     View Full Archive
                  </Button>
               </div>
            </GlassCard>
         </div>

         {/* RIGHT COLUMN: Flash News Terminal */}
         <div className="lg:col-span-4 flex flex-col gap-6">
            <div className="flex items-center gap-2 px-2">
               <ShieldCheck className="h-4 w-4 text-blue-500" />
               <h2 className="text-sm font-black uppercase tracking-[0.2em] text-gray-500 dark:text-zinc-400">Verified Intelligence</h2>
            </div>
            <div className="h-[calc(100vh-280px)] min-h-[700px] sticky top-24">
               <NewsIntelligence />
            </div>
         </div>
      </div>
    </div>
  );
}

function MetricItem({ label, value, change, icon }: any) {
  return (
    <GlassCard className="p-4 flex flex-col gap-1 hover:bg-white dark:hover:bg-zinc-900 transition-all group border-none shadow-sm cursor-pointer">
       <div className="flex items-center justify-between mb-1">
          <span className="text-[10px] font-black text-gray-400 dark:text-zinc-500 uppercase tracking-tighter group-hover:text-black dark:group-hover:text-white transition-colors">{label}</span>
          {icon}
       </div>
       <div className="flex items-baseline gap-2">
          <span className="text-xl font-bold text-black dark:text-white font-mono tracking-tighter">{value}</span>
          <span className={`text-[9px] font-black ${change.startsWith('+') ? 'text-emerald-500' : 'text-blue-500'}`}>{change}</span>
       </div>
    </GlassCard>
  )
}

function SignalRow({ ticker, signal, impact, confidence, age, color }: any) {
  const colorMap: any = {
    emerald: 'bg-emerald-500',
    amber: 'bg-amber-500',
    red: 'bg-red-500',
    blue: 'bg-blue-500'
  };

  return (
    <div className="p-5 flex items-center justify-between hover:bg-[var(--surface-2)] transition-colors group cursor-pointer">
       <div className="flex items-center gap-4">
          <div className={`h-2 w-2 rounded-full ${colorMap[color]} shadow-sm group-hover:scale-125 transition-transform`} />
          <div className="flex flex-col">
             <span className="text-xs font-black text-black dark:text-white">{ticker}</span>
             <span className="text-[10px] font-bold text-gray-400 dark:text-zinc-500 uppercase tracking-tighter">{signal}</span>
          </div>
       </div>
       <div className="flex items-center gap-10 text-right">
          <div className="flex flex-col">
             <span className="text-[9px] font-black text-gray-300 dark:text-zinc-600 uppercase tracking-widest">Impact</span>
             <span className={`text-[10px] font-bold ${impact === 'High' ? 'text-black dark:text-white' : 'text-gray-500 dark:text-zinc-400'}`}>{impact}</span>
          </div>
          <div className="flex flex-col w-12">
             <span className="text-[9px] font-black text-gray-300 dark:text-zinc-600 uppercase tracking-widest font-mono">Confidence</span>
             <span className="text-[10px] font-bold text-black dark:text-white font-mono">{confidence}</span>
          </div>
          <span className="text-[10px] font-bold text-gray-300 dark:text-zinc-600 w-16 font-mono">{age}</span>
       </div>
    </div>
  )
}