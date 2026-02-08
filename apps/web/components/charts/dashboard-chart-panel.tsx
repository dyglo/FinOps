'use client';

import dynamic from 'next/dynamic';

const TradingViewAdvancedChart = dynamic(() => import('@/components/charts/tradingview-advanced-chart'), {
  ssr: false,
  loading: () => (
    <div className="flex h-[420px] items-center justify-center rounded-lg border border-[var(--line-soft)] bg-[var(--surface-0)] text-sm text-[var(--text-muted)]">
      Loading chart surface...
    </div>
  ),
});

export function DashboardChartPanel() {
  return <TradingViewAdvancedChart symbol="NASDAQ:AAPL" />;
}
