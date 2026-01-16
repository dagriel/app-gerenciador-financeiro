"""Report repository port.

Relatórios são essencialmente queries de leitura/aggregations. Mantemos um port
para que a camada de aplicação (services) não precise conhecer SQLAlchemy/Session
nem chamar repositories de infra diretamente.
"""

from __future__ import annotations

import datetime as dt
from decimal import Decimal
from typing import Protocol, runtime_checkable


@runtime_checkable
class ReportRepository(Protocol):
    def sum_income(self, *, start: dt.date, end: dt.date) -> Decimal: ...

    def sum_expense(self, *, start: dt.date, end: dt.date) -> Decimal: ...

    def list_budgets_for_month(self, *, month: str) -> list[tuple[int, Decimal]]: ...

    def sum_expenses_by_category(self, *, start: dt.date, end: dt.date) -> list[tuple[int, Decimal]]: ...

    def get_category_names(self, *, category_ids: list[int]) -> dict[int, str]: ...
