'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { api } from '@/lib/api/client';
import { MarketTimeseriesResponseSchema } from '@/lib/api/schemas';
import { GlassCard } from '@/components/ui/glass-card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Search, Plus, TrendingUp, TrendingDown, DollarSign } from 'lucide-react';
import dynamic from 'next/dynamic';

const TradingViewAdvancedChart = dynamic(() => import('@/components/charts/tradingview-advanced-chart'), {
  ssr: false,
  loading: () => <div className="h-full w-full bg-gray-50 animate-pulse rounded-xl" />,
});

const WATCHLIST = ['NVDA', 'AAPL', 'MSFT', 'TSLA', 'AMD'];

export default function MarketsPage() {
  const [selectedTicker, setSelectedTicker] = useState('NVDA');

  const { data: timeseries } = useQuery({
    queryKey: ['market', 'timeseries', selectedTicker],
    queryFn: async () => {
       try {
         const response = await api.get('/v1/market/timeseries', { params: { symbol: selectedTicker, limit: 1 } });
         return MarketTimeseriesResponseSchema.parse(response);
       } catch (e) {
         return null; 
       }
    },
    retry: false
  });

  const latestQuote = timeseries?.data[0];

  return (
    <div className="flex flex-col gap-8 py-8 pb-20">
      <div className="flex justify-between items-end">
        <div className="space-y-2">
           <h1 className="text-4xl font-bold text-black tracking-tight">Market Data</h1>
           <p className="text-gray-500">Real-time pricing and ticker exploration.</p>
        </div>
        <div className="relative w-64">
           <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
           <Input placeholder="Search Ticker..." className="pl-10 h-12 bg-white/50 border-gray-200 rounded-xl" />
        </div>
      </div>

      <div className="grid lg:grid-cols-4 gap-8">
         {/* Left: Watchlist */}
         <div className="lg:col-span-1 space-y-4">
            <GlassCard className="p-0 overflow-hidden">
               <div className="p-4 border-b border-gray-100 flex justify-between items-center bg-gray-50/50">
                  <h3 className="font-bold text-sm text-gray-500 uppercase tracking-widest">Watchlist</h3>
                  <Button size="icon" variant="ghost" className="h-6 w-6"><Plus className="h-4 w-4" /></Button>
               </div>
               <div className="divide-y divide-gray-100">
                  {WATCHLIST.map(ticker => (
                     <div 
                       key={ticker}
                       onClick={() => setSelectedTicker(ticker)}
                       className={`
                         p-4 flex justify-between items-center cursor-pointer transition-colors
                         ${selectedTicker === ticker ? 'bg-blue-50/50' : 'hover:bg-gray-50/50'}
                       `}
                     >
                        <div>
                           <div className="font-bold text-black">{ticker}</div>
                           <div className="text-xs text-gray-400 font-bold">NASDAQ</div>
                        </div>
                        <div className="text-right">
                           <div className="font-mono text-sm font-bold">$124.50</div>
                           <div className="text-xs font-bold text-emerald-600 flex items-center justify-end gap-0.5">
                              <TrendingUp className="h-3 w-3" /> +1.2%
                           </div>
                        </div>
                     </div>
                  ))}
               </div>
            </GlassCard>
         </div>

         {/* Right: Main Chart & Details */}
         <div className="lg:col-span-3 space-y-8">
            <div className="grid md:grid-cols-3 gap-6">
               <GlassCard className="p-6 flex items-center gap-4">
                  <div className="h-12 w-12 rounded-full bg-black flex items-center justify-center text-white">
                     <DollarSign className="h-6 w-6" />
                  </div>
                  <div>
                     <p className="text-xs text-gray-400 font-bold uppercase tracking-widest">Last Price</p>
                     <h3 className="text-2xl font-bold font-mono tracking-tight">
                        {latestQuote ? latestQuote.close.toFixed(2) : '---.--'}
                     </h3>
                  </div>
               </GlassCard>
               <GlassCard className="p-6 flex items-center gap-4">
                  <div className="h-12 w-12 rounded-full bg-emerald-100 flex items-center justify-center text-emerald-700">
                     <TrendingUp className="h-6 w-6" />
                  </div>
                  <div>
                     <p className="text-xs text-gray-400 font-bold uppercase tracking-widest">24h Change</p>
                     <h3 className="text-2xl font-bold font-mono tracking-tight text-emerald-600">+2.45%</h3>
                  </div>
               </GlassCard>
               <GlassCard className="p-6 flex items-center gap-4">
                  <div className="h-12 w-12 rounded-full bg-blue-100 flex items-center justify-center text-blue-700">
                     <TrendingDown className="h-6 w-6" />
                  </div>
                  <div>
                     <p className="text-xs text-gray-400 font-bold uppercase tracking-widest">Volume</p>
                     <h3 className="text-2xl font-bold font-mono tracking-tight">
                        {latestQuote ? (latestQuote.volume / 1000000).toFixed(1) + 'M' : '--- M'}
                     </h3>
                  </div>
               </GlassCard>
            </div>

            <GlassCard className="h-[500px] p-6 relative">
               <div className="absolute top-6 left-6 z-10">
                  <h2 className="text-2xl font-bold text-black">{selectedTicker}</h2>
                  <p className="text-xs text-gray-400 font-bold uppercase tracking-widest">Advanced Charting</p>
               </div>
               <TradingViewAdvancedChart symbol={`NASDAQ:${selectedTicker}`} />
            </GlassCard>
         </div>
      </div>
    </div>
  );
}
