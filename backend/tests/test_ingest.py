"""Tests for full ingest pipeline."""

from sqlmodel import Session, select

from app.ingest.pipeline import run_pipeline
from app.models.memory import MemoryItem
from app.models.raw import RawEvent, RawFile
from app.models.runs import Run


def test_full_pipeline(session: Session, demo_jsonl: str):
    result = run_pipeline(session, "ws_test", "demo_runs.jsonl", demo_jsonl)

    assert result["success"] is True
    assert result["raw_file_id"] is not None
    assert result["event_count"] > 0
    assert result["run_count"] == 2
    assert result["memory_count"] > 0
    assert result["hash_valid"] is True
    assert result["pii_level"] in ("none", "low", "high")
    assert len(result["errors"]) == 0


def test_pipeline_creates_raw_records(session: Session, demo_jsonl: str):
    run_pipeline(session, "ws_test", "demo_runs.jsonl", demo_jsonl)

    raw_files = session.exec(select(RawFile)).all()
    assert len(raw_files) == 1
    assert raw_files[0].filename == "demo_runs.jsonl"
    assert raw_files[0].workspace_id == "ws_test"

    raw_events = session.exec(select(RawEvent)).all()
    assert len(raw_events) > 0

    # Verify each event has a valid SHA-256 hash stored (64-char hex)
    sorted_events = sorted(raw_events, key=lambda e: e.line_number)
    hashes = [re.hash_chain for re in sorted_events]
    assert all(len(h) == 64 for h in hashes)
    # Chain effect: every hash must be unique (each includes prev hash)
    assert len(set(hashes)) == len(hashes)


def test_pipeline_creates_runs(session: Session, demo_jsonl: str):
    run_pipeline(session, "ws_test", "demo_runs.jsonl", demo_jsonl)

    runs = session.exec(select(Run)).all()
    assert len(runs) == 2

    external_ids = {r.external_id for r in runs}
    assert "run_demo_001" in external_ids
    assert "run_demo_002" in external_ids


def test_pipeline_creates_memories(session: Session, demo_jsonl: str):
    run_pipeline(session, "ws_test", "demo_runs.jsonl", demo_jsonl)

    memories = session.exec(select(MemoryItem)).all()
    assert len(memories) > 0

    titles = [m.title for m in memories]
    assert "Apply airline preference before booking" in titles


def test_pipeline_idempotent_filename(session: Session, demo_jsonl: str):
    """Importing the same file twice deduplicates memories via deterministic IDs."""
    run_pipeline(session, "ws_test", "demo_runs.jsonl", demo_jsonl)
    run_pipeline(session, "ws_test", "demo_runs.jsonl", demo_jsonl)

    raw_files = session.exec(select(RawFile)).all()
    # Second import creates a new raw file record (different hash chain ID)
    assert len(raw_files) == 2

    # But memories deduplicate via deterministic IDs
    memories = session.exec(select(MemoryItem)).all()
    titles = [m.title for m in memories]
    assert titles.count("Apply airline preference before booking") == 1
