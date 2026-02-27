"""Drift detection: analyse tool_call patterns across workspace runs."""

import math
from collections import defaultdict
from dataclasses import dataclass, field

from sqlmodel import Session, select

from app.models.runs import Run, ToolCall


@dataclass
class ToolAnomaly:
    tool_name: str
    expected_freq: float  # mean calls-per-run across workspace
    actual_freq: float  # count in the most anomalous run
    anomaly_score: float  # (actual - mean) / std_dev
    runs_affected: list[str] = field(default_factory=list)


@dataclass
class DriftReport:
    workspace_id: str
    total_runs: int
    anomalies: list[ToolAnomaly] = field(default_factory=list)


def compute_drift(db: Session, workspace_id: str) -> DriftReport:
    """Return anomalous tool-usage patterns for the workspace.

    Algorithm: for each tool, compute the mean + std-dev of calls-per-run.
    Any run whose count exceeds mean + 2 * std_dev is flagged as an anomaly.
    Requires at least 2 runs (otherwise no meaningful baseline).
    """
    runs = list(db.exec(select(Run).where(Run.workspace_id == workspace_id)).all())
    if len(runs) < 2:
        return DriftReport(workspace_id=workspace_id, total_runs=len(runs))

    run_ids = [r.id for r in runs]

    tool_calls = list(
        db.exec(
            select(ToolCall).where(ToolCall.run_id.in_(run_ids))  # type: ignore[attr-defined]
        ).all()
    )

    # counts[tool_name][run_id] = call count
    counts: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for tc in tool_calls:
        counts[tc.tool_name][tc.run_id] += 1

    anomalies: list[ToolAnomaly] = []

    for tool_name, run_counts in counts.items():
        all_counts = [run_counts.get(r_id, 0) for r_id in run_ids]
        n = len(all_counts)
        mean = sum(all_counts) / n
        variance = sum((c - mean) ** 2 for c in all_counts) / n
        std_dev = math.sqrt(variance)

        if std_dev == 0:
            continue  # uniform usage -- no anomaly

        threshold = mean + 2.0 * std_dev
        affected: list[str] = []
        max_actual = 0.0
        max_score = 0.0

        for r_id in run_ids:
            count = run_counts.get(r_id, 0)
            if count > threshold:
                affected.append(r_id)
                score = (count - mean) / std_dev
                if score > max_score:
                    max_score = score
                    max_actual = float(count)

        if affected:
            anomalies.append(
                ToolAnomaly(
                    tool_name=tool_name,
                    expected_freq=round(mean, 3),
                    actual_freq=max_actual,
                    anomaly_score=round(max_score, 3),
                    runs_affected=affected,
                )
            )

    anomalies.sort(key=lambda a: a.anomaly_score, reverse=True)
    return DriftReport(
        workspace_id=workspace_id,
        total_runs=len(runs),
        anomalies=anomalies,
    )
