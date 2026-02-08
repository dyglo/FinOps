import { Suspense } from 'react';

import { ResearchConsole } from '@/components/research/research-console';

function ResearchLoading() {
  return (
    <div className="rounded-xl border border-[var(--line-soft)] bg-[var(--surface-1)] p-5 text-sm text-[var(--text-muted)]">
      Loading deterministic runtime surfaces...
    </div>
  );
}

export default function ResearchPage() {
  return (
    <main className="space-y-6">
      <section>
        <p className="text-xs uppercase tracking-[0.14em] text-[var(--text-muted)]">Phase 2 Agent Plane</p>
        <h1 className="mt-2 text-3xl font-semibold text-[var(--text-strong)]">Research Room</h1>
        <p className="mt-3 max-w-2xl text-sm leading-6 text-[var(--text-base)]">
          Execute deterministic runtime graphs, inspect run ledger metadata, enforce citations for web-derived claims,
          and replay from stored tool responses.
        </p>
      </section>
      <Suspense fallback={<ResearchLoading />}>
        <ResearchConsole />
      </Suspense>
    </main>
  );
}
