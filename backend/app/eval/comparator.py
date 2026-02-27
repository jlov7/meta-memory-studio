"""Baseline vs memory-guided comparison for contribution measurement."""

from sqlmodel import Session, select

from app.models.memory import ContributionEvent, MemoryItem, RetrievalEvent
from app.models.runs import Run


def compare_runs(
    session: Session,
    workspace_id: str,
) -> list[ContributionEvent]:
    """Compare runs in a workspace to measure memory contribution.

    Strategy: find runs where memories were retrieved (guided) vs runs without
    retrieval (baseline). Create contribution events for each memory used.
    """
    runs = list(
        session.exec(
            select(Run).where(Run.workspace_id == workspace_id).order_by(Run.started_at)  # type: ignore[arg-type]
        ).all()
    )
    if len(runs) < 2:
        return []

    baseline_runs: list[Run] = []
    guided_runs: list[Run] = []

    for run in runs:
        has_retrieval = session.exec(
            select(RetrievalEvent).where(RetrievalEvent.run_id == run.id)
        ).first()
        if has_retrieval:
            guided_runs.append(run)
        else:
            baseline_runs.append(run)

    if not baseline_runs or not guided_runs:
        return []

    contributions: list[ContributionEvent] = []

    for guided in guided_runs:
        retrievals = list(
            session.exec(select(RetrievalEvent).where(RetrievalEvent.run_id == guided.id)).all()
        )

        baseline = baseline_runs[0]
        baseline_score = baseline.score if baseline.score is not None else 0.0
        guided_score = guided.score if guided.score is not None else 0.0

        for retrieval in retrievals:
            memory = session.get(MemoryItem, retrieval.memory_item_id)
            if not memory:
                continue

            delta = guided_score - baseline_score
            contrib = ContributionEvent(
                memory_item_id=retrieval.memory_item_id,
                workspace_id=workspace_id,
                baseline_run_id=baseline.id,
                guided_run_id=guided.id,
                baseline_score=baseline_score,
                guided_score=guided_score,
                delta=round(delta, 4),
            )
            contributions.append(contrib)

    return contributions
