"""Run and timeline response schemas."""

from datetime import datetime

from pydantic import BaseModel


class RunSummary(BaseModel):
    id: str
    external_id: str
    outcome: str
    score: float | None
    started_at: datetime | None
    ended_at: datetime | None
    episode_count: int
    step_count: int


class RunList(BaseModel):
    runs: list[RunSummary]
    total: int
    limit: int
    offset: int


class TimelineStep(BaseModel):
    id: str
    sequence: int
    event_type: str
    timestamp: datetime | None
    actor: str
    content: str  # JSON string
    raw_event_id: str | None = None


class RunDetail(BaseModel):
    id: str
    external_id: str
    outcome: str
    score: float | None
    started_at: datetime | None
    ended_at: datetime | None
    episode_count: int
    step_count: int
    timeline: list[TimelineStep]
    hash_valid: bool = True
