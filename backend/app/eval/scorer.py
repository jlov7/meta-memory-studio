"""Heuristic run scoring based on outcome and feedback."""


def score_run(outcome: str, feedback: str | None = None) -> float:
    """Score a run: success=1.0, fail=0.0, with feedback adjustments."""
    base = 1.0 if outcome == "success" else 0.0

    if feedback:
        lower = feedback.lower()
        if any(w in lower for w in ("good", "great", "correct", "helpful", "perfect")):
            base = min(base + 0.1, 1.0)
        elif any(w in lower for w in ("bad", "wrong", "incorrect", "unhelpful", "poor")):
            base = max(base - 0.1, 0.0)

    return round(base, 2)
