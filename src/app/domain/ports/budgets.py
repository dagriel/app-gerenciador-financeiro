"""Budget repository port."""

from __future__ import annotations

from decimal import Decimal
from typing import Protocol, runtime_checkable

from app.domain.entities.budget import Budget


@runtime_checkable
class BudgetRepository(Protocol):
    def list_budgets_by_month(self, *, month: str) -> list[Budget]: ...

    def get_budget(self, budget_id: int) -> Budget | None: ...

    def get_budget_by_month_category(self, *, month: str, category_id: int) -> Budget | None: ...

    def upsert_budget(
        self,
        *,
        month: str,
        category_id: int,
        amount_planned: Decimal,
    ) -> Budget: ...

    def delete_budget(self, *, budget_id: int) -> bool: ...
