"""Mount all API sub-routers."""

from fastapi import APIRouter

from app.api.drift import router as drift_router
from app.api.export import router as export_router
from app.api.health import router as health_router
from app.api.ingest import router as ingest_router
from app.api.memory import router as memory_router
from app.api.policy import router as policy_router
from app.api.runs import router as runs_router
from app.api.workspaces import router as workspaces_router

api_router = APIRouter(prefix="/api")
api_router.include_router(health_router)
api_router.include_router(workspaces_router)
api_router.include_router(ingest_router)
api_router.include_router(runs_router)
api_router.include_router(memory_router)
api_router.include_router(policy_router)
api_router.include_router(drift_router)
api_router.include_router(export_router)
