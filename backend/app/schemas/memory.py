"""Memory response schemas."""

from datetime import datetime

from pydantic import BaseModel


class MemoryOut(BaseModel):
    id: str
    title: str
    content: str
    memory_type: str
    status: str
    current_weight: float
    created_at: datetime
    updated_at: datetime


class MemoryList(BaseModel):
    memories: list[MemoryOut]
    total: int
    limit: int
    offset: int


class WeightUpdateOut(BaseModel):
    id: str
    old_weight: float
    new_weight: float
    delta: float
    reason: str
    updated_at: datetime


class ContributionOut(BaseModel):
    id: str
    memory_item_id: str
    baseline_run_id: str
    guided_run_id: str
    baseline_score: float
    guided_score: float
    delta: float
    measured_at: datetime


class MemoryDetail(BaseModel):
    memory: MemoryOut
    weight_history: list[WeightUpdateOut]
    contributions: list[ContributionOut]
    retrieval_count: int


class EvolveResult(BaseModel):
    contributions_created: int
    weight_updates: int


class ThemeGroup(BaseModel):
    theme_id: str
    theme_title: str
    memories: list[MemoryOut]


class ThemeGroupList(BaseModel):
    groups: list[ThemeGroup]
    total_memories: int
