"""SHA-256 hash chain for tamper-evident trace storage."""

import hashlib
import json


def canonical(event: dict) -> str:  # type: ignore[type-arg]
    """Deterministic JSON serialization for hashing."""
    return json.dumps(event, sort_keys=True, separators=(",", ":"))


def hash_event(prev_hash: str, event: dict) -> str:  # type: ignore[type-arg]
    """Compute next hash in chain: SHA-256(prev_hex + canonical(event))."""
    data = prev_hash + canonical(event)
    return hashlib.sha256(data.encode()).hexdigest()


def seed_hash(filename: str) -> str:
    """Seed hash from filename for chain initialization."""
    return hashlib.sha256(filename.encode()).hexdigest()


def build_chain(filename: str, events: list[dict]) -> list[str]:  # type: ignore[type-arg]
    """Build full hash chain for a list of events. Returns list of hashes."""
    hashes: list[str] = []
    prev = seed_hash(filename)
    for event in events:
        h = hash_event(prev, event)
        hashes.append(h)
        prev = h
    return hashes


def verify_chain(filename: str, events: list[dict], hashes: list[str]) -> bool:  # type: ignore[type-arg]
    """Verify a hash chain against events. Returns True if valid."""
    if len(events) != len(hashes):
        return False
    expected = build_chain(filename, events)
    return expected == hashes
