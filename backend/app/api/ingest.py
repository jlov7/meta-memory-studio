"""Trace import endpoints."""

from fastapi import APIRouter, Depends, UploadFile
from sqlmodel import Session

from app.api.errors import http_error
from app.api.workspaces import ensure_workspace
from app.config import settings
from app.database import get_db
from app.ingest.pipeline import run_pipeline
from app.schemas.ingest import ImportResult
from app.security.rate_limit import MutatingRateLimit

router = APIRouter(tags=["ingest"])


@router.post("/workspaces/{workspace_id}/import", response_model=ImportResult)
async def import_trace(
    workspace_id: str,
    file: UploadFile,
    _rate_limit: None = MutatingRateLimit,
    db: Session = Depends(get_db),
) -> ImportResult:
    """Import a JSONL trace file into a workspace."""
    ensure_workspace(workspace_id)
    content_bytes = await file.read()
    if len(content_bytes) > settings.MAX_IMPORT_BYTES:
        raise http_error(
            status_code=413,
            code="payload_too_large",
            message=f"Import file exceeds {settings.MAX_IMPORT_BYTES} bytes limit.",
        )

    try:
        content = content_bytes.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise http_error(
            status_code=400,
            code="invalid_encoding",
            message="Import file must be UTF-8 encoded JSONL.",
        ) from exc
    filename = file.filename or "unknown.jsonl"

    result = run_pipeline(db, workspace_id, filename, content)

    if not result["success"]:
        return ImportResult(success=False, errors=result.get("errors", []))

    return ImportResult(
        success=True,
        raw_file_id=result["raw_file_id"],
        duplicate=result.get("duplicate", False),
        duplicate_of_raw_file_id=result.get("duplicate_of_raw_file_id"),
        event_count=result["event_count"],
        run_count=result["run_count"],
        memory_count=result["memory_count"],
        pii_level=result["pii_level"],
    )


@router.post("/workspaces/{workspace_id}/import/demo", response_model=ImportResult)
def import_demo(
    workspace_id: str,
    _rate_limit: None = MutatingRateLimit,
    db: Session = Depends(get_db),
) -> ImportResult:
    """Import the bundled demo trace."""
    from pathlib import Path

    ensure_workspace(workspace_id, "Demo Workspace")
    demo_path = (
        Path(__file__).parent.parent.parent.parent
        / "examples"
        / "sample_traces"
        / "demo_runs.jsonl"
    )

    if not demo_path.exists():
        return ImportResult(success=False, errors=[f"Demo file not found: {demo_path}"])

    content = demo_path.read_text()
    result = run_pipeline(db, workspace_id, "demo_runs.jsonl", content)

    if not result["success"]:
        return ImportResult(success=False, errors=result.get("errors", []))

    return ImportResult(
        success=True,
        raw_file_id=result["raw_file_id"],
        duplicate=result.get("duplicate", False),
        duplicate_of_raw_file_id=result.get("duplicate_of_raw_file_id"),
        event_count=result["event_count"],
        run_count=result["run_count"],
        memory_count=result["memory_count"],
        pii_level=result["pii_level"],
    )
