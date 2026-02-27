"""Regex-based PII detection."""

import re

EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
PHONE_RE = re.compile(r"\b(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b")
SSN_RE = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")


def detect_pii(text: str) -> str:
    """Return PII level: 'high', 'low', or 'none'."""
    if SSN_RE.search(text):
        return "high"
    if EMAIL_RE.search(text) or PHONE_RE.search(text):
        return "low"
    return "none"


def scan_events(events: list[dict]) -> str:  # type: ignore[type-arg]
    """Scan all events and return the highest PII level found."""
    highest = "none"
    for event in events:
        text = str(event)
        level = detect_pii(text)
        if level == "high":
            return "high"
        if level == "low":
            highest = "low"
    return highest
