# Release Gate Master Checklist

Owner: Jason Lovell  
Execution mode: no-cost private repo, local-first verification  
Last updated: 2026-03-03

## Goal

Ship a release-ready MetaMemory Studio baseline with explicit reliability, security,
operational, and documentation controls that are verifiable end-to-end.

## Status Legend

- `[ ]` Not started
- `[~]` In progress
- `[x]` Completed and verified

## Track A — Governance and tracking

- [x] A1. Create this exhaustive release-gate master checklist.
- [x] A2. Define concrete verification command(s) for every engineering task in this file.
- [x] A3. Align this checklist with existing pre-release docs and avoid conflicting instructions.

## Track B — Backend reliability and API hardening

- [x] B1. Add request ID middleware and return `X-Request-ID` on every API response.
- [x] B2. Add structured request logging with request ID, method, path, status, and latency.
- [x] B3. Add import payload size limit with configurable max bytes.
- [x] B4. Add simple per-IP rate limiting for mutating endpoints (import, evolve, export, delete/deprecate).
- [x] B5. Add idempotent import behavior for duplicate trace content in same workspace.
- [x] B6. Add pagination to runs list endpoint (`limit`, `offset`) with deterministic ordering.
- [x] B7. Add pagination to memory list endpoint (`limit`, `offset`) with deterministic ordering.
- [x] B8. Add explicit API error envelope for common failure cases in new code paths.

## Track C — Tests and quality coverage

- [x] C1. Add API tests for request ID response header behavior.
- [x] C2. Add API tests for import payload limit rejection.
- [x] C3. Add API tests for idempotent import behavior.
- [x] C4. Add API tests for runs pagination behavior.
- [x] C5. Add API tests for memory pagination behavior.
- [x] C6. Add API tests for rate limiting behavior.
- [x] C7. Ensure all existing tests still pass with no regressions.

## Track D — Ops automation and release tooling

- [x] D1. Add local `scripts/release_gate.sh` to run end-to-end release checks.
- [x] D2. Add DB backup script.
- [x] D3. Add DB restore script.
- [x] D4. Add retention cleanup script for stale/deleted artifacts.
- [x] D5. Add SBOM generation script for backend/frontend dependencies.
- [x] D6. Wire Makefile targets for new ops scripts where appropriate.

## Track E — Documentation for release operations

- [x] E1. Add dependency/vulnerability policy doc with triage and SLA.
- [x] E2. Add threat model doc tied to current architecture and controls.
- [x] E3. Add incident response doc with severity levels and response flow.
- [x] E4. Add rollback doc with concrete rollback commands.
- [x] E5. Update runbook with new scripts and release gate workflow.
- [x] E6. Update release checklist to reflect current no-cost/private execution reality.

## Track F — Final release-gate completion

- [x] F1. Run backend checks and tests clean.
- [x] F2. Run frontend checks/tests/e2e clean.
- [x] F3. Run release gate script clean.
- [x] F4. Mark every checklist item complete with no open gaps.
- [x] F5. Provide completion summary with verification evidence.

## Verification commands

- Backend quality: `cd backend && uv run ruff check . && uv run ruff format --check . && uv run mypy . && uv run pytest -q`
- Frontend quality: `cd frontend && pnpm lint && pnpm typecheck && pnpm test && pnpm e2e`
- Full project: `make verify`
- Release gate (new): `./scripts/release_gate.sh`

## Verification evidence (2026-03-03)

- `make release-gate` completed successfully.
- `make verify` completed successfully.
- Backend tests: `57 passed`.
- Frontend unit tests: `11 passed`.
- Frontend E2E tests: `11 passed`.
