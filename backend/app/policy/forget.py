"""Soft delete (deprecate) and hard delete (forget with tombstone)."""

import datetime

from sqlalchemy import text
from sqlmodel import Session

from app.models.memory import MemoryItem


def soft_delete(session: Session, memory_id: str) -> MemoryItem | None:
    """Deprecate a memory — no longer retrieved but data preserved."""
    memory = session.get(MemoryItem, memory_id)
    if not memory:
        return None
    memory.status = "deprecated"
    memory.updated_at = datetime.datetime.now(datetime.UTC)
    session.add(memory)
    session.commit()
    session.refresh(memory)
    return memory


def hard_delete(session: Session, memory_id: str) -> bool:
    """Forget a memory — content wiped, tombstone left for audit."""
    memory = session.get(MemoryItem, memory_id)
    if not memory:
        return False

    memory.status = "deleted"
    memory.title = "[REDACTED]"
    memory.content = "[REDACTED]"
    memory.updated_at = datetime.datetime.now(datetime.UTC)
    session.add(memory)

    # Remove from FTS index
    session.exec(  # type: ignore[call-overload]
        text("DELETE FROM memory_items_fts WHERE memory_item_id = :mid"),
        params={"mid": memory_id},
    )

    session.commit()
    return True
