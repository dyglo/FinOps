'use client';

import { MarketSnapshot } from '@/components/dashboard/market-snapshot';
import { NewsIntelligence } from '@/components/dashboard/news-intelligence';
import { IngestionControl } from '@/components/dashboard/ingestion-control';

export default function DashboardPage() {
  return (
    <div className="flex flex-col gap-8 py-8 pb-20">
      <header className="flex flex-col gap-2">
         <h1 className="text-4xl font-bold text-black tracking-tight">Intelligence Dashboard</h1>
         <p className="text-gray-500">Real-time market signals and data ingestion pipeline.</p>
      </header>

      <div className="grid lg:grid-cols-3 gap-8 items-start h-full">
         {/* Left Column: Market Data (Visual Heavy) */}
         <div className="lg:col-span-2 space-y-8 h-full">
            <div className="h-[420px]">
               <MarketSnapshot />
            </div>
            <IngestionControl />
         </div>

         {/* Right Column: News Feed (Scrollable) */}
         <div className="h-[calc(100vh-200px)] min-h-[600px] sticky top-24">
            <NewsIntelligence />
         </div>
      </div>
    </div>
  );
}
