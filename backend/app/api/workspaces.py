"""Workspace management endpoints."""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlmodel import Session, func, select

from app.database import get_db
from app.models.memory import MemoryItem
from app.models.runs import Run
from app.schemas.common import Workspace, WorkspaceList

router = APIRouter(prefix="/workspaces", tags=["workspaces"])

# Simple in-memory workspace registry (SQLite doesn't need a separate table for MVP)
_workspaces: dict[str, str] = {}


class WorkspaceCreate(BaseModel):
    name: str = "default"


def ensure_workspace(workspace_id: str, name: str | None = None) -> None:
    if workspace_id not in _workspaces:
        _workspaces[workspace_id] = name or workspace_id


def clear_workspaces() -> None:
    """Clear workspace registry — for testing only."""
    _workspaces.clear()


@router.get("", response_model=WorkspaceList)
def list_workspaces(db: Session = Depends(get_db)) -> WorkspaceList:
    workspaces: list[Workspace] = []
    for ws_id, ws_name in _workspaces.items():
        run_count = db.exec(
            select(func.count()).select_from(Run).where(Run.workspace_id == ws_id)
        ).one()
        memory_count = db.exec(
            select(func.count())
            .select_from(MemoryItem)
            .where(MemoryItem.workspace_id == ws_id)
            .where(MemoryItem.status != "deleted")
        ).one()
        workspaces.append(
            Workspace(
                id=ws_id,
                name=ws_name,
                run_count=run_count,
                memory_count=memory_count,
            )
        )
    return WorkspaceList(workspaces=workspaces)


@router.post("", response_model=Workspace)
def create_workspace(body: WorkspaceCreate, db: Session = Depends(get_db)) -> Workspace:
    from uuid_utils import uuid7

    ws_id = str(uuid7())
    ensure_workspace(ws_id, body.name)
    return Workspace(id=ws_id, name=body.name)
