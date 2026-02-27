"""Tests for memory constructor."""

from app.ingest.validator import validate_jsonl
from app.memory.constructor import construct_memories, deterministic_id


def test_deterministic_id():
    id1 = deterministic_id("ws1", "Apply airline preference before booking")
    id2 = deterministic_id("ws1", "Apply airline preference before booking")
    assert id1 == id2

    id3 = deterministic_id("ws1", "Different title")
    assert id1 != id3

    id4 = deterministic_id("ws2", "Apply airline preference before booking")
    assert id1 != id4


def test_construct_from_demo(demo_jsonl: str):
    result = validate_jsonl(demo_jsonl)
    assert result.valid

    raw_ids = [f"raw_{i}" for i in range(len(result.events))]
    run_ids = {"run_demo_001": "uuid-run-001", "run_demo_002": "uuid-run-002"}

    items, sources = construct_memories("ws1", result.events, raw_ids, run_ids)

    # Demo should produce at least one memory from memory_write_candidate
    assert len(items) > 0
    assert len(sources) == len(items)

    # Check the specific memory from demo
    titles = [m.title for m in items]
    assert "Apply airline preference before booking" in titles

    # Sources should reference runs
    for source in sources:
        assert source.source_type == "write_candidate"
