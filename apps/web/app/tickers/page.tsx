import { finopsApiClient } from '@/lib/api/client';

export const dynamic = 'force-dynamic';

export default async function TickersPage() {
  let records = 0;
  try {
    const response = await finopsApiClient.listNewsDocuments({ limit: 25, offset: 0 });
    records = response.data.length;
  } catch {
    records = 0;
  }

  return (
    <main className="space-y-6">
      <section>
        <p className="text-xs uppercase tracking-[0.14em] text-[var(--text-muted)]">Market Expansion Lane</p>
        <h1 className="mt-2 text-3xl font-semibold text-[var(--text-strong)]">Ticker Lab</h1>
        <p className="mt-3 max-w-2xl text-sm leading-6 text-[var(--text-base)]">
          Placeholder surfaces for market feeds and symbol analytics, already connected to current canonical data lane
          contracts for continuity.
        </p>
      </section>

      <section className="grid gap-4 md:grid-cols-3">
        <div className="rounded-xl border border-[var(--line-soft)] bg-[var(--surface-1)] p-5">
          <p className="text-xs uppercase tracking-[0.14em] text-[var(--text-muted)]">News-backed Signals</p>
          <p className="mt-3 text-3xl font-semibold text-[var(--text-strong)]">{records}</p>
          <p className="mt-2 text-sm text-[var(--text-muted)]">Records available for signal prototyping.</p>
        </div>
        <div className="rounded-xl border border-[var(--line-soft)] bg-[var(--surface-1)] p-5">
          <p className="text-xs uppercase tracking-[0.14em] text-[var(--text-muted)]">Price Stream Slot</p>
          <p className="mt-3 text-lg font-medium text-[var(--text-strong)]">Reserved for Twelve Data integration</p>
        </div>
        <div className="rounded-xl border border-[var(--line-soft)] bg-[var(--surface-1)] p-5">
          <p className="text-xs uppercase tracking-[0.14em] text-[var(--text-muted)]">Execution Slot</p>
          <p className="mt-3 text-lg font-medium text-[var(--text-strong)]">Reserved for Alpaca order telemetry</p>
        </div>
      </section>
    </main>
  );
}
