"""Budget service (use-cases).

Application-layer orchestration for budgets.

Architecture goal:
- depend on ports (`uow.budgets`, `uow.categories`) instead of concrete repositories or SQLAlchemy.
"""

from __future__ import annotations

from decimal import Decimal

from app.core.error_messages import ErrorMessage
from app.core.exceptions import NotFoundError
from app.db.uow import UnitOfWork
from app.domain.entities.budget import Budget as BudgetEntity
from app.domain.rules.budgets import validate_budget_category, validate_budget_month


def list_budgets(uow: UnitOfWork, *, month: str) -> list[BudgetEntity]:
    validate_budget_month(month)
    return uow.budgets.list_budgets_by_month(month=month)


def upsert_budget(
    uow: UnitOfWork,
    *,
    month: str,
    category_id: int,
    amount_planned: Decimal,
) -> BudgetEntity:
    """Create or update a budget row for (month, category).

    Notes:
        This service does not commit. Commit/rollback is controlled by the request-scoped UoW.
    """
    # month is validated by schema for POST /budgets (422), but keep defensive check for reuse.
    validate_budget_month(month)

    cat = uow.categories.get_active_category(category_id)
    validate_budget_category(category_kind=cat.kind if cat else None)

    return uow.budgets.upsert_budget(
        month=month,
        category_id=category_id,
        amount_planned=amount_planned,
    )


def delete_budget(uow: UnitOfWork, *, budget_id: int) -> None:
    deleted = uow.budgets.delete_budget(budget_id=budget_id)
    if not deleted:
        raise NotFoundError(ErrorMessage.BUDGET_NOT_FOUND)
    return None
