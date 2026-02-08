import { IngestionConsole } from '@/components/news/ingestion-console';

export default function NewsPage() {
  return (
    <main className="space-y-6">
      <section>
        <p className="text-xs uppercase tracking-[0.14em] text-[var(--text-muted)]">Phase 1 Data Plane</p>
        <h1 className="mt-2 text-3xl font-semibold text-[var(--text-strong)]">News Pipeline</h1>
        <p className="mt-3 max-w-2xl text-sm leading-6 text-[var(--text-base)]">
          Create ingestion jobs, monitor processing status, and inspect canonical news records produced by the
          deterministic data pipeline.
        </p>
      </section>
      <IngestionConsole />
    </main>
  );
}
