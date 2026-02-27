"""Ingest response schemas."""

from pydantic import BaseModel


class ImportResult(BaseModel):
    success: bool
    raw_file_id: str | None = None
    event_count: int = 0
    run_count: int = 0
    memory_count: int = 0
    pii_level: str = "none"
    hash_valid: bool = True
    errors: list[str] = []
