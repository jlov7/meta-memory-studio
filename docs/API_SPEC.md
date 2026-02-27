# API spec (current MVP)

Base URL: `/api`

## Health and integrity
- GET `/health`
- GET `/workspaces/{workspace_id}/integrity`
  - verifies raw hash-chain integrity for all imported files in a workspace

## Workspaces
- GET `/workspaces`
- POST `/workspaces`
  - body: `{ "name": string }`

## Import
- POST `/workspaces/{workspace_id}/import`
  - multipart upload with `file` (`.jsonl`)
  - response includes counts: `event_count`, `run_count`, `memory_count`, plus `raw_file_id`
- POST `/workspaces/{workspace_id}/import/demo`
  - imports bundled sample trace

## Runs
- GET `/workspaces/{workspace_id}/runs`
- GET `/workspaces/{workspace_id}/runs/{run_id}`
  - returns timeline-expanded run detail

## Memory
- GET `/workspaces/{workspace_id}/memory`
  - query params:
    - `q` (search text)
    - `status` (`active` default)
    - `memory_type`
- GET `/workspaces/{workspace_id}/memory/themes`
- GET `/workspaces/{workspace_id}/memory/{memory_id}`
- PATCH `/workspaces/{workspace_id}/memory/{memory_id}/deprecate`
- DELETE `/workspaces/{workspace_id}/memory/{memory_id}`
  - hard-delete (forget with tombstone semantics)

## Policy / evolution
- POST `/workspaces/{workspace_id}/policy/evolve`
  - creates contribution events and applies weight updates

## Drift
- GET `/workspaces/{workspace_id}/drift`
  - statistical anomaly report (tool-usage drift)

## Export
- POST `/workspaces/{workspace_id}/export/review-pack`
  - returns ZIP stream (`summary.md`, `memories.json`, `weight_history.json`) with PII-redacted text fields
