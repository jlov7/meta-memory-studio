"""FTS5-powered memory retrieval with weight multiplier."""

from sqlalchemy import text
from sqlmodel import Session, select

from app.models.memory import MemoryItem


def search_memories(
    session: Session,
    workspace_id: str,
    query: str,
    limit: int = 10,
) -> list[MemoryItem]:
    """Search active memories via FTS5, ranked by relevance * weight."""
    if not query.strip():
        stmt = (
            select(MemoryItem)
            .where(MemoryItem.workspace_id == workspace_id)
            .where(MemoryItem.status == "active")
            .order_by(MemoryItem.current_weight.desc())  # type: ignore[attr-defined]
            .limit(limit)
        )
        return list(session.exec(stmt).all())

    fts_query = text(
        "SELECT memory_item_id, rank FROM memory_items_fts "
        "WHERE memory_items_fts MATCH :query "
        "ORDER BY rank "
        "LIMIT :limit"
    )
    rows = session.exec(fts_query, params={"query": query, "limit": limit * 2}).all()  # type: ignore[call-overload]

    if not rows:
        return []

    ids = [row[0] for row in rows]
    stmt = (
        select(MemoryItem)
        .where(MemoryItem.id.in_(ids))  # type: ignore[attr-defined]
        .where(MemoryItem.workspace_id == workspace_id)
        .where(MemoryItem.status == "active")
    )
    items = list(session.exec(stmt).all())

    rank_map = {row[0]: abs(row[1]) for row in rows}
    items.sort(key=lambda m: rank_map.get(m.id, 0) * m.current_weight, reverse=True)
    return items[:limit]
