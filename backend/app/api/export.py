"""Memory Review Pack export -- streams a zip with summary + redacted memories."""

import datetime
import io
import json
import zipfile

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlmodel import Session, func, select

from app.database import get_db
from app.ingest.pii import EMAIL_RE, PHONE_RE, SSN_RE
from app.models.memory import MemoryItem, WeightUpdate
from app.models.runs import Run

router = APIRouter(prefix="/workspaces/{workspace_id}/export", tags=["export"])

_PII_PLACEHOLDER = "[REDACTED]"


def _redact(text: str) -> str:
    """Strip known PII patterns from a string."""
    text = SSN_RE.sub(_PII_PLACEHOLDER, text)
    text = EMAIL_RE.sub(_PII_PLACEHOLDER, text)
    text = PHONE_RE.sub(_PII_PLACEHOLDER, text)
    return text


def _build_summary(
    workspace_id: str,
    db: Session,
    memories: list[MemoryItem],
) -> str:
    """Render a Markdown summary of the workspace."""
    run_count = db.exec(
        select(func.count()).select_from(Run).where(Run.workspace_id == workspace_id)
    ).one()

    active = [m for m in memories if m.status == "active"]
    deprecated = [m for m in memories if m.status == "deprecated"]

    top_helpful = sorted(active, key=lambda m: m.current_weight, reverse=True)[:5]
    top_harmful = sorted(active, key=lambda m: m.current_weight)[:5]

    lines: list[str] = [
        "# Memory Review Pack",
        "",
        f"**Workspace:** `{workspace_id}`  ",
        f"**Generated:** {datetime.datetime.now(datetime.UTC).strftime('%Y-%m-%d %H:%M UTC')}",
        "",
        "## Stats",
        "",
        "| Metric | Value |",
        "|---|---|",
        f"| Total runs | {run_count} |",
        f"| Active memories | {len(active)} |",
        f"| Deprecated memories | {len(deprecated)} |",
        "",
        "## Top 5 High-Weight Memories",
        "",
    ]
    for m in top_helpful:
        lines.append(f"- **{_redact(m.title)}** (weight: {m.current_weight:.3f})")
    lines += ["", "## Top 5 Low-Weight Memories", ""]
    for m in top_harmful:
        lines.append(f"- **{_redact(m.title)}** (weight: {m.current_weight:.3f})")
    lines += [""]
    return "\n".join(lines)


@router.post("/review-pack")
def export_review_pack(
    workspace_id: str,
    db: Session = Depends(get_db),
) -> StreamingResponse:
    memories = list(
        db.exec(select(MemoryItem).where(MemoryItem.workspace_id == workspace_id)).all()
    )

    summary_md = _build_summary(workspace_id, db, memories)

    exportable = [m for m in memories if m.status != "deleted"]
    memories_data = [
        {
            "id": m.id,
            "title": _redact(m.title),
            "content": _redact(m.content),
            "memory_type": m.memory_type,
            "status": m.status,
            "current_weight": m.current_weight,
            "created_at": m.created_at.isoformat() if m.created_at else None,
            "updated_at": m.updated_at.isoformat() if m.updated_at else None,
        }
        for m in exportable
    ]

    history: dict[str, list[dict[str, object]]] = {}
    for m in exportable:
        updates = list(
            db.exec(
                select(WeightUpdate)
                .where(WeightUpdate.memory_item_id == m.id)
                .order_by(WeightUpdate.updated_at)  # type: ignore[arg-type]
            ).all()
        )
        if updates:
            history[m.id] = [
                {
                    "old_weight": u.old_weight,
                    "new_weight": u.new_weight,
                    "delta": u.delta,
                    "reason": u.reason,
                    "updated_at": u.updated_at.isoformat() if u.updated_at else None,
                }
                for u in updates
            ]

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("summary.md", summary_md)
        zf.writestr("memories.json", json.dumps(memories_data, indent=2))
        zf.writestr("weight_history.json", json.dumps(history, indent=2))
    buf.seek(0)

    date_stamp = datetime.datetime.now(datetime.UTC).strftime("%Y%m%d")
    filename = f"review-pack-{workspace_id[:8]}-{date_stamp}.zip"
    return StreamingResponse(
        buf,
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
