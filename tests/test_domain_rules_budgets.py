from __future__ import annotations

import pytest

from app.core.error_messages import ErrorMessage
from app.core.exceptions import BadRequestError
from app.domain.rules.budgets import validate_budget_category, validate_budget_month


def test_validate_budget_month_accepts_valid_month() -> None:
    # Should not raise
    validate_budget_month("2026-01")


@pytest.mark.parametrize(
    "month, expected",
    [
        ("2026/01", ErrorMessage.MONTH_FORMAT),
        ("2026-13", ErrorMessage.MONTH_RANGE),
        ("1800-01", ErrorMessage.MONTH_YEAR_RANGE),
    ],
)
def test_validate_budget_month_rejects_invalid_month(month: str, expected: ErrorMessage) -> None:
    with pytest.raises(BadRequestError) as exc:
        validate_budget_month(month)

    assert exc.value.detail == expected
    assert exc.value.code == expected.name


def test_validate_budget_category_requires_active_category() -> None:
    with pytest.raises(BadRequestError) as exc:
        validate_budget_category(category_kind=None)

    assert exc.value.detail == ErrorMessage.CATEGORY_INVALID_OR_INACTIVE
    assert exc.value.code == ErrorMessage.CATEGORY_INVALID_OR_INACTIVE.name


def test_validate_budget_category_only_allows_expense_in_mvp() -> None:
    with pytest.raises(BadRequestError) as exc:
        validate_budget_category(category_kind="INCOME")

    assert exc.value.detail == ErrorMessage.BUDGET_ONLY_EXPENSE_MVP
    assert exc.value.code == ErrorMessage.BUDGET_ONLY_EXPENSE_MVP.name
