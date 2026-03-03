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
- Full release gate: `make release-gate`

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
- Local DB backup:
  - `make db-backup`
  - default source: `backend/metamemory.db`
  - output: `backups/db/metamemory_<timestamp>.db`
- Local DB restore:
  - `make db-restore BACKUP=backups/db/<file>.db`
  - auto-creates pre-restore snapshot
- Local retention cleanup:
  - dry-run: `make cleanup-retention`
  - destructive mode: `DRY_RUN=false make cleanup-retention`
  - configurable: `BACKUP_RETENTION_DAYS`, `ARTIFACT_RETENTION_DAYS`
- Dependency manifest/SBOM:
  - `make sbom`
  - output: `sbom/`

## Incident response

If a memory is identified as harmful:
1. Deprecate it (no retrieval).
2. Run policy evolution and verify outcome improvements.
3. If sensitive: hard-delete (forget) and retain tombstone audit trail.

## Release operations references

- Dependency policy: `docs/DEPENDENCY_POLICY.md`
- Threat model: `docs/THREAT_MODEL.md`
- Incident response: `docs/INCIDENT_RESPONSE.md`
- Rollback guide: `docs/ROLLBACK.md`
