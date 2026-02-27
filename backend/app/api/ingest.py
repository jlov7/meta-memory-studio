"""Trace import endpoints."""

from fastapi import APIRouter, Depends, UploadFile
from sqlmodel import Session

from app.api.workspaces import ensure_workspace
from app.database import get_db
from app.ingest.pipeline import run_pipeline
from app.schemas.ingest import ImportResult

router = APIRouter(tags=["ingest"])


@router.post("/workspaces/{workspace_id}/import", response_model=ImportResult)
async def import_trace(
    workspace_id: str,
    file: UploadFile,
    db: Session = Depends(get_db),
) -> ImportResult:
    """Import a JSONL trace file into a workspace."""
    ensure_workspace(workspace_id)
    content = (await file.read()).decode("utf-8")
    filename = file.filename or "unknown.jsonl"

    result = run_pipeline(db, workspace_id, filename, content)

    if not result["success"]:
        return ImportResult(success=False, errors=result.get("errors", []))

    return ImportResult(
        success=True,
        raw_file_id=result["raw_file_id"],
        event_count=result["event_count"],
        run_count=result["run_count"],
        memory_count=result["memory_count"],
        pii_level=result["pii_level"],
    )


@router.post("/workspaces/{workspace_id}/import/demo", response_model=ImportResult)
def import_demo(
    workspace_id: str,
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
        event_count=result["event_count"],
        run_count=result["run_count"],
        memory_count=result["memory_count"],
        pii_level=result["pii_level"],
    )
