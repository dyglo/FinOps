'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { api } from '@/lib/api/client';
import { MarketTimeseriesResponseSchema } from '@/lib/api/schemas';
import { GlassCard } from '@/components/ui/glass-card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { 
  Search, 
  Plus, 
  TrendingUp, 
  TrendingDown, 
  DollarSign, 
  Activity, 
  Layers, 
  ChevronRight,
  CandlestickChart,
  Target,
  Globe
} from 'lucide-react';
import dynamic from 'next/dynamic';
import { Badge } from '@/components/ui/badge';

const TradingViewAdvancedChart = dynamic(() => import('@/components/charts/tradingview-advanced-chart'), {
  ssr: false,
  loading: () => <div className="h-full w-full bg-gray-50/50 animate-pulse rounded-[32px] border-2 border-dashed border-gray-100" />,
});

const WATCHLIST = ['NVDA', 'AAPL', 'MSFT', 'TSLA', 'AMD', 'BTC', 'ETH', 'GOOGL'];

export default function MarketsPage() {
  const [selectedTicker, setSelectedTicker] = useState('NVDA');

  const { data: timeseries, isFetching } = useQuery({
    queryKey: ['market', 'timeseries', selectedTicker],
    queryFn: async () => {
       try {
         const response = await api.get('/v1/market/timeseries', { params: { symbol: selectedTicker, limit: 10 } });
         return MarketTimeseriesResponseSchema.parse(response);
       } catch (e) {
         return null; 
       }
    },
    retry: false
  });

  const latestQuote = timeseries?.data[0];

  return (
    <div className="flex flex-col h-[calc(100vh-100px)] gap-4 py-4">
      {/* TERMINAL HEADER */}
      <div className="flex items-center justify-between px-2">
        <div className="flex items-center gap-4">
           <div className="h-10 w-10 rounded-xl bg-black flex items-center justify-center shadow-lg">
              <Activity className="h-5 w-5 text-white" />
           </div>
           <div>
              <h1 className="text-xl font-bold text-black tracking-tight">Market Exploration</h1>
              <div className="flex items-center gap-2">
                 <Badge variant="success" className="text-[8px] h-4 px-1.5 font-black uppercase">Exchanges Active</Badge>
                 <span className="text-[10px] text-gray-400 font-bold uppercase tracking-widest">Feed Status: Nominal</span>
              </div>
           </div>
        </div>

        <div className="flex items-center gap-2">
           <div className="relative w-64">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
              <Input 
                placeholder="Lookup Symbol..." 
                className="pl-10 h-10 border-none bg-white/40 glass-card shadow-sm rounded-xl focus-visible:ring-black" 
              />
           </div>
           <Button variant="outline" className="h-10 px-4 gap-2 text-xs font-bold uppercase tracking-wider border-none glass-card bg-white/40 hover:bg-white transition-all">
              <Plus className="h-4 w-4" />
              <span>Watchlist</span>
           </Button>
        </div>
      </div>

      <div className="flex-1 flex gap-6 overflow-hidden min-h-0">
         {/* Left: Ticker Watchlist */}
         <div className="w-[320px] flex flex-col gap-4">
            <GlassCard className="p-0 flex-1 flex flex-col overflow-hidden border-none shadow-xl">
               <div className="p-4 border-b border-gray-100 bg-white/60 backdrop-blur-md flex items-center justify-between">
                  <div className="flex items-center gap-2">
                     <Layers className="h-4 w-4 text-gray-400" />
                     <span className="text-xs font-bold text-black uppercase tracking-widest">Active Watch</span>
                  </div>
                  {isFetching && <div className="h-1.5 w-1.5 rounded-full bg-blue-500 animate-pulse" />}
               </div>
               
               <div className="flex-1 overflow-y-auto divide-y divide-gray-50 custom-scrollbar">
                  {WATCHLIST.map(ticker => {
                     const active = selectedTicker === ticker;
                     return (
                        <div 
                          key={ticker}
                          onClick={() => setSelectedTicker(ticker)}
                          className={`
                            p-5 flex justify-between items-center cursor-pointer transition-all border-l-4
                            ${active ? 'bg-blue-50/50 border-blue-500 shadow-inner' : 'border-transparent hover:bg-gray-50/50'}
                          `}
                        >
                           <div className="flex flex-col">
                              <span className={`text-sm font-black ${active ? 'text-blue-900' : 'text-black'}`}>{ticker}</span>
                              <span className="text-[9px] font-bold text-gray-400 uppercase tracking-tighter">NASDAQ Exchange</span>
                           </div>
                           <div className="text-right flex flex-col items-end">
                              <span className="text-xs font-bold font-mono text-black">$1,244.50</span>
                              <div className="text-[9px] font-black text-emerald-600 flex items-center gap-0.5">
                                 <TrendingUp className="h-2 w-2" /> +1.24%
                              </div>
                           </div>
                        </div>
                     )
                  })}
               </div>
            </GlassCard>
         </div>

         {/* Right: Main Analytics Pane */}
         <div className="flex-1 flex flex-col gap-6 overflow-hidden">
            <div className="grid grid-cols-4 gap-4">
               <MarketMetric label="Spot Price" value={latestQuote ? `$${latestQuote.close.toFixed(2)}` : '---.--'} icon={<DollarSign className="h-4 w-4 text-black" />} />
               <MarketMetric label="24h Delta" value="+2.45%" trend="up" icon={<TrendingUp className="h-4 w-4 text-emerald-500" />} />
               <MarketMetric label="Volume (M)" value={latestQuote ? `${(latestQuote.volume / 1000000).toFixed(1)}M` : '--- M'} icon={<Activity className="h-4 w-4 text-blue-500" />} />
               <MarketMetric label="Intel Rank" value="#4" icon={<Target className="h-4 w-4 text-purple-500" />} />
            </div>

            <GlassCard className="flex-1 p-0 overflow-hidden border-none shadow-2xl relative">
               <div className="absolute top-6 left-6 z-10 flex items-center gap-4 bg-white/90 backdrop-blur-md p-4 rounded-2xl border border-white shadow-lg shadow-black/5">
                  <div className="h-10 w-10 rounded-xl bg-black flex items-center justify-center text-white">
                     <CandlestickChart className="h-5 w-5" />
                  </div>
                  <div>
                     <h2 className="text-xl font-bold text-black tracking-tighter">{selectedTicker} / USD</h2>
                     <p className="text-[10px] text-gray-400 font-bold uppercase tracking-[0.2em]">Real-time Analytics Surface</p>
                  </div>
               </div>
               <div className="absolute top-6 right-6 z-10 flex items-center gap-2">
                  <Badge variant="outline" className="bg-white/80 border-gray-100 text-[9px] h-8 px-3 font-black uppercase tracking-widest text-gray-400">Timeframe: 1D</Badge>
                  <Button variant="ghost" size="icon" className="h-8 w-8 bg-white/80 border border-gray-100 rounded-lg hover:bg-white">
                     <Globe className="h-4 w-4 text-gray-400" />
                  </Button>
               </div>
               
               <div className="h-full w-full">
                  <TradingViewAdvancedChart symbol={`NASDAQ:${selectedTicker}`} />
               </div>
            </GlassCard>
         </div>
      </div>
    </div>
  );
}

function MarketMetric({ label, value, trend, icon }: any) {
  return (
    <GlassCard className="p-4 py-5 flex items-center gap-4 border-none shadow-lg hover:bg-white transition-all cursor-pointer group">
       <div className="h-10 w-10 rounded-xl bg-gray-50 flex items-center justify-center border border-gray-100 group-hover:scale-110 transition-transform">
          {icon}
       </div>
       <div className="flex flex-col min-w-0">
          <span className="text-[9px] font-black text-gray-300 uppercase tracking-widest mb-0.5">{label}</span>
          <span className={`text-lg font-bold font-mono tracking-tighter truncate ${trend === 'up' ? 'text-emerald-600' : 'text-black'}`}>
             {value}
          </span>
       </div>
    </GlassCard>
  )
}