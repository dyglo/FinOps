'use client';

import { useMutation, useQuery } from '@tanstack/react-query';
import { useMemo, useState } from 'react';

import { finopsApiClient } from '@/lib/api/client';
import type { IngestionJobRead, NewsDocumentRead } from '@/lib/contracts/api';

function makeIdempotencyKey() {
  return `news-${Date.now()}`;
}

export function IngestionConsole() {
  const [query, setQuery] = useState('nvidia earnings');
  const [jobId, setJobId] = useState<string | null>(null);

  const createJob = useMutation({
    mutationFn: async () => {
      const response = await finopsApiClient.createIngestionJob({
        provider: 'tavily',
        resource: 'news_search',
        idempotency_key: makeIdempotencyKey(),
        payload: { query, max_results: 8 },
      });
      return response.data;
    },
    onSuccess: (job) => {
      setJobId(job.id);
    },
  });

  const jobQuery = useQuery({
    queryKey: ['ingestion-job', jobId],
    enabled: Boolean(jobId),
    queryFn: async () => {
      const response = await finopsApiClient.getIngestionJob(jobId as string);
      return response.data;
    },
    refetchInterval: (queryData) => {
      const state = (queryData.state.data as IngestionJobRead | undefined)?.status;
      if (!state || state === 'pending' || state === 'running') {
        return 2000;
      }
      return false;
    },
  });

  const documentsQuery = useQuery({
    queryKey: ['news-documents', jobId],
    enabled: Boolean(jobId),
    queryFn: async () => {
      const response = await finopsApiClient.listNewsDocuments({ job_id: jobId as string, limit: 50, offset: 0 });
      return response.data;
    },
  });

  const status = useMemo(() => {
    if (!jobId) {
      return 'idle';
    }
    return jobQuery.data?.status ?? 'pending';
  }, [jobId, jobQuery.data?.status]);

  return (
    <section className="space-y-6">
      <div className="rounded-xl border border-[var(--line-soft)] bg-[var(--surface-1)] p-5">
        <h2 className="text-lg font-semibold text-[var(--text-strong)]">Create Ingestion Job</h2>
        <div className="mt-4 grid gap-3 md:grid-cols-[1fr_auto]">
          <input
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            className="w-full rounded-md border border-[var(--line-soft)] bg-white px-3 py-2 text-sm outline-none ring-sky-300 focus:ring"
            placeholder="Search query"
          />
          <button
            type="button"
            onClick={() => createJob.mutate()}
            disabled={createJob.isPending || query.trim().length < 2}
            className="rounded-md bg-slate-900 px-4 py-2 text-sm font-medium text-white disabled:cursor-not-allowed disabled:bg-slate-400"
          >
            {createJob.isPending ? 'Submitting...' : 'Submit Job'}
          </button>
        </div>
      </div>

      <div className="rounded-xl border border-[var(--line-soft)] bg-[var(--surface-1)] p-5">
        <h2 className="text-lg font-semibold text-[var(--text-strong)]">Job Status</h2>
        <p className="mt-3 text-sm text-[var(--text-base)]">Job ID: {jobId ?? 'No job submitted yet'}</p>
        <p className="mt-2 text-sm text-[var(--text-base)]">Status: {status}</p>
        {jobQuery.data?.error_message ? (
          <p className="mt-2 text-sm text-red-700">Error: {jobQuery.data.error_message}</p>
        ) : null}
      </div>

      <div className="rounded-xl border border-[var(--line-soft)] bg-[var(--surface-1)] p-5">
        <h2 className="text-lg font-semibold text-[var(--text-strong)]">Normalized Documents</h2>
        {documentsQuery.isLoading ? <p className="mt-3 text-sm text-[var(--text-muted)]">Loading documents...</p> : null}
        {documentsQuery.data && documentsQuery.data.length === 0 ? (
          <p className="mt-3 text-sm text-[var(--text-muted)]">No documents yet for this job.</p>
        ) : null}
        {documentsQuery.data && documentsQuery.data.length > 0 ? (
          <ul className="mt-4 space-y-3 text-sm text-[var(--text-base)]">
            {documentsQuery.data.map((document: NewsDocumentRead) => (
              <li key={document.id} className="rounded-md border border-[var(--line-soft)] bg-[var(--surface-0)] p-3">
                <p className="font-medium text-[var(--text-strong)]">{document.title}</p>
                <p className="mt-1 text-[var(--text-base)]">{document.snippet}</p>
                <a href={document.source_url} target="_blank" rel="noreferrer" className="mt-2 inline-block text-sky-700">
                  Source link
                </a>
              </li>
            ))}
          </ul>
        ) : null}
      </div>
    </section>
  );
}
