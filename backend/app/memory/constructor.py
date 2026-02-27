"""Construct MemoryItem rows from memory_write_candidate events."""

import uuid

from app.models.memory import MemoryItem, MemorySource

# Deterministic namespace for demo trace IDs
DEMO_NAMESPACE = uuid.UUID("6ba7b811-9dad-11d1-80b4-00c04fd430c8")  # NAMESPACE_URL


def deterministic_id(workspace_id: str, title: str) -> str:
    """Generate deterministic UUID5 scoped to workspace and title."""
    return str(uuid.uuid5(DEMO_NAMESPACE, f"{workspace_id}:{title}"))


def construct_memories(
    workspace_id: str,
    events: list[dict],  # type: ignore[type-arg]
    raw_event_ids: list[str],
    run_ids_by_external: dict[str, str],
) -> tuple[list[MemoryItem], list[MemorySource]]:
    """Process memory_write_candidate events into MemoryItem + MemorySource rows."""
    items: list[MemoryItem] = []
    sources: list[MemorySource] = []

    for event, raw_id in zip(events, raw_event_ids, strict=True):
        if event.get("type") != "memory_write_candidate":
            continue

        payload = event.get("payload", {})
        title = payload.get("title", "")
        content = payload.get("content", "") or payload.get("lesson", "")
        memory_type = payload.get("memory_type", "") or payload.get("kind", "episodic")
        # run_id can be top-level or nested under source
        run_ext_id = payload.get("run_id", "")
        if not run_ext_id:
            source_ref = payload.get("source", {})
            run_ext_id = source_ref.get("run_id", "") if isinstance(source_ref, dict) else ""

        # Use deterministic ID so demo trace retrieval events can reference it
        mem_id = deterministic_id(workspace_id, title)

        item = MemoryItem(
            id=mem_id,
            workspace_id=workspace_id,
            title=title,
            content=content,
            memory_type=memory_type,
        )
        items.append(item)

        run_id = run_ids_by_external.get(run_ext_id, "")
        source = MemorySource(
            memory_item_id=mem_id,
            run_id=run_id,
            raw_event_id=raw_id,
            source_type="write_candidate",
        )
        sources.append(source)

    return items, sources
