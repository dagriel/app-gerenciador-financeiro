"""Domain rules for budgets.

Regras puras (sem I/O) e validações de invariantes relacionadas a orçamentos.
"""

from __future__ import annotations

from app.domain.error_messages import ErrorMessage
from app.domain.errors import BadRequestError
from app.domain.validators import parse_month_str


def validate_budget_month(month: str) -> None:
    """Validate month string for budget operations (YYYY-MM).

    Raises:
        BadRequestError: When month is invalid.
    """
    try:
        parse_month_str(month)
    except ValueError as e:
        # Preserve ErrorMessage for stable "code" in ProblemDetail.
        detail = e.args[0] if e.args and isinstance(e.args[0], ErrorMessage) else str(e)
        raise BadRequestError(detail) from e


def validate_budget_category(*, category_kind: str | None) -> None:
    """Validate that the category exists/is active and is EXPENSE (MVP rule)."""
    if category_kind is None:
        raise BadRequestError(ErrorMessage.CATEGORY_INVALID_OR_INACTIVE)

    if category_kind != "EXPENSE":
        raise BadRequestError(ErrorMessage.BUDGET_ONLY_EXPENSE_MVP)
