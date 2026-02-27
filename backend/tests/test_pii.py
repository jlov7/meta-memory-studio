"""Tests for PII detection."""

from app.ingest.pii import detect_pii, scan_events


def test_detect_email():
    assert detect_pii("Contact us at test@example.com") == "low"


def test_detect_phone():
    assert detect_pii("Call me at 555-123-4567") == "low"


def test_detect_ssn():
    assert detect_pii("SSN: 123-45-6789") == "high"


def test_detect_none():
    assert detect_pii("No personal info here") == "none"


def test_detect_combined():
    assert detect_pii("Email: a@b.com and SSN: 111-22-3333") == "high"


def test_scan_events_none():
    events = [{"type": "test", "payload": {"msg": "hello"}}]
    assert scan_events(events) == "none"


def test_scan_events_low():
    events = [
        {"type": "test", "payload": {"msg": "hello"}},
        {"type": "test", "payload": {"email": "user@example.com"}},
    ]
    assert scan_events(events) == "low"


def test_scan_events_high():
    events = [
        {"type": "test", "payload": {"ssn": "123-45-6789"}},
    ]
    assert scan_events(events) == "high"
