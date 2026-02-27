"""Health check and integrity verification endpoints."""

import json

from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from app.database import get_db
from app.ingest.hasher import verify_chain
from app.models.raw import RawEvent, RawFile
from app.schemas.common import HealthResponse, IntegrityResponse, IntegrityResult

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    return HealthResponse()


@router.get("/workspaces/{workspace_id}/integrity", response_model=IntegrityResponse)
def check_integrity(workspace_id: str, db: Session = Depends(get_db)) -> IntegrityResponse:
    """Verify hash chain integrity for all raw files in workspace."""
    raw_files = list(db.exec(select(RawFile).where(RawFile.workspace_id == workspace_id)).all())

    results: list[IntegrityResult] = []
    all_valid = True

    for rf in raw_files:
        raw_events = list(
            db.exec(
                select(RawEvent).where(RawEvent.raw_file_id == rf.id).order_by(RawEvent.line_number)  # type: ignore[arg-type]
            ).all()
        )

        original_events = []
        for re in raw_events:
            original_events.append(
                {
                    "type": re.event_type,
                    "ts": re.timestamp.isoformat(),
                    "payload": json.loads(re.payload),
                }
            )

        stored_hashes = [re.hash_chain for re in raw_events]
        valid = verify_chain(rf.filename, original_events, stored_hashes)

        if not valid:
            all_valid = False

        results.append(
            IntegrityResult(
                raw_file_id=rf.id,
                filename=rf.filename,
                valid=valid,
                event_count=len(raw_events),
            )
        )

    return IntegrityResponse(
        workspace_id=workspace_id,
        results=results,
        all_valid=all_valid,
    )
