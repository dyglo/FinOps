import Link from 'next/link';

import { DashboardChartPanel } from '@/components/charts/dashboard-chart-panel';
import { finopsApiClient } from '@/lib/api/client';

export const dynamic = 'force-dynamic';

export default async function DashboardPage() {
  let headlineCount = 0;
  let latestHeadlines: string[] = [];

  try {
    const response = await finopsApiClient.listNewsDocuments({ limit: 5, offset: 0 });
    headlineCount = response.data.length;
    latestHeadlines = response.data.map((item) => item.title);
  } catch {
    latestHeadlines = [];
  }

  return (
    <main className="space-y-8">
      <section className="grid gap-4 md:grid-cols-3">
        <div className="rounded-xl border border-[var(--line-soft)] bg-[var(--surface-1)] p-5">
          <p className="text-xs uppercase tracking-[0.14em] text-[var(--text-muted)]">Canonical News</p>
          <p className="mt-3 text-3xl font-semibold text-[var(--text-strong)]">{headlineCount}</p>
          <p className="mt-2 text-sm text-[var(--text-muted)]">Most recent normalized records loaded.</p>
        </div>
        <div className="rounded-xl border border-[var(--line-soft)] bg-[var(--surface-1)] p-5">
          <p className="text-xs uppercase tracking-[0.14em] text-[var(--text-muted)]">Ingestion Workspace</p>
          <p className="mt-3 text-lg font-medium text-[var(--text-strong)]">Launch jobs and monitor completion</p>
          <Link href="/news" className="mt-3 inline-block text-sm font-medium text-sky-700">
            Open News Pipeline
          </Link>
        </div>
        <div className="rounded-xl border border-[var(--line-soft)] bg-[var(--surface-1)] p-5">
          <p className="text-xs uppercase tracking-[0.14em] text-[var(--text-muted)]">Agent Research</p>
          <p className="mt-3 text-lg font-medium text-[var(--text-strong)]">Run deterministic reports and replay</p>
          <Link href="/research" className="mt-3 inline-block text-sm font-medium text-sky-700">
            Open Research Room
          </Link>
        </div>
      </section>

      <section className="rounded-xl border border-[var(--line-soft)] bg-[var(--surface-1)] p-6">
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-xl font-semibold text-[var(--text-strong)]">Live Market Analytics</h2>
          <p className="text-xs uppercase tracking-[0.14em] text-[var(--text-muted)]">TradingView Advanced Chart</p>
        </div>
        <DashboardChartPanel />
      </section>

      <section className="rounded-xl border border-[var(--line-soft)] bg-[var(--surface-1)] p-6">
        <h2 className="text-xl font-semibold text-[var(--text-strong)]">Latest Headlines</h2>
        {latestHeadlines.length > 0 ? (
          <ul className="mt-4 space-y-3 text-sm text-[var(--text-base)]">
            {latestHeadlines.map((headline) => (
              <li key={headline} className="rounded-md border border-[var(--line-soft)] bg-[var(--surface-0)] p-3">
                {headline}
              </li>
            ))}
          </ul>
        ) : (
          <p className="mt-4 text-sm text-[var(--text-muted)]">
            No headlines available yet. Trigger ingestion from the News Pipeline.
          </p>
        )}
      </section>
    </main>
  );
}
