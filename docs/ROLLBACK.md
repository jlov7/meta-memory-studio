# Rollback Guide

## Preconditions

- Identify the target commit/tag to revert to.
- Ensure a current DB backup exists: `make db-backup`.
- Confirm no write-heavy operations are running.

## Code rollback

1. Check current state:
- `git status`
- `git log --oneline -n 10`

2. Roll back non-destructively (recommended):
- `git revert <bad_commit_sha>`
- For multiple commits: `git revert --no-commit <oldest_sha>^..<newest_sha>` then commit

3. Verify rollback:
- `make check && make test`
- Run targeted `make e2e` if UI/API behavior changed

## Database rollback (SQLite)

1. Create safety snapshot of current DB:
- `make db-backup`

2. Restore a known-good backup:
- `make db-restore BACKUP=backups/db/<backup-file>.db`

3. Restart services and validate:
- `make dev` (or restart backend/frontend processes)
- Smoke test health/import/list/export flows

## Recovery validation checklist

- `GET /api/health` returns `ok`
- Demo import succeeds
- Runs and memory lists return expected counts
- Integrity endpoint reports `all_valid=true`

## Notes

- Prefer `git revert` over history rewrites for shared branches.
- Never use destructive reset commands for release rollback on collaborative branches.
