"""Report schemas.

Even though report services may return plain dicts, defining response models improves:
- OpenAPI/Swagger documentation
- Type checking / consistency
- Contract clarity (especially for money as string)

Money fields use MoneyDecimal, which serializes to string with 2 decimal places.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from app.schemas.types import MoneyDecimal


class MonthlySummaryByCategoryOut(BaseModel):
    """Category breakdown inside the monthly summary report."""

    category_id: int
    category_name: str
    planned: MoneyDecimal
    realized: MoneyDecimal
    deviation: MoneyDecimal


class MonthlySummaryOut(BaseModel):
    """Monthly summary report output."""

    model_config = ConfigDict(extra="forbid")

    month: str
    income_total: MoneyDecimal
    expense_total: MoneyDecimal
    balance: MoneyDecimal
    by_category: list[MonthlySummaryByCategoryOut]
