# Architecture — MetaMemory Studio

## Overview

Two layers:
1) **Raw Trace Store** (immutable, append-only):
   - stores ingested JSONL events verbatim
   - hashed + chained per file (tamper-evident)
2) **Derived Memory Layer** (mutable, queryable):
   - episodes, steps, tool calls, outcomes
   - experience bank + meta-guideline bank
   - retrieval events and contribution metrics
   - weight updates & forgetting decisions

## Core pipeline

### Ingest
- Accept JSONL (drag/drop UI → backend upload)
- Validate → persist raw events → compute trace hash chain

### Normalize
- Parse events into a canonical internal event schema:
  - timestamps normalized to ISO8601
  - deterministic IDs (UUIDv7 recommended)
  - tool calls normalized

### Episode reconstruction
- Group events into:
  - Workspace → Run → Episode → Step
- Extract:
  - user intents
  - tool calls and results
  - errors and retries
  - outcome signals
  - human feedback (if present)

### Memory construction
Create candidate memories:
- Experiences: “situation → actions → outcome → lesson”
- Guidelines: “if X, do Y; avoid Z”
- Facts/preferences: user/team constraints

### Retrieval
For a new task (or analysis run):
- Generate retrieval query
- Retrieve top candidates (weighted)
- (Optional) de-dup / hierarchical retrieval:
  - theme → episode → raw messages
- Compile into a task-specific guideline

### Contribution measurement
- Run baseline prompt vs memory-guided prompt
- Score outputs:
  - heuristic (day 1): exact match or rules
  - optional judge LLM (config flag)
- Attribute contribution to retrieved memories

### Update
- Update experience weights:
  - reinforce helpful
  - decay harmful/stale
- Log all updates as immutable “policy events”

## Backend modules

- `ingest/` : upload, validation, raw storage
- `parser/` : adapters for trace formats
- `memory/` : banks, retrieval, compilation
- `eval/` : scoring, baseline vs memory-guided
- `policy/` : weight update rules, retention, deletion
- `api/` : FastAPI routes + SSE

## Frontend architecture

- Next.js App Router
- Pages:
  - / (landing)
  - /workspaces/:id
  - /runs/:id
  - /memory/:id
  - /health
- Shared:
  - command palette
  - timeline component
  - diff viewer component
  - charts (lightweight)

## Storage

Dev:
- SQLite with FTS5 for search
- Embeddings stored as BLOB/JSON arrays; simple cosine search OK for MVP

Prod option:
- Postgres + pgvector
- Row-level security (multi-tenant)

## Integrity and audit

- Raw events are stored with a hash chain:
  - `h0 = sha256(file_header)`
  - `hi = sha256(hi-1 || canonical(event_i))`
- Derived tables reference raw events by `(raw_file_id, line_no)`.

## Privacy

- PII tags per event and per memory item.
- Redaction view generates a “Public export” (no raw payloads by default).

