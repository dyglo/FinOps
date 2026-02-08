# FinOps API Core

FastAPI service for tenant-scoped APIs, deterministic pipelines, and auditability.

## Local Run (Docker Compose)
1. From repo root: `docker compose up --build`.
2. Open Swagger: `http://localhost:8000/docs`.

## Phase 1 Verification (Swagger)
1. Call `POST /v1/ingestion/jobs`:
   - Header: `X-Org-Id: <tenant-uuid>`
   - Body:
     - `provider: "tavily"`
     - `resource: "news_search"`
     - `idempotency_key: "news-<unique-key>"`
     - `payload: {"query":"nvidia earnings","max_results":5}`
2. Poll `GET /v1/ingestion/jobs/{job_id}` until `status=completed`.
3. Read normalized documents:
   - `GET /v1/documents/news?job_id=<job_id>`
4. Tenant isolation check:
   - Call the same `GET` with a different `X-Org-Id`.
   - Expected: no records from the original tenant.
