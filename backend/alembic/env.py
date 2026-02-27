"""Alembic environment configuration."""

from sqlmodel import SQLModel

import app.models  # noqa: F401
from alembic import context
from app.database import engine

target_metadata = SQLModel.metadata


def run_migrations_online() -> None:
    connectable = engine
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


run_migrations_online()
