"""Run / Episode / Step / ToolCall models."""

from datetime import datetime

from sqlmodel import Field, SQLModel
from uuid_utils import uuid7


class Run(SQLModel, table=True):
    __tablename__ = "runs"

    id: str = Field(default_factory=lambda: str(uuid7()), primary_key=True)
    workspace_id: str = Field(index=True)
    external_id: str = Field(index=True)  # e.g. "run_demo_001"
    started_at: datetime | None = None
    ended_at: datetime | None = None
    outcome: str = Field(default="unknown")  # success | fail | unknown
    score: float | None = None
    episode_count: int = 0
    step_count: int = 0


class Episode(SQLModel, table=True):
    __tablename__ = "episodes"

    id: str = Field(default_factory=lambda: str(uuid7()), primary_key=True)
    run_id: str = Field(foreign_key="runs.id", index=True)
    sequence: int = 0
    title: str = ""
    started_at: datetime | None = None
    ended_at: datetime | None = None


class Step(SQLModel, table=True):
    __tablename__ = "steps"

    id: str = Field(default_factory=lambda: str(uuid7()), primary_key=True)
    episode_id: str = Field(foreign_key="episodes.id", index=True)
    run_id: str = Field(foreign_key="runs.id", index=True)
    sequence: int = 0
    event_type: str = ""
    timestamp: datetime | None = None
    actor: str = ""  # "user" | "agent" | "system"
    content: str = ""  # JSON string of the full event payload
    raw_event_id: str | None = Field(default=None, foreign_key="raw_events.id")


class ToolCall(SQLModel, table=True):
    __tablename__ = "tool_calls"

    id: str = Field(default_factory=lambda: str(uuid7()), primary_key=True)
    step_id: str = Field(foreign_key="steps.id", index=True)
    run_id: str = Field(foreign_key="runs.id", index=True)
    tool_name: str = Field(index=True)
    arguments: str = ""  # JSON string
    result: str = ""  # JSON string
    duration_ms: int | None = None
