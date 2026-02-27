"""Tests for episode builder."""

from app.ingest.validator import validate_jsonl
from app.parser.episode_builder import build_episodes
from app.parser.normalizer import normalize_event


def test_build_two_runs(demo_jsonl: str):
    result = validate_jsonl(demo_jsonl)
    assert result.valid

    normalized = [normalize_event(e) for e in result.events]
    raw_ids = [f"raw_{i}" for i in range(len(normalized))]

    runs, episodes, steps, tool_calls = build_episodes("ws1", normalized, raw_ids)

    # Demo has 2 runs
    assert len(runs) == 2

    external_ids = {r.external_id for r in runs}
    assert "run_demo_001" in external_ids
    assert "run_demo_002" in external_ids

    # Each run gets one episode
    assert len(episodes) == 2

    # Steps should exist for both runs
    assert len(steps) > 0

    # At least some tool calls in the demo
    assert len(tool_calls) > 0


def test_run_outcomes(demo_jsonl: str):
    result = validate_jsonl(demo_jsonl)
    normalized = [normalize_event(e) for e in result.events]
    raw_ids = [f"raw_{i}" for i in range(len(normalized))]

    runs, _, _, _ = build_episodes("ws1", normalized, raw_ids)

    outcomes = {r.external_id: r.outcome for r in runs}
    assert outcomes["run_demo_001"] == "fail"
    assert outcomes["run_demo_002"] == "success"
