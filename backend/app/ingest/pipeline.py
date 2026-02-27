"""Full ingest orchestration: validate → hash → store → parse → construct memories."""

import json

from sqlalchemy import text
from sqlmodel import Session

from app.config import settings
from app.ingest.hasher import build_chain
from app.ingest.pii import scan_events
from app.ingest.validator import validate_jsonl
from app.memory.constructor import construct_memories, deterministic_id
from app.models.memory import RetrievalEvent
from app.models.raw import RawEvent, RawFile
from app.parser.episode_builder import build_episodes
from app.parser.normalizer import normalize_event


def run_pipeline(
    session: Session,
    workspace_id: str,
    filename: str,
    content: str,
) -> dict:  # type: ignore[type-arg]
    """Run the full ingest pipeline. Returns summary dict."""
    # 1. Validate JSONL
    result = validate_jsonl(content)
    if not result.valid:
        return {"success": False, "errors": result.errors}

    events = result.events

    # 2. PII scan
    pii_level = scan_events(events)

    # 3. Hash chain — use only storable fields (sorted: payload, ts as isoformat, type)
    # so check_integrity can re-verify exactly from DB rows.
    hashable_events = [
        {
            "payload": e.get("payload", {}),
            "ts": normalize_event(e)["ts"].replace(tzinfo=None).isoformat(),
            "type": e["type"],
        }
        for e in events
    ]
    hashes = build_chain(filename, hashable_events)

    # 4. Store raw file
    raw_file = RawFile(
        workspace_id=workspace_id,
        filename=filename,
        sha256_hash=hashes[-1] if hashes else "",
        event_count=len(events),
        pii_level=pii_level,
    )
    session.add(raw_file)
    session.flush()

    # 5. Store raw events
    raw_event_ids: list[str] = []
    for i, (event, hash_val) in enumerate(zip(events, hashes, strict=True)):
        raw_event = RawEvent(
            raw_file_id=raw_file.id,
            workspace_id=workspace_id,
            line_number=event.get("_line_number", i + 1),
            event_type=event["type"],
            timestamp=normalize_event(event)["ts"],
            payload=json.dumps(event.get("payload", {})),
            hash_chain=hash_val,
        )
        session.add(raw_event)
        session.flush()
        raw_event_ids.append(raw_event.id)

    # 6. Normalize events
    normalized = [normalize_event(e) for e in events]

    # 7. Build episodes
    runs, episodes, steps, tool_calls = build_episodes(workspace_id, normalized, raw_event_ids)
    # Insert in FK dependency order to avoid intermittent SQLite FK errors
    # under concurrent imports (runs -> episodes -> steps -> tool_calls).
    for run in runs:
        session.add(run)
    session.flush()

    for episode in episodes:
        session.add(episode)
    session.flush()

    for step in steps:
        session.add(step)
    session.flush()

    for tool_call in tool_calls:
        session.add(tool_call)
    session.flush()

    # Build run ID mapping for memory constructor
    run_ids_by_external = {r.external_id: r.id for r in runs}

    # 8. Construct memories (if enabled)
    memory_items = []
    memory_sources = []
    if settings.ENABLE_MEMORY_CONSTRUCTION:
        from sqlmodel import select as sql_select

        from app.models.memory import MemoryItem

        candidate_items, candidate_sources = construct_memories(
            workspace_id, events, raw_event_ids, run_ids_by_external
        )

        # Filter out items with existing IDs (deterministic IDs enable re-import dedup)
        existing_ids: set[str] = set()
        if candidate_items:
            existing_ids = set(
                session.exec(
                    sql_select(MemoryItem.id).where(
                        MemoryItem.id.in_([m.id for m in candidate_items])  # type: ignore[attr-defined]
                    )
                ).all()
            )
        memory_items = [m for m in candidate_items if m.id not in existing_ids]
        memory_sources = [s for s in candidate_sources if s.memory_item_id not in existing_ids]

        for memory_item in memory_items:
            session.add(memory_item)
        for memory_source in memory_sources:
            session.add(memory_source)
        session.flush()

        # Sync new items to FTS index
        for item in memory_items:
            session.exec(  # type: ignore[call-overload]
                text(
                    "INSERT INTO memory_items_fts (memory_item_id, title, content) "
                    "VALUES (:mid, :title, :content)"
                ),
                params={"mid": item.id, "title": item.title, "content": item.content},
            )

        # Rebuild theme clusters
        if memory_items:
            from app.memory.themes import rebuild_themes

            rebuild_themes(session, workspace_id)

    # Build title→ID mapping for resolving demo placeholder IDs
    title_to_id: dict[str, str] = {}
    for item in memory_items:
        title_to_id[item.title] = item.id

    # 9. Process retrieval events from the trace
    from app.models.memory import MemoryItem

    current_run_external = ""
    for event, _raw_id in zip(normalized, raw_event_ids, strict=True):
        event_type = event.get("type", "")
        if event_type == "run_start":
            current_run_external = event.get("run_id", "")

        if event_type == "memory_retrieval":
            payload = event["payload"]
            run_ext_id = event.get("run_id", "") or current_run_external
            run_id = run_ids_by_external.get(run_ext_id, "")
            if not run_id:
                continue

            # Support both "candidates" (demo) and "memories_retrieved" formats
            candidates = payload.get("candidates", payload.get("memories_retrieved", []))
            for rank, mem_ref in enumerate(candidates):
                if isinstance(mem_ref, str):
                    mem_id = mem_ref
                else:
                    mem_id = mem_ref.get("memory_id", "")
                    # Resolve placeholder IDs by title if needed
                    title = mem_ref.get("title", "")
                    if title and title in title_to_id:
                        mem_id = title_to_id[title]
                    elif title:
                        mem_id = deterministic_id(workspace_id, title)

                if not mem_id:
                    continue
                if session.get(MemoryItem, mem_id) is None:
                    continue

                retrieval = RetrievalEvent(
                    memory_item_id=mem_id,
                    run_id=run_id,
                    query=payload.get("query", ""),
                    rank=rank,
                    score=mem_ref.get("score", 0.0) if isinstance(mem_ref, dict) else 0.0,
                )
                session.add(retrieval)

        if event_type == "run_end":
            current_run_external = ""

    # 10. Score runs
    from app.eval.scorer import score_run

    for run in runs:
        if run.score is None:
            run.score = score_run(run.outcome)
            session.add(run)

    session.commit()

    return {
        "success": True,
        "raw_file_id": raw_file.id,
        "event_count": len(events),
        "run_count": len(runs),
        "memory_count": len(memory_items),
        "pii_level": pii_level,
        "hash_valid": True,
        "errors": [],
    }
