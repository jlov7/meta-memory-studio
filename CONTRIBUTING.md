# Contributing to MetaMemory Studio

Thank you for your interest in contributing. This document explains how to get from idea → merged PR in the least amount of friction.

---

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Ways to Contribute](#ways-to-contribute)
- [Development Environment](#development-environment)
- [Architecture Overview](#architecture-overview)
- [Making Changes](#making-changes)
  - [Backend (Python)](#backend-python)
  - [Frontend (TypeScript)](#frontend-typescript)
  - [Adding a New API Endpoint](#adding-a-new-api-endpoint)
  - [Adding a New Frontend Page](#adding-a-new-frontend-page)
- [Testing](#testing)
  - [Unit & Integration Tests](#unit--integration-tests)
  - [E2E Tests](#e2e-tests)
  - [Quality Gate](#quality-gate)
- [Commit Style](#commit-style)
- [Pull Request Process](#pull-request-process)
- [Project Decisions](#project-decisions)

---

## Code of Conduct

Be excellent to each other. We enforce the [Contributor Covenant](https://www.contributor-covenant.org/version/2/1/code_of_conduct/) — discrimination, harassment, and disrespect have no place here. Report violations to the maintainers.

---

## Ways to Contribute

| Type | How |
|---|---|
| Bug report | Open a GitHub Issue with steps to reproduce, expected vs actual |
| Feature request | Open a GitHub Discussion first — design before code |
| Bug fix | Fork → branch → fix → tests → PR |
| New feature | Discussion → agreement on design → implementation PR |
| Documentation | Edit files in `docs/` or `README.md` — clarity is a feature |
| Performance | Benchmark before and after, include numbers in PR description |
| Security | **Do not open a public issue.** Email `security@metamemory.dev` |

---

## Development Environment

### Prerequisites

| Tool | Version | Notes |
|---|---|---|
| Python | ≥ 3.11 | via `pyenv` or system |
| `uv` | latest | `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| Node.js | ≥ 22 | via `fnm` or `nvm` |
| `pnpm` | ≥ 9 | `npm i -g pnpm` or `corepack enable` |
| Git | any | |

### First-Time Setup

```bash
# Clone
git clone https://github.com/your-org/metamemory-studio.git
cd metamemory-studio

# Copy environment config
cp .env.example .env

# Install everything and start both servers
make install
make dev
```

`make dev` starts:
- Backend at **http://localhost:8000** (FastAPI + auto-reload)
- Frontend at **http://localhost:3000** (Next.js + HMR)

To load demo data:

```bash
make demo
```

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│  Frontend  (Next.js / React / TanStack Query)               │
│  localhost:3000                                             │
└───────────────────────────┬─────────────────────────────────┘
                            │ HTTP / JSON
┌───────────────────────────▼─────────────────────────────────┐
│  Backend  (FastAPI / SQLModel / SQLite FTS5)                │
│  localhost:8000                                             │
│                                                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │  ingest/ │  │ parser/  │  │ memory/  │  │  eval/   │   │
│  │ validate │→ │normalize │→ │construct │→ │  score   │   │
│  │   hash   │  │ episodes │  │  themes  │  │ compare  │   │
│  │   pii    │  │  steps   │  │ retrieve │  │  drift   │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  SQLite: raw_events · runs · episodes · memory_items  │  │
│  │          weight_updates · contribution_events · FTS5  │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

Key design invariants:
- **Raw Trace Store is immutable.** Once ingested, events are never modified.
- **Hash chain is append-only.** Each event hashes the previous event's hash; break a link → integrity fail.
- **PII is detected at ingest** and never stored in memory items (only in raw store with `pii_flag=true`).
- **Memory weights are deterministic.** Same inputs always produce the same weight update: `w_new = clamp(w_old + 0.1 × δ, 0.0, 10.0)`.

---

## Making Changes

### Fork and Branch

```bash
# Fork on GitHub, then:
git clone https://github.com/YOUR_USERNAME/metamemory-studio.git
cd metamemory-studio
git remote add upstream https://github.com/your-org/metamemory-studio.git

# Create a feature branch
git checkout -b feat/my-feature
# or for bugs:
git checkout -b fix/issue-123-describe-bug
```

Branch naming: `feat/`, `fix/`, `docs/`, `refactor/`, `test/`, `chore/`

---

### Backend (Python)

The backend lives in `backend/`. All commands run from there with `uv run`:

```bash
cd backend

# Run the server
uv run uvicorn app.main:app --reload

# Lint (ruff)
uv run ruff check .
uv run ruff format --check .

# Type check (mypy strict)
uv run mypy .

# Run all tests
uv run pytest -q

# Run a single test file
uv run pytest tests/test_ingest.py -v

# Run tests matching a pattern
uv run pytest -k "test_pii" -v
```

**Conventions:**
- All new modules need `__init__.py`
- API handlers live in `app/api/` — keep them thin (delegate to modules)
- Business logic in `app/{domain}/` (ingest, memory, eval, policy)
- Schemas (Pydantic) in `app/schemas/` — never use raw dicts in responses
- No `print()` — use Python `logging`
- All DB access via `Session` dependency — never use globals

**When to write a migration:**

Any change to a SQLModel table class requires an Alembic migration:

```bash
cd backend
uv run alembic revision --autogenerate -m "describe the change"
# Review the generated file in alembic/versions/ before committing
```

---

### Frontend (TypeScript)

The frontend lives in `frontend/`. All commands with `pnpm`:

```bash
cd frontend

# Dev server
pnpm dev

# Type check
pnpm typecheck

# Lint
pnpm lint

# Build (catches all type errors)
pnpm build

# Run unit tests (Vitest)
pnpm test

# Run E2E (Playwright)
pnpm e2e
```

**Conventions:**
- Pages in `src/app/` using Next.js App Router
- Components in `src/components/{domain}/`
- All API calls go through `src/lib/api.ts` — never raw `fetch` in components
- Data fetching via TanStack Query hooks — no `useEffect` for data fetching
- TypeScript strict mode — no `any`, no `!` non-null assertions without comment
- Tailwind for all styling — no inline styles, no CSS modules
- `cn()` utility for conditional classes (from `src/lib/utils.ts`)

---

### Adding a New API Endpoint

1. **Define the schema** in `backend/app/schemas/`:

```python
# app/schemas/myfeature.py
from pydantic import BaseModel

class MyFeatureOut(BaseModel):
    id: str
    name: str
```

2. **Implement the logic** in the appropriate domain module:

```python
# app/myfeature/service.py
from sqlmodel import Session
from app.models.memory import MemoryItem

def do_thing(db: Session, workspace_id: str) -> MyFeatureOut:
    ...
```

3. **Add the route** in `backend/app/api/`:

```python
# app/api/myfeature.py
from fastapi import APIRouter, Depends
from app.database import get_db
from app.schemas.myfeature import MyFeatureOut

router = APIRouter(prefix="/workspaces/{workspace_id}/myfeature", tags=["myfeature"])

@router.get("", response_model=MyFeatureOut)
def get_myfeature(workspace_id: str, db: Session = Depends(get_db)) -> MyFeatureOut:
    return do_thing(db, workspace_id)
```

4. **Mount the router** in `app/api/router.py`

5. **Write tests** in `backend/tests/test_myfeature.py`

6. **Update TypeScript types** in `frontend/src/types/api.ts`

7. **Add API wrapper** in `frontend/src/lib/api.ts`

---

### Adding a New Frontend Page

1. Create the page at the correct App Router path:

```
src/app/workspaces/[id]/myfeature/page.tsx
```

2. Fetch data using TanStack Query:

```tsx
// src/app/workspaces/[id]/myfeature/page.tsx
"use client";

import { useQuery } from "@tanstack/react-query";
import { getMyFeature } from "@/lib/api";
import { queryKeys } from "@/lib/query-keys";

export default function MyFeaturePage({ params }: { params: { id: string } }) {
  const { data, isLoading } = useQuery({
    queryKey: queryKeys.myfeature(params.id),
    queryFn: () => getMyFeature(params.id),
  });

  if (isLoading) return <MySkeleton />;
  return <MyFeatureView data={data} />;
}
```

3. Add the query key factory to `src/lib/query-keys.ts`

4. Add navigation to `src/components/layout/sidebar.tsx` if needed

5. Add an E2E test for the happy path

---

## Testing

### Unit & Integration Tests

Every PR must maintain or improve test coverage. New features need tests; bug fixes need a regression test.

**Test file locations:**

| What | Where |
|---|---|
| Backend unit tests | `backend/tests/test_{module}.py` |
| Backend integration | `backend/tests/test_api.py` |
| Frontend unit | `frontend/src/**/__tests__/` |
| E2E | `frontend/e2e/*.spec.ts` |

**Backend test fixtures** (in `backend/tests/conftest.py`):
- `client` — an httpx `TestClient` with an in-memory SQLite database
- Database is reset between each test

**Example backend test:**

```python
def test_my_feature(client):
    ws = client.post("/api/workspaces", json={"name": "Test WS"}).json()
    resp = client.get(f"/api/workspaces/{ws['id']}/myfeature")
    assert resp.status_code == 200
    data = resp.json()
    assert "id" in data
```

**Example frontend test (Vitest):**

```typescript
import { render, screen } from "@testing-library/react";
import { MyComponent } from "../MyComponent";

test("renders correctly", () => {
  render(<MyComponent value="hello" />);
  expect(screen.getByText("hello")).toBeInTheDocument();
});
```

---

### E2E Tests

E2E tests run against live backend + frontend. Start both servers first, or use `pnpm e2e` which handles `webServer` via Playwright config.

```bash
# Run all E2E tests
cd frontend && pnpm e2e

# Run a specific spec
pnpm e2e e2e/smoke.spec.ts

# Run headed (watch the browser)
pnpm e2e --headed

# Debug mode (step-by-step)
pnpm e2e --debug
```

E2E tests should:
- Be independent (each test creates its own workspace)
- Test user-visible behavior, not implementation details
- Use `data-testid` attributes only when ARIA selectors are insufficient

---

### Quality Gate

Before opening a PR, run the full quality gate:

```bash
make check   # ruff + mypy + eslint + tsc (no warnings allowed)
make test    # pytest + vitest (all pass)
make e2e     # Playwright (all pass)
```

**The CI will reject your PR if any of these fail.**

If you're adding a new `make` target, keep it composable:

```makefile
myfeature: check-myfeature test-myfeature
```

---

## Commit Style

We follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <imperative summary>

[optional body explaining WHY, not what]

Co-Authored-By: Your Name <you@example.com>
```

**Types:** `feat`, `fix`, `docs`, `refactor`, `test`, `chore`, `perf`, `ci`

**Scope:** optional, matches the module or area: `ingest`, `memory`, `drift`, `export`, `ui`, `tests`

**Examples:**

```
feat(memory): add Jaccard theme clustering for hierarchical retrieval

Naive search returns duplicate memories from the same theme.
Cluster at ingest time using Jaccard on word tokens so retrieval
returns at most one memory per theme.

fix(ingest): handle BOM in UTF-8 JSONL files

Several AI systems prepend a UTF-8 BOM to their trace output.
Strip before JSON parsing to avoid decode errors.

docs: add CONTRIBUTING.md with full setup guide
```

Rules:
- Summary in imperative mood ("add", not "added" or "adds")
- ≤ 72 characters in the summary line
- Body explains WHY, not what (the diff shows what)
- One logical change per commit — prefer small, focused commits
- Never commit: `.env`, secrets, `*.pyc`, `__pycache__/`, `node_modules/`, database files

---

## Pull Request Process

1. **Open a Draft PR early** — this signals work-in-progress and allows early feedback

2. **Fill out the PR template completely:**

   ```markdown
   ## What does this PR do?
   One sentence.

   ## Why?
   Motivation / link to issue.

   ## How?
   Approach taken. Any alternatives considered.

   ## Testing
   - [ ] Unit tests added/updated
   - [ ] Integration tests pass
   - [ ] E2E tests pass (or not applicable, with reason)
   - [ ] `make check` clean

   ## Screenshots / recordings
   (For UI changes)
   ```

3. **Mark as Ready for Review** once:
   - All checklist items are done
   - CI is green
   - Self-reviewed the diff

4. **One approval required** to merge

5. **Squash merge** to `main` — the PR title becomes the commit message

6. **Delete the branch** after merge

---

## Project Decisions

Some decisions are deliberately fixed to maintain consistency. These are **not** up for re-discussion in PRs:

| Decision | Rationale |
|---|---|
| SQLite (not Postgres) | Zero-infrastructure dev experience; FTS5 is built-in |
| UUIDv7 IDs | Sortable by time, globally unique without coordination |
| SHA-256 hash chain | Tamper-evident trace provenance |
| `uv` for Python deps | Fastest resolver; lockfile ensures reproducibility |
| `pnpm` for Node deps | Disk-efficient; strict dependency isolation |
| TanStack Query | Caching, background refetch, server state without global store |
| Ruff + mypy strict | Fast lint + full type safety; no `type: ignore` without comment |

If you believe a decision is wrong, open a **Discussion** (not a PR) and make the case. The maintainers will engage.

---

## Questions?

- **GitHub Discussions** — design questions, feature ideas
- **GitHub Issues** — bug reports
- **Security** — `security@metamemory.dev` (private)

We read everything. Response time goal: 48 hours.
