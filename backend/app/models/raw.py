"""Raw trace storage models — immutable, hash-chained."""

import datetime

from sqlmodel import Field, SQLModel
from uuid_utils import uuid7


class RawFile(SQLModel, table=True):
    __tablename__ = "raw_files"

    id: str = Field(default_factory=lambda: str(uuid7()), primary_key=True)
    workspace_id: str = Field(index=True)
    filename: str
    sha256_hash: str
    event_count: int = 0
    pii_level: str = Field(default="none")  # none | low | high
    imported_at: datetime.datetime = Field(
        default_factory=lambda: datetime.datetime.now(datetime.UTC)
    )


class RawEvent(SQLModel, table=True):
    __tablename__ = "raw_events"

    id: str = Field(default_factory=lambda: str(uuid7()), primary_key=True)
    raw_file_id: str = Field(foreign_key="raw_files.id", index=True)
    workspace_id: str = Field(index=True)
    line_number: int
    event_type: str = Field(index=True)
    timestamp: datetime.datetime
    payload: str  # JSON string
    hash_chain: str  # SHA-256 of (prev_hash + canonical(event))
