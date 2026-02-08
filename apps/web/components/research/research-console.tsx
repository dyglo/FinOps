'use client';

import { useMutation, useQuery } from '@tanstack/react-query';
import { useMemo, useState } from 'react';

import { finopsApiClient } from '@/lib/api/client';
import type { IntelRunRead } from '@/lib/contracts/api';

type RunOutput = {
  summary?: string;
  claims?: { claim: string; citations: string[] }[];
  citations?: string[];
  tool_count?: number;
};

export function ResearchConsole() {
  const [query, setQuery] = useState('nvidia');
  const [runId, setRunId] = useState<string | null>(null);

  const createRun = useMutation({
    mutationFn: async () => {
      const response = await finopsApiClient.createIntelRun({
        run_type: 'research_summary',
        model_name: 'gpt-5-mini',
        prompt_version: 'v1',
        input_snapshot_uri: query,
        input_payload: {
          query,
          limit: 5,
          tool_name: 'news_document_search',
        },
        execution_mode: 'live',
      });
      return response.data;
    },
    onSuccess: (run) => {
      setRunId(run.id);
    },
  });

  const runQuery = useQuery({
    queryKey: ['intel-run', runId],
    enabled: Boolean(runId),
    queryFn: async () => {
      const response = await finopsApiClient.getIntelRun(runId as string);
      return response.data;
    },
    refetchInterval: (queryData) => {
      const state = (queryData.state.data as IntelRunRead | undefined)?.status;
      if (!state || state === 'pending' || state === 'running') {
        return 2000;
      }
      return false;
    },
  });

  const replayRun = useMutation({
    mutationFn: async () => {
      if (!runId) {
        throw new Error('No source run selected for replay');
      }
      const response = await finopsApiClient.replayIntelRun(runId, {});
      return response.data;
    },
    onSuccess: (replay) => {
      setRunId(replay.id);
    },
  });

  const runData = runQuery.data;
  const output = (runData?.output_payload ?? {}) as RunOutput;
  const citations = output.citations ?? [];

  const citationMessage = useMemo(() => {
    if (!runData) {
      return 'No run executed yet.';
    }
    if (runData.status === 'failed' && runData.error_message?.includes('Citations are required')) {
      return 'Run failed because no citations were available for web-derived claims.';
    }
    if (citations.length === 0) {
      return 'No citations available.';
    }
    return `${citations.length} citation(s) captured.`;
  }, [citations.length, runData]);

  return (
    <section className="space-y-6">
      <div className="rounded-xl border border-[var(--line-soft)] bg-[var(--surface-1)] p-5">
        <h2 className="text-lg font-semibold text-[var(--text-strong)]">Create Deterministic Run</h2>
        <div className="mt-4 grid gap-3 md:grid-cols-[1fr_auto]">
          <input
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            className="w-full rounded-md border border-[var(--line-soft)] bg-white px-3 py-2 text-sm outline-none ring-sky-300 focus:ring"
            placeholder="Research query"
          />
          <button
            type="button"
            onClick={() => createRun.mutate()}
            disabled={createRun.isPending || query.trim().length < 2}
            className="rounded-md bg-slate-900 px-4 py-2 text-sm font-medium text-white disabled:cursor-not-allowed disabled:bg-slate-400"
          >
            {createRun.isPending ? 'Executing...' : 'Run Analysis'}
          </button>
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <div className="rounded-xl border border-[var(--line-soft)] bg-[var(--surface-1)] p-5">
          <h2 className="text-lg font-semibold text-[var(--text-strong)]">Run Ledger</h2>
          <p className="mt-3 text-sm text-[var(--text-base)]">Run ID: {runId ?? 'No run yet'}</p>
          <p className="mt-2 text-sm text-[var(--text-base)]">Status: {runData?.status ?? 'idle'}</p>
          <p className="mt-2 text-sm text-[var(--text-base)]">Execution Mode: {runData?.execution_mode ?? '-'}</p>
          <p className="mt-2 text-sm text-[var(--text-base)]">Graph Version: {runData?.graph_version ?? '-'}</p>
          {runData?.error_message ? <p className="mt-2 text-sm text-red-700">Error: {runData.error_message}</p> : null}
          <button
            type="button"
            onClick={() => replayRun.mutate()}
            disabled={!runId || replayRun.isPending}
            className="mt-4 rounded-md border border-[var(--line-soft)] px-3 py-2 text-sm text-[var(--text-strong)] disabled:cursor-not-allowed disabled:text-[var(--text-muted)]"
          >
            {replayRun.isPending ? 'Replaying...' : 'Replay Run'}
          </button>
        </div>

        <div className="rounded-xl border border-[var(--line-soft)] bg-[var(--surface-1)] p-5">
          <h2 className="text-lg font-semibold text-[var(--text-strong)]">Summary</h2>
          <p className="mt-3 text-sm text-[var(--text-base)]">{output.summary ?? 'Awaiting execution.'}</p>
          <p className="mt-3 text-sm text-[var(--text-base)]">{citationMessage}</p>
        </div>
      </div>

      <div className="rounded-xl border border-[var(--line-soft)] bg-[var(--surface-1)] p-5">
        <h2 className="text-lg font-semibold text-[var(--text-strong)]">Citations</h2>
        {citations.length > 0 ? (
          <ul className="mt-3 space-y-2 text-sm text-[var(--text-base)]">
            {citations.map((citation) => (
              <li key={citation} className="truncate rounded-md border border-[var(--line-soft)] bg-[var(--surface-0)] p-2">
                <a href={citation} target="_blank" rel="noreferrer" className="text-sky-700">
                  {citation}
                </a>
              </li>
            ))}
          </ul>
        ) : (
          <p className="mt-3 text-sm text-[var(--text-muted)]">No citations returned yet.</p>
        )}
      </div>
    </section>
  );
}
