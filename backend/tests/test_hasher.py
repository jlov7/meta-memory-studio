"""Tests for SHA-256 hash chain."""

from app.ingest.hasher import build_chain, hash_event, seed_hash, verify_chain


def test_seed_hash_deterministic():
    h1 = seed_hash("test.jsonl")
    h2 = seed_hash("test.jsonl")
    assert h1 == h2
    assert len(h1) == 64  # SHA-256 hex length


def test_hash_event_deterministic():
    event = {"type": "test", "ts": "2025-01-01T00:00:00Z", "payload": {"key": "value"}}
    h1 = hash_event("abc", event)
    h2 = hash_event("abc", event)
    assert h1 == h2


def test_hash_event_different_prev():
    event = {"type": "test", "ts": "2025-01-01T00:00:00Z", "payload": {}}
    h1 = hash_event("aaa", event)
    h2 = hash_event("bbb", event)
    assert h1 != h2


def test_build_and_verify_chain():
    events = [
        {"type": "a", "ts": "2025-01-01T00:00:00Z", "payload": {}},
        {"type": "b", "ts": "2025-01-01T00:01:00Z", "payload": {"x": 1}},
        {"type": "c", "ts": "2025-01-01T00:02:00Z", "payload": {"y": "z"}},
    ]
    hashes = build_chain("test.jsonl", events)
    assert len(hashes) == 3
    assert verify_chain("test.jsonl", events, hashes)


def test_verify_fails_on_tamper():
    events = [
        {"type": "a", "ts": "2025-01-01T00:00:00Z", "payload": {}},
        {"type": "b", "ts": "2025-01-01T00:01:00Z", "payload": {"x": 1}},
    ]
    hashes = build_chain("test.jsonl", events)

    # Tamper with an event
    events[1]["payload"]["x"] = 999  # type: ignore[index]
    assert not verify_chain("test.jsonl", events, hashes)


def test_verify_fails_on_wrong_filename():
    events = [{"type": "a", "ts": "2025-01-01T00:00:00Z", "payload": {}}]
    hashes = build_chain("original.jsonl", events)
    assert not verify_chain("different.jsonl", events, hashes)
