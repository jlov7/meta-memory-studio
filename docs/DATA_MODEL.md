# Data model

This spec describes the minimum schema for MVP.

## Raw

### raw_files
- id (pk)
- workspace_id
- filename
- imported_at
- sha256_head (final hash)
- event_count

### raw_events
- id (pk)
- raw_file_id
- line_no
- ts
- type
- payload_json (text)
- prev_hash
- hash

## Runs / episodes

### runs
- id (pk)
- workspace_id
- started_at
- ended_at
- status (success|fail|unknown)
- agent_name
- metadata_json

### episodes
- id (pk)
- run_id
- title
- summary
- outcome_label
- friction_score (int)
- created_at

### steps
- id (pk)
- episode_id
- idx
- kind (message|tool|memory|eval|other)
- ts
- title
- details_json
- raw_event_refs_json

### tool_calls
- id (pk)
- step_id
- tool_name
- args_json
- result_json
- error_json
- latency_ms

## Memory

### memory_items
- id (pk)
- workspace_id
- type (experience|guideline|fact)
- title
- content_md
- content_json
- created_at
- updated_at
- status (active|deprecated|deleted)
- pii_level (none|low|high)
- ttl_days (nullable)
- pinned (bool)

### memory_sources
- id (pk)
- memory_item_id
- episode_id
- step_id (nullable)
- rationale

### retrieval_events
- id (pk)
- run_id
- ts
- query_text
- candidates_json
- selected_memory_ids_json
- retrieval_latency_ms

### contribution_events
- id (pk)
- run_id
- ts
- baseline_score
- memory_score
- delta
- rubric_json
- selected_memory_ids_json

### weight_updates
- id (pk)
- memory_item_id
- ts
- prev_weight
- new_weight
- reason
- evidence_json

## Indexes
- FTS on memory_items.title/content_md
- (workspace_id, created_at) on memory_items
- (run_id, ts) on steps, retrieval_events

