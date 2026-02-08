'use client';

import { useQuery } from '@tanstack/react-query';
import { api } from '@/lib/api/client';
import { MarketTimeseriesResponseSchema } from '@/lib/api/schemas';
import { GlassCard } from '@/components/ui/glass-card';
import { TrendingUp, BarChart2, ArrowUpRight } from 'lucide-react';
import dynamic from 'next/dynamic';

const TradingViewAdvancedChart = dynamic(() => import('@/components/charts/tradingview-advanced-chart'), {
  ssr: false,
  loading: () => <div className="h-full w-full bg-gray-50 animate-pulse rounded-xl" />,
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
    <GlassCard className="h-full flex flex-col p-8">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className="h-10 w-10 rounded-full bg-blue-100 flex items-center justify-center">
            <BarChart2 className="h-5 w-5 text-blue-600" />
          </div>
          <div>
            <h3 className="text-lg font-bold text-black">Market Snapshot</h3>
            <p className="text-xs text-gray-400 font-bold uppercase tracking-widest">Real-time Intelligence</p>
          </div>
        </div>
        <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-50 border border-emerald-100">
           <TrendingUp className="h-3 w-3 text-emerald-600" />
           <span className="text-xs font-bold text-emerald-700">Bullish</span>
        </div>
      </div>

      <div className="flex-1 min-h-[300px] relative rounded-2xl overflow-hidden border border-gray-100 bg-white/50">
        {/* We use the tradingview widget as the visual layer since we might not have enough raw data yet */}
        <TradingViewAdvancedChart symbol="NASDAQ:NDX" />
        
        {data && data.data.length > 0 && (
          <div className="absolute top-4 left-4 bg-white/90 backdrop-blur p-3 rounded-lg border border-gray-100 shadow-sm z-10">
             <div className="text-xs text-gray-400 uppercase font-bold">Internal Feed</div>
             <div className="text-lg font-bold text-black flex items-center gap-1">
               {data.data[0].close.toFixed(2)}
               <ArrowUpRight className="h-4 w-4 text-emerald-500" />
             </div>
          </div>
        )}
      </div>
    </GlassCard>
  );
}
