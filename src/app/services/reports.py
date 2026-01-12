"""Report service - generates financial reports."""

import calendar
import datetime as dt

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.models import Budget, Category, Transaction


def _month_range(month: str) -> tuple[dt.date, dt.date]:
    """Get first and last day of a month.

    Args:
        month: Month in YYYY-MM format

    Returns:
        Tuple of (first_day, last_day)
    """
    y, m = month.split("-")
    year = int(y)
    mon = int(m)
    last_day = calendar.monthrange(year, mon)[1]
    return dt.date(year, mon, 1), dt.date(year, mon, last_day)


def monthly_summary(db: Session, month: str) -> dict:
    """Generate monthly financial summary.

    Args:
        db: Database session
        month: Month in YYYY-MM format

    Returns:
        Dict with income_total, expense_total, balance, and by_category breakdown
    """
    start, end = _month_range(month)

    # Total income
    income_total = db.execute(
        select(func.coalesce(func.sum(Transaction.amount), 0))
        .where(Transaction.kind == "INCOME")
        .where(Transaction.date.between(start, end))
    ).scalar_one()

    # Total expenses (signed, will be negative)
    expense_total_signed = db.execute(
        select(func.coalesce(func.sum(Transaction.amount), 0))
        .where(Transaction.kind == "EXPENSE")
        .where(Transaction.date.between(start, end))
    ).scalar_one()

    # Get planned budgets
    budgets = db.execute(
        select(Budget.category_id, Budget.amount_planned).where(Budget.month == month)
    ).all()
    planned_map = {int(cid): float(val) for cid, val in budgets}

    # Get realized expenses by category
    realized = db.execute(
        select(Transaction.category_id, func.coalesce(func.sum(Transaction.amount), 0))
        .where(Transaction.kind == "EXPENSE")
        .where(Transaction.category_id.is_not(None))
        .where(Transaction.date.between(start, end))
        .group_by(Transaction.category_id)
    ).all()
    realized_map = {int(cid): float(val) for cid, val in realized}

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
    by_category = []
    for cid in all_cat_ids:
        planned = planned_map.get(cid, 0.0)
        realized_abs = abs(realized_map.get(cid, 0.0))
        by_category.append(
            {
                "category_id": cid,
                "category_name": cat_name.get(cid, "N/A"),
                "planned": planned,
                "realized": realized_abs,
                "deviation": realized_abs - planned,
            }
        )

    return {
        "month": month,
        "income_total": float(income_total),
        "expense_total": abs(float(expense_total_signed)),
        "balance": float(income_total + expense_total_signed),
        "by_category": by_category,
    }
