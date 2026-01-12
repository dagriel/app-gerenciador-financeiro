"""Database session management."""

from functools import lru_cache

from sqlalchemy import create_engine
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
    return create_engine(url, future=True, connect_args=connect_args)


def get_session() -> Session:
    """Create a new database session."""
    engine = get_engine()
    return Session(engine, autoflush=False, autocommit=False, future=True)
