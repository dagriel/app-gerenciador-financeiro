"""Compatibility shim for domain/application errors.

Source of truth now lives in `app.domain.errors` (framework-agnostic).

We keep this module to preserve existing imports across the codebase while we
migrate the boundaries (FastAPI handlers) to map domain errors to HTTP status
codes.
"""

from __future__ import annotations

from app.domain.errors import (  # noqa: F401
    BadRequestError,
    ConflictError,
    DomainError,
    NotFoundError,
    UnauthorizedError,
)

__all__ = [
    "DomainError",
    "BadRequestError",
    "UnauthorizedError",
    "NotFoundError",
    "ConflictError",
]
