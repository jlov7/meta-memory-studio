"""Hierarchical theme clustering for de-dup memory retrieval."""

import datetime
import json
import re

from sqlmodel import Session, select

from app.models.memory import MemoryItem, MemoryTheme

_STOP_WORDS = {
    "",
    "a",
    "an",
    "the",
    "of",
    "for",
    "in",
    "on",
    "to",
    "is",
    "are",
    "was",
    "were",
    "with",
    "by",
    "at",
    "from",
    "and",
    "or",
    "not",
}
_JACCARD_THRESHOLD = 0.25


def _tokenize(text: str) -> set[str]:
    return set(re.split(r"\W+", text.lower())) - _STOP_WORDS


def _jaccard(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def rebuild_themes(db: Session, workspace_id: str) -> None:
    """Recluster all active memories in workspace by title Jaccard similarity."""
    memories = list(
        db.exec(
            select(MemoryItem)
            .where(MemoryItem.workspace_id == workspace_id)
            .where(MemoryItem.status == "active")
        ).all()
    )

    # Remove stale themes
    stale = list(db.exec(select(MemoryTheme).where(MemoryTheme.workspace_id == workspace_id)).all())
    for t in stale:
        db.delete(t)
    db.flush()

    if not memories:
        db.commit()
        return

    tokens = {m.id: _tokenize(m.title) for m in memories}
    unclustered = list(memories)
    clusters: list[list[MemoryItem]] = []

    while unclustered:
        seed = unclustered.pop(0)
        cluster = [seed]
        remaining: list[MemoryItem] = []
        for m in unclustered:
            if _jaccard(tokens[seed.id], tokens[m.id]) >= _JACCARD_THRESHOLD:
                cluster.append(m)
            else:
                remaining.append(m)
        unclustered = remaining
        clusters.append(cluster)

    for cluster in clusters:
        rep = max(cluster, key=lambda m: m.current_weight)
        theme = MemoryTheme(
            workspace_id=workspace_id,
            title=rep.title,
            memory_item_ids=json.dumps([m.id for m in cluster]),
            updated_at=datetime.datetime.now(datetime.UTC),
        )
        db.add(theme)

    db.commit()


def get_grouped_memories(
    db: Session, workspace_id: str
) -> list[tuple[MemoryTheme, list[MemoryItem]]]:
    """Return (theme, members) pairs sorted by max member weight."""
    themes = list(
        db.exec(select(MemoryTheme).where(MemoryTheme.workspace_id == workspace_id)).all()
    )

    result: list[tuple[MemoryTheme, list[MemoryItem]]] = []
    for theme in themes:
        ids: list[str] = json.loads(theme.memory_item_ids) if theme.memory_item_ids else []
        members = [db.get(MemoryItem, mid) for mid in ids if db.get(MemoryItem, mid) is not None]
        active = [m for m in members if m is not None and m.status == "active"]
        if active:
            result.append((theme, active))

    # Sort themes by the highest weight member
    result.sort(key=lambda pair: max(m.current_weight for m in pair[1]), reverse=True)
    return result
