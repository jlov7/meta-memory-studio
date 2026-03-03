"""Memory CRUD endpoints."""

from fastapi import APIRouter, Depends, Query
from sqlmodel import Session, func, select

from app.api.errors import http_error
from app.database import get_db
from app.models.memory import (
    ContributionEvent,
    MemoryItem,
    RetrievalEvent,
    WeightUpdate,
)
from app.policy.forget import hard_delete, soft_delete
from app.schemas.memory import (
    ContributionOut,
    MemoryDetail,
    MemoryList,
    MemoryOut,
    ThemeGroup,
    ThemeGroupList,
    WeightUpdateOut,
)
from app.security.rate_limit import MutatingRateLimit

router = APIRouter(prefix="/workspaces/{workspace_id}/memory", tags=["memory"])


def _memory_out(m: MemoryItem) -> MemoryOut:
    return MemoryOut(
        id=m.id,
        title=m.title,
        content=m.content,
        memory_type=m.memory_type,
        status=m.status,
        current_weight=m.current_weight,
        created_at=m.created_at,
        updated_at=m.updated_at,
    )


@router.get("", response_model=MemoryList)
def list_memories(
    workspace_id: str,
    q: str = Query(default="", description="Search query"),
    status: str = Query(default="active", description="Filter by status"),
    memory_type: str = Query(default="", description="Filter by type"),
    limit: int = Query(default=50, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> MemoryList:
    total = 0
    if q:
        from sqlalchemy import text

        rows = db.exec(  # type: ignore[call-overload]
            text(
                "SELECT memory_item_id, rank FROM memory_items_fts "
                "WHERE memory_items_fts MATCH :query "
                "ORDER BY rank"
            ),
            params={"query": q},
        ).all()
        ids = [row[0] for row in rows]
        rank_map = {row[0]: abs(row[1]) for row in rows}

        if ids:
            stmt = select(MemoryItem).where(MemoryItem.id.in_(ids))  # type: ignore[attr-defined]
            stmt = stmt.where(MemoryItem.workspace_id == workspace_id)
            if status:
                stmt = stmt.where(MemoryItem.status == status)
            if memory_type:
                stmt = stmt.where(MemoryItem.memory_type == memory_type)
            items = list(db.exec(stmt).all())
            items.sort(
                key=lambda m: (
                    -(rank_map.get(m.id, 0) * m.current_weight),
                    m.id,
                )
            )
        else:
            items = []
        total = len(items)
        items = items[offset : offset + limit]
    else:
        total_stmt = (
            select(func.count())
            .select_from(MemoryItem)
            .where(MemoryItem.workspace_id == workspace_id)
        )
        if status:
            total_stmt = total_stmt.where(MemoryItem.status == status)
        if memory_type:
            total_stmt = total_stmt.where(MemoryItem.memory_type == memory_type)
        total = db.exec(total_stmt).one()

        stmt = select(MemoryItem).where(MemoryItem.workspace_id == workspace_id)
        if status:
            stmt = stmt.where(MemoryItem.status == status)
        if memory_type:
            stmt = stmt.where(MemoryItem.memory_type == memory_type)
        stmt = stmt.order_by(MemoryItem.current_weight.desc(), MemoryItem.id.asc())  # type: ignore[attr-defined]
        stmt = stmt.offset(offset).limit(limit)
        items = list(db.exec(stmt).all())

    return MemoryList(
        memories=[_memory_out(m) for m in items],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/themes", response_model=ThemeGroupList)
def list_themes(
    workspace_id: str,
    db: Session = Depends(get_db),
) -> ThemeGroupList:
    from app.memory.themes import get_grouped_memories

    pairs = get_grouped_memories(db, workspace_id)
    groups = [
        ThemeGroup(
            theme_id=theme.id,
            theme_title=theme.title,
            memories=[_memory_out(m) for m in members],
        )
        for theme, members in pairs
    ]
    total = sum(len(g.memories) for g in groups)
    return ThemeGroupList(groups=groups, total_memories=total)


@router.get("/{memory_id}", response_model=MemoryDetail)
def get_memory(
    workspace_id: str,
    memory_id: str,
    db: Session = Depends(get_db),
) -> MemoryDetail:
    memory = db.get(MemoryItem, memory_id)
    if not memory or memory.workspace_id != workspace_id:
        raise http_error(
            status_code=404,
            code="memory_not_found",
            message="Memory not found.",
        )

    weight_history = list(
        db.exec(
            select(WeightUpdate)
            .where(WeightUpdate.memory_item_id == memory_id)
            .order_by(WeightUpdate.updated_at)  # type: ignore[arg-type]
        ).all()
    )

    contributions = list(
        db.exec(
            select(ContributionEvent)
            .where(ContributionEvent.memory_item_id == memory_id)
            .order_by(ContributionEvent.measured_at.desc())  # type: ignore[attr-defined]
        ).all()
    )

    retrieval_count = db.exec(
        select(func.count())
        .select_from(RetrievalEvent)
        .where(RetrievalEvent.memory_item_id == memory_id)
    ).one()

    return MemoryDetail(
        memory=_memory_out(memory),
        weight_history=[
            WeightUpdateOut(
                id=wu.id,
                old_weight=wu.old_weight,
                new_weight=wu.new_weight,
                delta=wu.delta,
                reason=wu.reason,
                updated_at=wu.updated_at,
            )
            for wu in weight_history
        ],
        contributions=[
            ContributionOut(
                id=c.id,
                memory_item_id=c.memory_item_id,
                baseline_run_id=c.baseline_run_id,
                guided_run_id=c.guided_run_id,
                baseline_score=c.baseline_score,
                guided_score=c.guided_score,
                delta=c.delta,
                measured_at=c.measured_at,
            )
            for c in contributions
        ],
        retrieval_count=retrieval_count,
    )


@router.patch("/{memory_id}/deprecate", response_model=MemoryOut)
def deprecate_memory(
    workspace_id: str,
    memory_id: str,
    _rate_limit: None = MutatingRateLimit,
    db: Session = Depends(get_db),
) -> MemoryOut:
    memory = soft_delete(db, memory_id)
    if not memory or memory.workspace_id != workspace_id:
        raise http_error(
            status_code=404,
            code="memory_not_found",
            message="Memory not found.",
        )
    return _memory_out(memory)


@router.delete("/{memory_id}")
def forget_memory(
    workspace_id: str,
    memory_id: str,
    _rate_limit: None = MutatingRateLimit,
    db: Session = Depends(get_db),
) -> dict[str, bool]:
    memory = db.get(MemoryItem, memory_id)
    if not memory or memory.workspace_id != workspace_id:
        raise http_error(
            status_code=404,
            code="memory_not_found",
            message="Memory not found.",
        )

    success = hard_delete(db, memory_id)
    if not success:
        raise http_error(
            status_code=500,
            code="memory_delete_failed",
            message="Failed to delete memory.",
        )
    return {"deleted": True}
