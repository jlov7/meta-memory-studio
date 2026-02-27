#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOG_DIR="$ROOT_DIR/.codex/logs"
mkdir -p "$LOG_DIR"

BACK_LOG="$LOG_DIR/screenshot-backend.log"
FRONT_LOG="$LOG_DIR/screenshot-frontend.log"

cleanup() {
  if [[ -n "${BACK_PID:-}" ]]; then
    kill "$BACK_PID" >/dev/null 2>&1 || true
  fi
  if [[ -n "${FRONT_PID:-}" ]]; then
    kill "$FRONT_PID" >/dev/null 2>&1 || true
  fi
}
trap cleanup EXIT

(
  cd "$ROOT_DIR/backend"
  uv run uvicorn app.main:app --port 8000 >"$BACK_LOG" 2>&1
) &
BACK_PID=$!

(
  cd "$ROOT_DIR/frontend"
  pnpm dev --port 3000 >"$FRONT_LOG" 2>&1
) &
FRONT_PID=$!

for _ in {1..60}; do
  if curl -fsS "http://localhost:8000/api/health" >/dev/null 2>&1; then
    break
  fi
  sleep 1
done

for _ in {1..90}; do
  if curl -fsS "http://localhost:3000" >/dev/null 2>&1; then
    break
  fi
  sleep 1
done

(
  cd "$ROOT_DIR/frontend"
  node scripts/capture-readme-screenshots.mjs
)

echo "README gallery screenshots refreshed."
