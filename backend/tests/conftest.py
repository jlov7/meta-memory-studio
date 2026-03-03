"""Shared test fixtures — in-memory SQLite with FTS5."""

import pathlib

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Engine, text
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from app.database import get_db
from app.main import app

# StaticPool forces all threads (test + ASGI background thread) to share
# the same in-memory SQLite connection, so TestClient sees the same tables.
TEST_ENGINE = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)


def _create_fts5(engine: Engine) -> None:
    """Create the memory_items_fts virtual table used by the pipeline."""
    with engine.connect() as conn:
        conn.execute(
            text(
                "CREATE VIRTUAL TABLE IF NOT EXISTS memory_items_fts "
                "USING fts5(title, content, memory_item_id UNINDEXED)"
            )
        )
        conn.commit()


@pytest.fixture(autouse=True)
def setup_db():
    """Create all tables + FTS5 before each test, drop after."""
    SQLModel.metadata.create_all(TEST_ENGINE)
    _create_fts5(TEST_ENGINE)
    from app.security.rate_limit import rate_limiter

    rate_limiter.clear()
    yield
    SQLModel.metadata.drop_all(TEST_ENGINE)
    with TEST_ENGINE.connect() as conn:
        conn.execute(text("DROP TABLE IF EXISTS memory_items_fts"))
        conn.commit()
    # Clear in-memory workspace registry between tests
    from app.api.workspaces import _workspaces

    _workspaces.clear()


@pytest.fixture
def session():
    """Yield a database session for direct DB tests."""
    with Session(TEST_ENGINE) as s:
        yield s


@pytest.fixture
def client(session: Session):
    """FastAPI test client with DB dependency override."""

    def _override():
        yield session

    app.dependency_overrides[get_db] = _override
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def demo_jsonl() -> str:
    """Load the demo trace JSONL from examples/."""
    path = (
        pathlib.Path(__file__).resolve().parents[1]
        / "examples"
        / "sample_traces"
        / "demo_runs.jsonl"
    )
    if not path.exists():
        # Fallback: project root
        path = (
            pathlib.Path(__file__).resolve().parents[2]
            / "examples"
            / "sample_traces"
            / "demo_runs.jsonl"
        )
    return path.read_text()
