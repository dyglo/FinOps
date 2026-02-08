'use client';

import { useQuery } from '@tanstack/react-query';
import { api } from '@/lib/api/client';
import { MarketTimeseriesResponseSchema } from '@/lib/api/schemas';
import { GlassCard } from '@/components/ui/glass-card';
import { TrendingUp, BarChart2, ArrowUpRight } from 'lucide-react';
import dynamic from 'next/dynamic';

const TradingViewAdvancedChart = dynamic(() => import('@/components/charts/tradingview-advanced-chart'), {
  ssr: false,
  loading: () => <div className="h-full w-full bg-[var(--surface-0)] animate-pulse rounded-xl" />,
});

export function MarketSnapshot() {
  const { data, isLoading } = useQuery({
    queryKey: ['market', 'timeseries', 'SPY'],
    queryFn: async () => {
      // Intentionally using a mock symbol or checking if the backend actually supports it.
      // If the backend returns 404 or empty, we handle it.
      try {
        const response = await api.get('/v1/market/timeseries', { params: { symbol: 'SPY', limit: 50 } });
        return MarketTimeseriesResponseSchema.parse(response);
      } catch (e) {
        return null;
      }
    },
    retry: false,
  });

  return (
    <GlassCard className="h-full flex flex-col p-8 border-none shadow-xl">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className="h-10 w-10 rounded-full bg-blue-100 dark:bg-blue-900/30 flex items-center justify-center border border-blue-200 dark:border-blue-900/50">
            <BarChart2 className="h-5 w-5 text-blue-600 dark:text-blue-400" />
          </div>
          <div>
            <h3 className="text-lg font-bold text-black dark:text-white">Market Snapshot</h3>
            <p className="text-xs text-gray-400 dark:text-zinc-600 font-black uppercase tracking-widest transition-colors">Real-time Intelligence</p>
          </div>
        </div>
        <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-50 dark:bg-emerald-900/30 border border-emerald-100 dark:border-emerald-900/50">
           <TrendingUp className="h-3 w-3 text-emerald-600 dark:text-emerald-400" />
           <span className="text-xs font-bold text-emerald-700 dark:text-emerald-400">Bullish</span>
        </div>
      </div>

      <div className="flex-1 min-h-[300px] relative rounded-2xl overflow-hidden border border-[var(--line-soft)] bg-[var(--surface-1)]/50">
        {/* We use the tradingview widget as the visual layer since we might not have enough raw data yet */}
        <TradingViewAdvancedChart symbol="NASDAQ:NDX" />
        
        {data && data.data.length > 0 && (
          <div className="absolute top-4 left-4 bg-[var(--surface-1)]/90 backdrop-blur p-3 rounded-lg border border-[var(--line-soft)] shadow-sm z-10">
             <div className="text-[9px] text-gray-400 dark:text-zinc-500 uppercase font-black tracking-widest mb-0.5">Internal Feed</div>
             <div className="text-lg font-bold text-black dark:text-white flex items-center gap-1 font-mono tracking-tighter">
               {data.data[0].close.toFixed(2)}
               <ArrowUpRight className="h-4 w-4 text-emerald-500" />
             </div>
          </div>
        )}
      </div>
    </GlassCard>
  );
}