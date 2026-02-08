# Engineering Standards

## Testing
- API changes require unit/integration coverage.
- Multi-tenant access rules must have explicit tests.
- CI gates: Ruff, Mypy, Pytest, and Next.js build.

## Observability
- Every request emits `X-Request-Id` and response timing metadata.
- Structured JSON logging is the default for API runtime.
- Queue consumers must emit job status and failure diagnostics.

## Security
- No secrets committed.
- `.env.example` documents required variables.
- RLS is enabled and forced for tenant tables.
- All tenant tables include `org_id` and are queried via tenant-scoped sessions.

## Delivery
- Docker-first local runtime with production-parity services.
- Alembic migrations are source-controlled and applied at service startup.
- CI enforces static checks before merge.