#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <backup_file> [target_db_path]" >&2
  exit 1
fi

BACKUP_FILE="$1"
TARGET_DB_PATH="${2:-backend/metamemory.db}"

if [[ ! -f "$BACKUP_FILE" ]]; then
  echo "[db-restore] Backup file not found: $BACKUP_FILE" >&2
  exit 1
fi

mkdir -p "$(dirname "$TARGET_DB_PATH")"

if [[ -f "$TARGET_DB_PATH" ]]; then
  PRE_RESTORE="${TARGET_DB_PATH}.pre_restore.$(date +"%Y%m%d_%H%M%S")"
  cp "$TARGET_DB_PATH" "$PRE_RESTORE"
  echo "[db-restore] Pre-restore backup written: $PRE_RESTORE"
fi

cp "$BACKUP_FILE" "$TARGET_DB_PATH"

echo "[db-restore] Restored $BACKUP_FILE -> $TARGET_DB_PATH"
