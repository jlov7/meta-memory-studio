"""Drift detection endpoint."""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlmodel import Session

from app.database import get_db
from app.eval.drift import compute_drift

router = APIRouter(prefix="/workspaces/{workspace_id}/drift", tags=["drift"])


class ToolAnomalyOut(BaseModel):
    tool_name: str
    expected_freq: float
    actual_freq: float
    anomaly_score: float
    runs_affected: list[str]


class DriftReportOut(BaseModel):
    workspace_id: str
    total_runs: int
    anomalies: list[ToolAnomalyOut]


@router.get("", response_model=DriftReportOut)
def get_drift_report(
    workspace_id: str,
    db: Session = Depends(get_db),
) -> DriftReportOut:
    report = compute_drift(db, workspace_id)
    return DriftReportOut(
        workspace_id=report.workspace_id,
        total_runs=report.total_runs,
        anomalies=[
            ToolAnomalyOut(
                tool_name=a.tool_name,
                expected_freq=a.expected_freq,
                actual_freq=a.actual_freq,
                anomaly_score=a.anomaly_score,
                runs_affected=a.runs_affected,
            )
            for a in report.anomalies
        ],
    )
