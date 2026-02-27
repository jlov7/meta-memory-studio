"""JSONL validation — ensures each line has required fields."""

import json
from dataclasses import dataclass, field


@dataclass
class ValidationResult:
    valid: bool = True
    events: list[dict] = field(default_factory=list)  # type: ignore[type-arg]
    errors: list[str] = field(default_factory=list)


REQUIRED_FIELDS = {"type", "ts", "payload"}


def validate_jsonl(content: str) -> ValidationResult:
    """Validate JSONL content line by line. Returns parsed events and any errors."""
    result = ValidationResult()
    lines = content.strip().split("\n")

    for i, line in enumerate(lines, start=1):
        line = line.strip()
        if not line:
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError as e:
            result.errors.append(f"Line {i}: invalid JSON — {e}")
            result.valid = False
            continue

        missing = REQUIRED_FIELDS - set(event.keys())
        if missing:
            result.errors.append(f"Line {i}: missing fields {missing}")
            result.valid = False
            continue

        event["_line_number"] = i
        result.events.append(event)

    if not result.events and not result.errors:
        result.errors.append("File is empty")
        result.valid = False

    return result
