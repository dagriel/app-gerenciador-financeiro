"""Domain/application errors (framework-agnostic).

These exceptions represent business/application failures without coupling the
domain to HTTP/FastAPI.

HTTP mapping must happen at the boundary layer (FastAPI exception handlers).

Conventions:
- `detail` can be a plain string or an `ErrorMessage` enum member.
- `code` is stable and defaults to `ErrorMessage.name` when detail is an enum.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.domain.error_messages import ErrorMessage


@dataclass(eq=False)
class DomainError(Exception):
    """Base exception for domain/application errors.

    Attributes:
        detail: Human-readable message or ErrorMessage enum.
        code: Stable machine-readable code (defaults to ErrorMessage.name).
        errors: Optional structured error details (rare; mostly for validation-like cases).
    """

    detail: str | ErrorMessage
    code: str | None = None
    errors: list[dict[str, Any]] | None = None

    def __post_init__(self) -> None:
        if self.code is None and isinstance(self.detail, ErrorMessage):
            self.code = self.detail.name

    @property
    def detail_str(self) -> str:
        if isinstance(self.detail, ErrorMessage):
            return self.detail.value
        return str(self.detail)


class BadRequestError(DomainError):
    """Business rule / manual validation error (maps to HTTP 400)."""


class UnauthorizedError(DomainError):
    """Authentication/authorization error (maps to HTTP 401)."""


class NotFoundError(DomainError):
    """Missing resource error (maps to HTTP 404)."""


class ConflictError(DomainError):
    """Conflict/uniqueness error (maps to HTTP 409)."""
