#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

DB_PATH="${1:-backend/metamemory.db}"
BACKUP_DIR="${2:-backups/db}"
TIMESTAMP="$(date +"%Y%m%d_%H%M%S")"

mkdir -p "$BACKUP_DIR"

if [[ ! -f "$DB_PATH" ]]; then
  echo "[db-backup] Database file not found: $DB_PATH" >&2
  exit 1
fi

DEST="$BACKUP_DIR/metamemory_${TIMESTAMP}.db"
cp "$DB_PATH" "$DEST"

if command -v shasum >/dev/null 2>&1; then
  shasum -a 256 "$DEST" > "$DEST.sha256"
fi

echo "[db-backup] Backup created: $DEST"
if [[ -f "$DEST.sha256" ]]; then
  echo "[db-backup] Checksum: $DEST.sha256"
fi
