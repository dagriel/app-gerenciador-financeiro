"""Report service - generates financial reports."""

import calendar
import datetime as dt
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.money import quantize_money, serialize_money, to_decimal
from app.core.validators import parse_month_str
from app.db.models import Budget, Category, Transaction


def _month_range(month: str) -> tuple[dt.date, dt.date]:
    """Get first and last day of a month.

    Args:
        month: Month in YYYY-MM format

    Returns:
        Tuple of (first_day, last_day)

    Raises:
        ValueError: If month is invalid.
    """
    parsed = parse_month_str(month)
    last_day = calendar.monthrange(parsed.year, parsed.month)[1]
    return dt.date(parsed.year, parsed.month, 1), dt.date(parsed.year, parsed.month, last_day)


def monthly_summary(db: Session, month: str) -> dict:
    """Generate monthly financial summary.

    Monetary values are returned as strings (Decimal), always with 2 decimal places.

    Args:
        db: Database session
        month: Month in YYYY-MM format

    Returns:
        Dict with income_total, expense_total, balance, and by_category breakdown
    """
    start, end = _month_range(month)

    # Total income
    income_total_raw = db.execute(
        select(func.coalesce(func.sum(Transaction.amount), 0))
        .where(Transaction.kind == "INCOME")
        .where(Transaction.date.between(start, end))
    ).scalar_one()
    income_total = quantize_money(to_decimal(income_total_raw))

    # Total expenses (signed, will be negative)
    expense_total_signed_raw = db.execute(
        select(func.coalesce(func.sum(Transaction.amount), 0))
        .where(Transaction.kind == "EXPENSE")
        .where(Transaction.date.between(start, end))
    ).scalar_one()
    expense_total_signed = quantize_money(to_decimal(expense_total_signed_raw))

    # Get planned budgets
    budgets = db.execute(
        select(Budget.category_id, Budget.amount_planned).where(Budget.month == month)
    ).all()
    planned_map = {int(cid): quantize_money(to_decimal(val)) for cid, val in budgets}

    # Get realized expenses by category (signed values, negative)
    realized = db.execute(
        select(Transaction.category_id, func.coalesce(func.sum(Transaction.amount), 0))
        .where(Transaction.kind == "EXPENSE")
        .where(Transaction.category_id.is_not(None))
        .where(Transaction.date.between(start, end))
        .group_by(Transaction.category_id)
    ).all()
    realized_map = {int(cid): quantize_money(to_decimal(val)) for cid, val in realized}

    # Get all category IDs involved (planned or realized)
    all_cat_ids = sorted(set(planned_map.keys()) | set(realized_map.keys()))

    # Get category names (include inactive to preserve history)
    if all_cat_ids:
        categories = db.execute(
            select(Category.id, Category.name).where(Category.id.in_(all_cat_ids))
        ).all()
    else:
        categories = []

    cat_name = {int(cid): name for cid, name in categories}

    # Build by_category breakdown
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
