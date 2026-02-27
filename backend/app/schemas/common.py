"""Shared response schemas."""

from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str = "ok"
    version: str = "0.1.0"


class IntegrityResult(BaseModel):
    raw_file_id: str
    filename: str
    valid: bool
    event_count: int


class IntegrityResponse(BaseModel):
    workspace_id: str
    results: list[IntegrityResult]
    all_valid: bool


class Workspace(BaseModel):
    id: str
    name: str
    run_count: int = 0
    memory_count: int = 0


class WorkspaceList(BaseModel):
    workspaces: list[Workspace]
