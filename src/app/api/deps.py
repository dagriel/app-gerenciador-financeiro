"""API dependencies - database session and API key verification."""

from collections.abc import Generator

from fastapi import Header
from sqlalchemy.orm import Session

from app.core.security import verify_api_key
from app.db.session import get_session


def require_api_key(x_api_key: str | None = Header(default=None)) -> None:
    """Verify API key header.

    Args:
        x_api_key: API key from X-API-Key header

    Raises:
        HTTPException: If API key is invalid or missing (when enabled)
    """
    verify_api_key(x_api_key)


def get_db() -> Generator[Session]:
    """Get database session.

    Yields:
        Database session
    """
    with get_session() as db:
        yield db
