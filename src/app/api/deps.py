"""API dependencies - Unit of Work and API key verification."""
from collections.abc import Generator

from fastapi import Security
from fastapi.security.api_key import APIKeyHeader

from app.core.security import verify_api_key
from app.db.session import get_session
from app.db.uow import UnitOfWork

api_key_scheme = APIKeyHeader(name="X-API-Key", auto_error=False)


def require_api_key(x_api_key: str | None = Security(api_key_scheme)) -> None:
    """Verify API key header.

    This is declared as a FastAPI Security dependency so OpenAPI/Swagger can
    expose it as a proper security scheme (Authorize button).

    Args:
        x_api_key: API key from X-API-Key header.

    Raises:
        HTTPException: If API key is invalid or missing (when enabled).
    """
    verify_api_key(x_api_key)


def get_uow() -> Generator[UnitOfWork]:
    """Get a Unit of Work for a request (commit/rollback boundary).

    Behavior:
        - Yields a UnitOfWork holding a SQLAlchemy session
        - Commits on success
        - Rolls back on any exception (including DomainError), then re-raises
    """
    with get_session() as db:
        uow = UnitOfWork(db)
        try:
            yield uow
            db.commit()
        except Exception:
            db.rollback()
            raise
