"""Report service - generates financial reports.

Architecture goal:
- depend on ports (`uow.reports`) instead of SQLAlchemy Session or repository functions.
"""

from __future__ import annotations

from decimal import Decimal

from app.core.money import quantize_money, serialize_money, to_decimal
from app.db.uow import UnitOfWork
from app.domain.rules.reports import month_range


def monthly_summary(uow: UnitOfWork, month: str) -> dict:
    """Generate monthly financial summary.

    Monetary values are returned as strings (Decimal), always with 2 decimal places.
    """
    start, end = month_range(month)

    income_total_raw = uow.reports.sum_income(start=start, end=end)
    income_total = quantize_money(to_decimal(income_total_raw))

    expense_total_signed_raw = uow.reports.sum_expense(start=start, end=end)
    expense_total_signed = quantize_money(to_decimal(expense_total_signed_raw))

    budgets = uow.reports.list_budgets_for_month(month=month)
    planned_map = {int(cid): quantize_money(to_decimal(val)) for cid, val in budgets}

    realized = uow.reports.sum_expenses_by_category(start=start, end=end)
    realized_map = {int(cid): quantize_money(to_decimal(val)) for cid, val in realized}

    all_cat_ids = sorted(set(planned_map.keys()) | set(realized_map.keys()))
    cat_name = uow.reports.get_category_names(category_ids=all_cat_ids)

    by_category: list[dict] = []
    for cid in all_cat_ids:
        planned = planned_map.get(cid, Decimal("0"))
        realized_abs = abs(realized_map.get(cid, Decimal("0")))
        by_category.append(
            {
                "category_id": cid,
                "category_name": cat_name.get(cid, "N/A"),
                "planned": serialize_money(planned),
                "realized": serialize_money(realized_abs),
                "deviation": serialize_money(quantize_money(realized_abs - planned)),
            }
        )

    balance = quantize_money(income_total + expense_total_signed)

    return {
        "month": month,
        "income_total": serialize_money(income_total),
        "expense_total": serialize_money(abs(expense_total_signed)),
        "balance": serialize_money(balance),
        "by_category": by_category,
    }
