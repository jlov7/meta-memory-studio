#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

OUT_DIR="${1:-sbom}"
mkdir -p "$OUT_DIR"

if command -v syft >/dev/null 2>&1; then
  echo "[sbom] syft detected, generating CycloneDX SBOMs"
  syft "dir:$ROOT_DIR/backend" -o cyclonedx-json > "$OUT_DIR/backend.cdx.json"
  syft "dir:$ROOT_DIR/frontend" -o cyclonedx-json > "$OUT_DIR/frontend.cdx.json"
else
  echo "[sbom] syft not found; generating dependency manifests"
  (
    cd backend
    uv export --format requirements-txt --no-hashes > "$ROOT_DIR/$OUT_DIR/backend-requirements.txt"
  )
  (
    cd frontend
    pnpm list --prod --json > "$ROOT_DIR/$OUT_DIR/frontend-deps.json"
  )
fi

echo "[sbom] artifacts written to $OUT_DIR"
