"""Database session management."""

from functools import lru_cache

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from app.core.config import settings


@lru_cache(maxsize=1)
def get_engine() -> Engine:
    """Get or create the database engine (cached)."""
    url = settings.database_url
    connect_args = {}
    if url.startswith("sqlite"):
        connect_args = {"check_same_thread": False}

    engine = create_engine(url, future=True, connect_args=connect_args)

    # Ensure foreign keys are enforced on SQLite (disabled by default in many setups).
    if url.startswith("sqlite"):

        @event.listens_for(engine, "connect")
        def _set_sqlite_pragma(dbapi_connection, _connection_record) -> None:  # noqa: ANN001
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            # Reduce "database is locked" issues and improve read/write concurrency for local usage.
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.execute("PRAGMA busy_timeout=5000")
            cursor.close()

    return engine


def get_session() -> Session:
    """Create a new database session."""
    engine = get_engine()
    return Session(engine, autoflush=False, autocommit=False, future=True)
