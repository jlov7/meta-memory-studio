"""Policy endpoints — evolution (contribution measurement + weight update)."""

from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.config import settings
from app.database import get_db
from app.eval.comparator import compare_runs
from app.policy.weight_updater import update_weights
from app.schemas.memory import EvolveResult
from app.security.rate_limit import MutatingRateLimit

router = APIRouter(prefix="/workspaces/{workspace_id}/policy", tags=["policy"])


@router.post("/evolve", response_model=EvolveResult)
def evolve(
    workspace_id: str,
    _rate_limit: None = MutatingRateLimit,
    db: Session = Depends(get_db),
) -> EvolveResult:
    """Run contribution measurement + weight update cycle."""
    if not settings.ENABLE_EVOLUTION:
        return EvolveResult(contributions_created=0, weight_updates=0)

    contributions = compare_runs(db, workspace_id)
    for c in contributions:
        db.add(c)
    db.flush()

    weight_updates = update_weights(db, contributions)
    db.commit()

    return EvolveResult(
        contributions_created=len(contributions),
        weight_updates=len(weight_updates),
    )
