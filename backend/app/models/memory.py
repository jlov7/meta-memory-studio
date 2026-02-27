"""Memory items, sources, retrieval, contribution, and weight updates."""

import datetime

from sqlmodel import Field, SQLModel
from uuid_utils import uuid7


class MemoryItem(SQLModel, table=True):
    __tablename__ = "memory_items"

    id: str = Field(default_factory=lambda: str(uuid7()), primary_key=True)
    workspace_id: str = Field(index=True)
    title: str
    content: str
    memory_type: str = Field(default="episodic", index=True)  # episodic | semantic | procedural
    status: str = Field(default="active", index=True)  # active | deprecated | deleted
    current_weight: float = Field(default=1.0)
    created_at: datetime.datetime = Field(
        default_factory=lambda: datetime.datetime.now(datetime.UTC)
    )
    updated_at: datetime.datetime = Field(
        default_factory=lambda: datetime.datetime.now(datetime.UTC)
    )


class MemorySource(SQLModel, table=True):
    __tablename__ = "memory_sources"

    id: str = Field(default_factory=lambda: str(uuid7()), primary_key=True)
    memory_item_id: str = Field(foreign_key="memory_items.id", index=True)
    run_id: str = Field(foreign_key="runs.id")
    raw_event_id: str | None = Field(default=None, foreign_key="raw_events.id")
    source_type: str = ""  # "write_candidate" | "manual"


class RetrievalEvent(SQLModel, table=True):
    __tablename__ = "retrieval_events"

    id: str = Field(default_factory=lambda: str(uuid7()), primary_key=True)
    memory_item_id: str = Field(foreign_key="memory_items.id", index=True)
    run_id: str = Field(foreign_key="runs.id", index=True)
    query: str = ""
    rank: int = 0
    score: float = 0.0
    retrieved_at: datetime.datetime = Field(
        default_factory=lambda: datetime.datetime.now(datetime.UTC)
    )


class ContributionEvent(SQLModel, table=True):
    __tablename__ = "contribution_events"

    id: str = Field(default_factory=lambda: str(uuid7()), primary_key=True)
    memory_item_id: str = Field(foreign_key="memory_items.id", index=True)
    workspace_id: str = Field(index=True)
    baseline_run_id: str = Field(foreign_key="runs.id")
    guided_run_id: str = Field(foreign_key="runs.id")
    baseline_score: float = 0.0
    guided_score: float = 0.0
    delta: float = 0.0
    measured_at: datetime.datetime = Field(
        default_factory=lambda: datetime.datetime.now(datetime.UTC)
    )


class WeightUpdate(SQLModel, table=True):
    __tablename__ = "weight_updates"

    id: str = Field(default_factory=lambda: str(uuid7()), primary_key=True)
    memory_item_id: str = Field(foreign_key="memory_items.id", index=True)
    old_weight: float
    new_weight: float
    delta: float
    reason: str = ""  # "evolution" | "manual" | "decay"
    updated_at: datetime.datetime = Field(
        default_factory=lambda: datetime.datetime.now(datetime.UTC)
    )


class MemoryTheme(SQLModel, table=True):
    __tablename__ = "memory_themes"

    id: str = Field(default_factory=lambda: str(uuid7()), primary_key=True)
    workspace_id: str = Field(index=True)
    title: str  # representative title for the theme cluster
    memory_item_ids: str = ""  # JSON array of MemoryItem IDs
    updated_at: datetime.datetime = Field(
        default_factory=lambda: datetime.datetime.now(datetime.UTC)
    )
