"""Database engine, session factory, and lifespan init."""

from collections.abc import Generator
from contextlib import contextmanager

from sqlalchemy import event, text
from sqlmodel import Session, SQLModel, create_engine

from app.config import settings

connect_args = {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(settings.DATABASE_URL, connect_args=connect_args)


@event.listens_for(engine, "connect")
def _set_sqlite_pragma(dbapi_connection, _connection_record):  # type: ignore[no-untyped-def]
    """Enable WAL mode and foreign keys for SQLite."""
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


def init_db() -> None:
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        # Create FTS5 virtual table if it doesn't exist
        session.exec(  # type: ignore[call-overload]
            text(
                "CREATE VIRTUAL TABLE IF NOT EXISTS memory_items_fts "
                "USING fts5(title, content, memory_item_id UNINDEXED)"
            )
        )
        session.commit()


@contextmanager
def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency."""
    with Session(engine) as session:
        yield session
