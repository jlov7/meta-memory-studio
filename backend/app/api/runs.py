"""Run listing, detail, and timeline endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.database import get_db
from app.models.runs import Run, Step
from app.schemas.runs import RunDetail, RunList, RunSummary, TimelineStep

router = APIRouter(prefix="/workspaces/{workspace_id}/runs", tags=["runs"])


@router.get("", response_model=RunList)
def list_runs(workspace_id: str, db: Session = Depends(get_db)) -> RunList:
    runs = list(
        db.exec(
            select(Run).where(Run.workspace_id == workspace_id).order_by(Run.started_at.desc())  # type: ignore[union-attr]
        ).all()
    )
    summaries = [
        RunSummary(
            id=r.id,
            external_id=r.external_id,
            outcome=r.outcome,
            score=r.score,
            started_at=r.started_at,
            ended_at=r.ended_at,
            episode_count=r.episode_count,
            step_count=r.step_count,
        )
        for r in runs
    ]
    return RunList(runs=summaries, total=len(summaries))


@router.get("/{run_id}", response_model=RunDetail)
def get_run(workspace_id: str, run_id: str, db: Session = Depends(get_db)) -> RunDetail:
    run = db.get(Run, run_id)
    if not run or run.workspace_id != workspace_id:
        raise HTTPException(status_code=404, detail="Run not found")

    steps = list(
        db.exec(
            select(Step).where(Step.run_id == run_id).order_by(Step.sequence)  # type: ignore[arg-type]
        ).all()
    )

    timeline = [
        TimelineStep(
            id=s.id,
            sequence=s.sequence,
            event_type=s.event_type,
            timestamp=s.timestamp,
            actor=s.actor,
            content=s.content,
            raw_event_id=s.raw_event_id,
        )
        for s in steps
    ]

    return RunDetail(
        id=run.id,
        external_id=run.external_id,
        outcome=run.outcome,
        score=run.score,
        started_at=run.started_at,
        ended_at=run.ended_at,
        episode_count=run.episode_count,
        step_count=run.step_count,
        timeline=timeline,
    )
