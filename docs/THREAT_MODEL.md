# Threat Model

## System context

MetaMemory Studio ingests agent trace JSONL files, derives memory artifacts, and exposes read/write APIs and exports for analysis.

## Trust boundaries

- Boundary A: Client/browser to API (`/api/*`)
- Boundary B: API to SQLite persistence layer
- Boundary C: Export generation boundary (memory content leaves system as ZIP)
- Boundary D: CI/dependency boundary (third-party package supply chain)

## Critical assets

- Raw trace integrity (`raw_files`, `raw_events`, hash chain)
- Memory content confidentiality (`memory_items.content`)
- Workspace isolation integrity (`workspace_id` boundaries)
- Operational availability (import/evolve/export endpoints)

## Primary threat scenarios

1. Tampered traces bypass integrity guarantees
- Risk: false memories, corrupted evaluation outcomes
- Control: append-only raw events and hash chain verification endpoint

2. PII leakage in memory content or export artifacts
- Risk: privacy breach and unsafe sharing
- Control: ingest PII detection + export redaction regex policy

3. Cross-workspace data leakage via ID enumeration
- Risk: unauthorized data access
- Control: workspace checks in API handlers and schema-bound responses

4. Endpoint abuse / request flooding
- Risk: resource exhaustion and degraded UX
- Control: per-IP rate limiting on mutating endpoints

5. Oversized import payload abuse
- Risk: memory/CPU pressure and denial of service
- Control: configurable import byte limit with explicit 413 error

6. Dependency supply-chain vulnerabilities
- Risk: remote code execution/data exfiltration through vulnerable packages
- Control: lockfiles, security workflow scans, dependency policy SLA

## Residual risks and planned hardening

- Authentication/authorization is currently out of scope for local/private mode.
- In-memory rate limiter is single-process and not distributed.
- PII detection is regex-based and may miss uncommon patterns.

## Validation checks

- `GET /api/workspaces/{id}/integrity` returns `all_valid=true`
- API tests cover rate limiting, payload limits, and duplicate ingest behavior
- Release gate includes lint, typecheck, unit/integration, and E2E checks
