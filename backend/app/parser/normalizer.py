"""Canonical event schema and timestamp normalization."""

from datetime import datetime


def parse_timestamp(ts: str) -> datetime:
    """Parse ISO 8601 timestamp, handling Z suffix."""
    ts = ts.replace("Z", "+00:00")
    return datetime.fromisoformat(ts)


def normalize_event(raw: dict) -> dict:  # type: ignore[type-arg]
    """Normalize a raw event into canonical schema."""
    return {
        "type": raw["type"],
        "ts": parse_timestamp(raw["ts"]),
        "run_id": raw.get("payload", {}).get("run_id", raw.get("run_id", "")),
        "payload": raw.get("payload", {}),
        "raw": raw,
    }
