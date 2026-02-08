# Architecture Baseline

## Runtime Topology
- `apps/web`: Next.js app deployed on Vercel.
- `apps/api-core`: FastAPI API for deterministic data and agent orchestration.
- `apps/api-core` worker runtime: Arq consumers for ingestion, processing, and agent async jobs.
- `postgres` with `pgvector`: system of record plus vector storage.
- `redis`: cache, queue, and coordination backend.

## Service Boundaries
- API owns external contracts, tenant context, and request validation.
- Worker lanes own ingestion/processing execution with idempotent envelopes.
- DB schemas isolate core entities, market data, intelligence runs, and audit entries.

## Determinism and Auditability
- Every tenant-bound request requires `X-Org-Id` and writes are `org_id` scoped.
- All AI/tool interactions are intended to be persisted in `tool_call_audit`.
- Pipeline execution is job-queue driven, enabling replay with immutable inputs.