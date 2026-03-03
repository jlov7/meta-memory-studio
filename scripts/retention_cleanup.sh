#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

BACKUP_RETENTION_DAYS="${BACKUP_RETENTION_DAYS:-30}"
ARTIFACT_RETENTION_DAYS="${ARTIFACT_RETENTION_DAYS:-14}"
DRY_RUN="${DRY_RUN:-true}"

delete_or_print() {
  local path="$1"
  if [[ "$DRY_RUN" == "true" ]]; then
    echo "[retention-cleanup] would remove: $path"
  else
    rm -rf "$path"
    echo "[retention-cleanup] removed: $path"
  fi
}

cleanup_dir() {
  local base_dir="$1"
  local age_days="$2"

  if [[ ! -d "$base_dir" ]]; then
    return
  fi

  while IFS= read -r target; do
    [[ -z "$target" ]] && continue
    delete_or_print "$target"
  done < <(find "$base_dir" -mindepth 1 -mtime +"$age_days" -print)
}

cleanup_dir "backups/db" "$BACKUP_RETENTION_DAYS"
cleanup_dir "frontend/test-results" "$ARTIFACT_RETENTION_DAYS"
cleanup_dir "frontend/playwright-report" "$ARTIFACT_RETENTION_DAYS"

echo "[retention-cleanup] complete (dry_run=$DRY_RUN)"
