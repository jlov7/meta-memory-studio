# MetaMemory Studio — Claude Code Instructions

This file is read automatically by Claude Code at session start. It captures project-specific conventions, invariants, and working notes that apply to every AI-assisted session in this repo.

---

## Project Summary

**MetaMemory Studio** is a full-stack "memory-of-memory" control plane for agentic AI systems. It ingests JSONL trace files, extracts learned memories, scores their contribution to agent performance, and provides a UI to govern, debug, and export them.

- **Backend**: Python 3.11+ · FastAPI · SQLModel · SQLite FTS5 · Alembic
- **Frontend**: Next.js 16 · React 19 · TypeScript · TanStack Query · Tailwind · Recharts
- **Package managers**: `uv` (Python) · `pnpm` (Node)
- **Test runners**: pytest (backend) · Vitest (frontend) · Playwright (E2E)

---

## Development Commands

```bash
make install   # install all deps (backend + frontend)
make dev       # start both servers (backend :8000, frontend :3000)
make demo      # import demo trace, shows data in UI
make check     # lint + typecheck (ruff, mypy strict, eslint, tsc)
make test      # unit + integration tests (pytest + vitest)
make e2e       # Playwright E2E tests
```

**Always run `make check` before marking a task complete.**

---

## Key File Locations

| Area | Key Files |
|---|---|
| API routing | `backend/app/api/router.py` — mounts all sub-routers |
| Domain config | `backend/app/config.py` — pydantic-settings, feature flags |
| DB session | `backend/app/database.py` — `get_db()` dependency |
| Models | `backend/app/models/` — `raw.py`, `runs.py`, `memory.py` |
| Schemas | `backend/app/schemas/` — all Pydantic request/response types |
| Ingest pipeline | `backend/app/ingest/pipeline.py` |
| Memory construction | `backend/app/memory/constructor.py` |
| Theme clustering | `backend/app/memory/themes.py` |
| FTS5 search | `backend/app/memory/retrieval.py` |
| Drift detection | `backend/app/eval/drift.py` |
| Export endpoint | `backend/app/api/export.py` |
| Weight updates | `backend/app/policy/weight_updater.py` |
| Test fixtures | `backend/tests/conftest.py` |
| TypeScript types | `frontend/src/types/api.ts` |
| API client | `frontend/src/lib/api.ts` |
| Query keys | `frontend/src/lib/query-keys.ts` |
| Utilities | `frontend/src/lib/utils.ts` (`cn()`, `formatDate()`) |
| Demo trace | `examples/sample_traces/demo_runs.jsonl` |

---

## Architecture Invariants

These must never be violated:

1. **Raw trace store is immutable.** Never `UPDATE` or `DELETE` from `raw_events` or `raw_files`.
2. **Hash chain is append-only.** `h0 = sha256(file_header)`, `hi = sha256(h_prev_hex + canonical(event_i))`. Breaking the chain is a data integrity failure.
3. **PII is redacted in memory layer.** The `memory_items.content` field must never contain email addresses, phone numbers, or SSNs. Detection runs in `app/ingest/pii.py` and redaction in `app/api/export.py`.
4. **Weight updates are deterministic.** Formula: `w_new = clamp(w_old + 0.1 × δ, 0.0, 10.0)`. Never change the learning rate without updating tests.
5. **IDs are UUIDv7.** Use `uuid_utils.uuid7()` for all new IDs. Demo trace uses `uuid5(NAMESPACE_URL, title)` for deterministic IDs that survive re-import.
6. **DB access via dependency injection.** Always use `Session = Depends(get_db)` in API handlers. Never use module-level globals.
7. **Schemas, not dicts.** All API responses must be Pydantic models (`response_model=...`). Never return raw dicts from route handlers.

---

## Adding an Endpoint (Checklist)

When asked to add a new API endpoint:

1. `backend/app/schemas/` — define request/response Pydantic models
2. `backend/app/api/` — create or extend a route file; keep handlers thin
3. `backend/app/api/router.py` — mount the new router
4. `backend/tests/` — write pytest tests using the `client` fixture
5. `frontend/src/types/api.ts` — add matching TypeScript interfaces
6. `frontend/src/lib/api.ts` — add typed fetch wrapper
7. `frontend/src/lib/query-keys.ts` — add query key factory if needed
8. Run `make check && make test` to verify

---

## Adding a Frontend Page (Checklist)

1. Create `frontend/src/app/{path}/page.tsx` with App Router conventions
2. Mark as `"use client"` if using hooks or browser APIs
3. Use TanStack Query (`useQuery`) for data fetching — **never** `useEffect` for data
4. Use `cn()` for conditional Tailwind classes
5. Provide a skeleton (`Skeleton` component) during loading
6. Provide an empty state (`EmptyState` component) when no data
7. Add an E2E test for the happy path in `frontend/e2e/`

---

## Testing Guidelines

- Backend: `uv run pytest -q` — test files in `backend/tests/`
- Frontend unit: `pnpm test` — Vitest
- E2E: `pnpm e2e` — Playwright against live servers
- **Each test must be independent.** Backend tests use an in-memory DB reset per test.
- E2E tests create their own workspace via `POST /api/workspaces`.
- PII tests: use real PII patterns (`john@example.com`, `+1-555-867-5309`) — these are for testing the redaction logic.

---

## Styling Conventions

```css
/* Color palette (Tailwind custom tokens) */
--bg:          #0d0d0f   /* page background */
--surface:     #141418   /* card/panel surface */
--border:      #1e1e24   /* borders */
--accent:      indigo-500 (6366f1)   /* interactive elements */
--text:        slate-100  /* primary text */
--muted:       slate-400  /* secondary text */
--success:     emerald-500
--warning:     amber-400
--error:       red-500
```

- Dark-first: every component must look correct without a light mode override
- Dense but readable — observability tool aesthetic, not a marketing site
- Fonts: Inter for UI text, JetBrains Mono for code/JSON
- `data-testid` attributes only when ARIA role/label selectors are insufficient

---

## Feature Flags

Controlled via environment variables (see `.env.example`):

| Flag | Default | Effect |
|---|---|---|
| `ENABLE_MEMORY_CONSTRUCTION` | `true` | `memory_write_candidate` events → `MemoryItem` rows |
| `ENABLE_EVOLUTION` | `true` | Weight updates via `POST /evolve` |

Check with `settings.enable_memory_construction` (pydantic-settings, auto-loaded from env).

---

## Common Pitfalls

- **`/memory/themes` MUST be declared before `/{memory_id}`** in the FastAPI router — otherwise FastAPI matches `themes` as a memory ID.
- **Alembic `--autogenerate` does NOT detect FTS5 virtual tables.** Use `op.execute(raw_sql)` for FTS5 creation/triggers.
- **`uuid_utils` vs `uuid`**: Import `uuid_utils` for `uuid7()` and `uuid5()`. Standard library `uuid` is for `NAMESPACE_URL` only.
- **TanStack Query conditional fetching**: `enabled: !!workspaceId` pattern — never pass `undefined` to a query function.
- **Streaming response (export)**: Use `fastapi.responses.StreamingResponse` with `io.BytesIO` — don't buffer large zips in memory.

---

## Session Workflow

When starting a new session:

1. Read this file ✓ (automatic)
2. Read `backend/tests/conftest.py` to understand the test setup
3. Run `make check` to see current state
4. Read the relevant domain module before editing it

When finishing a session:

1. Run `make check && make test`
2. Note any TODOs or in-progress work at the bottom of this file

---

## In-Progress Notes

> Use this section during sessions to track state across compactions.

<!-- Session notes go here. Clear after committing. -->
