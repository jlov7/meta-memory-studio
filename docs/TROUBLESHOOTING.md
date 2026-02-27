# Troubleshooting

## Import fails
- Ensure the file is JSONL (one JSON object per line)
- Validate required fields:
  - `type`
  - `ts`
  - `payload`
- Use `/api/workspaces/{id}/import` response error details.

## Hash verification fails
- The raw file has been modified after import.
- Re-import the file and ensure storage is immutable.

## No memories created
- The memory construction stage may be disabled.
- Verify the pipeline flags:
  - `ENABLE_MEMORY_CONSTRUCTION`
  - `ENABLE_EVOLUTION`

## Contribution compare shows “N/A”
- Baseline vs memory-guided evaluation requires:
  - a scoring rule
  - or judge LLM enabled
- Start with demo prompts that have deterministic checks.

## UI is bland
Non-negotiable:
- Implement the layout and components in docs/UX_SPEC.md
- Add:
  - skeleton loaders
  - proper empty states
  - icons and status pills
  - diff viewer + timeline microinteractions

