# FinOps

Institutional-grade finance intelligence platform scaffolding.

## Services
- `apps/api-core`: FastAPI API + worker runtime
- `apps/web`: Next.js web application
- `postgres`: primary datastore with pgvector
- `redis`: cache, queue, and rate limiting backend

## Quick Start
1. Copy `.env.example` to `.env` and fill values.
2. Start all services: `docker compose up --build`.
3. API docs: `http://localhost:8000/docs`
4. Web app: `http://localhost:3000`

## Local Validation
- API checks: `cd apps/api-core && python -m ruff check src tests && python -m mypy src && python -m pytest -q`
- Web checks: `cd apps/web && npm run lint && npm run build`

## Docs
- Architecture: `docs/architecture.md`
- Engineering standards: `docs/engineering-standards.md`
- Phase roadmap: `docs/phases.md`

## Phase 1 Swagger Demo
1. Start stack: `docker compose up --build`.
2. Open API docs: `http://localhost:8000/docs`.
3. Call `POST /v1/ingestion/jobs` with:
   - Header: `X-Org-Id: <tenant-uuid>`
   - Optional Header: `X-Request-Id: <request-uuid>`
   - Body:
     - `provider: "tavily"`
     - `resource: "news_search"`
     - `idempotency_key: "<unique-key>"`
     - `payload: {"query":"nvidia earnings","max_results":5}`
4. Poll `GET /v1/ingestion/jobs/{job_id}` until `status=completed`.
5. Read normalized results with `GET /v1/documents/news?job_id=<job_id>`.
6. Confirm tenant isolation:
   - Repeat step 5 with another tenant `X-Org-Id`.
   - Expected: no visibility into the first tenant's rows.

## Phase 2 Swagger Demo
1. Create and execute deterministic run with `POST /v1/intel/runs`:
   - Header: `X-Org-Id: <tenant-uuid>`
   - Body example:
     - `run_type: "research_summary"`
     - `model_name: "gpt-5-mini"`
     - `prompt_version: "v1"`
     - `input_snapshot_uri: "nvidia"`
     - `input_payload: {"query":"nvidia","limit":5}`
     - `execution_mode: "live"`
2. Fetch run ledger with `GET /v1/intel/runs/{run_id}`.
3. Replay deterministically from stored tool responses:
   - `POST /v1/intel/runs/{run_id}/replay` with `{}` body.

## Architecture Notes
- Multi-tenant by default via required `X-Org-Id` header and `org_id`-scoped tables.
- Deterministic pipelines and auditable AI run ledger are first-class concerns.
- No secrets are committed; use environment variables only.
