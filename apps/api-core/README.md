# FinOps API Core

FastAPI service for tenant-scoped APIs, deterministic pipelines, and auditability.

## Local Run (Docker Compose)
1. From repo root: `docker compose up --build`.
2. Open Swagger: `http://localhost:8000/docs`.
3. Health:
   - `GET http://localhost:8000/health/live`
   - `GET http://localhost:8000/health/ready`

## Phase 1 Verification (Swagger)
1. Call `POST /v1/ingestion/jobs`:
   - Header: `X-Org-Id: <tenant-uuid>`
   - Body:
     - `provider: "tavily" | "serper" | "serpapi"`
     - `resource: "news_search"`
     - `idempotency_key: "news-<unique-key>"`
     - `payload: {"query":"nvidia earnings","max_results":5}` for Tavily
     - `payload: {"query":"nvidia earnings","num":5}` for Serper
     - `payload: {"query":"nvidia earnings","num":5}` for SerpAPI
2. Poll `GET /v1/ingestion/jobs/{job_id}` until `status=completed`.
3. Read normalized documents:
   - `GET /v1/documents/news?job_id=<job_id>`
4. Tenant isolation check:
   - Call the same `GET` with a different `X-Org-Id`.
   - Expected: no records from the original tenant.

## Demo Seed + Endpoint Validation (Non-Empty Local Data)
Use this when provider keys are absent or you need deterministic local demo data.

1. Start backend stack from repo root:
   - `docker compose up --build -d postgres redis api-core worker`
2. Seed tenant-scoped demo data:
   - `docker compose exec api-core python -m finops_api.scripts.demo_seed --org-id 00000000-0000-0000-0000-000000000001 --symbol AAPL`
3. Verify ingestion jobs:
   - `curl -H "X-Org-Id: 00000000-0000-0000-0000-000000000001" http://localhost:8000/v1/ingestion/jobs/<job_id>`
4. Verify documents:
   - `curl -H "X-Org-Id: 00000000-0000-0000-0000-000000000001" "http://localhost:8000/v1/documents/news?limit=20"`
5. Verify market:
   - `curl -H "X-Org-Id: 00000000-0000-0000-0000-000000000001" "http://localhost:8000/v1/market/timeseries?symbol=AAPL&limit=20"`
   - `curl -H "X-Org-Id: 00000000-0000-0000-0000-000000000001" "http://localhost:8000/v1/market/quote?symbol=AAPL"`
6. Verify signals (if enabled):
   - `curl -H "X-Org-Id: 00000000-0000-0000-0000-000000000001" "http://localhost:8000/v1/signals/query?symbol=AAPL&limit=20"`

All `/v1/*` endpoints require `X-Org-Id` and return the canonical envelope:
`{ data, error, meta: { request_id, org_id, trace_id, ts, version } }`
