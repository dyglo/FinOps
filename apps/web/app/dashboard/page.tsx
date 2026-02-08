import { NewsIntelligencePanel } from '@/components/news/news-intelligence-panel';
import { IngestionConsole } from '@/components/news/ingestion-console';
import { DashboardChartPanel } from '@/components/charts/dashboard-chart-panel';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { TrendingUp, Activity, Globe } from 'lucide-react';

export default function DashboardPage() {
  return (
    <div className="space-y-8">
      <header>
        <h1 className="text-3xl font-bold text-[var(--text-strong)]">Intelligence Overview</h1>
        <p className="text-[var(--text-muted)] mt-1">Institutional-grade data ingestion and market analysis.</p>
      </header>

      <div className="grid gap-6 md:grid-cols-4">
         <Card className="bg-[var(--surface-1)]">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-xs font-medium uppercase tracking-wider text-[var(--text-muted)]">
              Market Status
            </CardTitle>
            <Activity className="h-4 w-4 text-emerald-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">Open</div>
            <p className="text-[10px] text-[var(--text-muted)] mt-1">NASDAQ / NYSE Active</p>
          </CardContent>
        </Card>

        <Card className="bg-[var(--surface-1)]">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-xs font-medium uppercase tracking-wider text-[var(--text-muted)]">
              Sentiment
            </CardTitle>
            <TrendingUp className="h-4 w-4 text-sky-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">Bullish</div>
            <p className="text-[10px] text-[var(--text-muted)] mt-1">+12% vs last 7d</p>
          </CardContent>
        </Card>

        <Card className="bg-[var(--surface-1)]">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-xs font-medium uppercase tracking-wider text-[var(--text-muted)]">
              Coverage
            </CardTitle>
            <Globe className="h-4 w-4 text-purple-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">Global</div>
            <p className="text-[10px] text-[var(--text-muted)] mt-1">Multi-source news</p>
          </CardContent>
        </Card>

        <Card className="bg-[var(--surface-1)] border-dashed border-2">
           <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-xs font-medium uppercase tracking-wider text-[var(--text-muted)]">
              System Health
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-emerald-600">Optimal</div>
            <p className="text-[10px] text-[var(--text-muted)] mt-1">All services online</p>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-6 lg:grid-cols-12">
        <div className="lg:col-span-8 space-y-6">
          <section className="rounded-xl border border-[var(--line-soft)] bg-[var(--surface-1)] p-6">
            <div className="mb-4 flex items-center justify-between">
              <h2 className="text-xl font-semibold text-[var(--text-strong)]">Live Market Analytics</h2>
            </div>
            <DashboardChartPanel />
          </section>
          
          <IngestionConsole />
        </div>

        <div className="lg:col-span-4">
          <NewsIntelligencePanel />
        </div>
      </div>
    </div>
  );
}