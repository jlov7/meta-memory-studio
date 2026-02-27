# Runbook (MVP)

## Local development

Preferred:
- `make dev` (backend + frontend)

Manual:
- backend: `cd backend && uv sync --group dev && uv run uvicorn app.main:app --reload --port 8000`
- frontend: `cd frontend && pnpm install && pnpm dev`

## Quality gates

- Static checks: `make check`
- Unit/integration tests: `make test`
- End-to-end tests: `make e2e`

## Deploy (prod candidate)

- backend:
  - gunicorn + uvicorn workers
  - Postgres + pgvector
- frontend:
  - Next.js build output behind reverse proxy

## Backups / retention

- Raw traces:
  - append-only storage (S3 or WORM storage in prod)
  - retention default: 90 days (config)
- Derived memories:
  - retention default: 365 days (config)

## Incident response

If a memory is identified as harmful:
1. Deprecate it (no retrieval).
2. Run policy evolution and verify outcome improvements.
3. If sensitive: hard-delete (forget) and retain tombstone audit trail.
