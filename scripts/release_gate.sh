#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

printf "[release-gate] %s\n" "Starting full local release gate"
printf "[release-gate] %s\n" "Repository: $ROOT_DIR"

printf "\n[release-gate] Running backend checks...\n"
(
  cd backend
  uv run ruff check .
  uv run ruff format --check .
  uv run mypy .
  uv run pytest -q
)

printf "\n[release-gate] Running frontend checks...\n"
(
  cd frontend
  pnpm lint
  pnpm typecheck
  pnpm test
)

printf "\n[release-gate] Running E2E checks...\n"
(
  cd frontend
  pnpm exec playwright install --with-deps
  pnpm e2e
)

printf "\n[release-gate] All checks passed.\n"
