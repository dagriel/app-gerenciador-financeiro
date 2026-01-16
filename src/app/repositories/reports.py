"""Reports repository.

Centraliza queries necessárias para geração de relatórios.
"""

from __future__ import annotations

import datetime as dt
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.models import Budget, Category, Transaction


def sum_income(db: Session, *, start: dt.date, end: dt.date) -> Decimal:
    """Sum INCOME transactions amount for a date range."""
    return db.execute(
        select(func.coalesce(func.sum(Transaction.amount), 0))
        .where(Transaction.kind == "INCOME")
        .where(Transaction.date.between(start, end))
    ).scalar_one()


def sum_expense(db: Session, *, start: dt.date, end: dt.date) -> Decimal:
    """Sum EXPENSE transactions amount for a date range (signed value)."""
    return db.execute(
        select(func.coalesce(func.sum(Transaction.amount), 0))
        .where(Transaction.kind == "EXPENSE")
        .where(Transaction.date.between(start, end))
    ).scalar_one()


def list_budgets_for_month(db: Session, *, month: str) -> list[tuple[int, Decimal]]:
    """Return (category_id, amount_planned) for budgets of a given month."""
    rows = db.execute(
        select(Budget.category_id, Budget.amount_planned).where(Budget.month == month)
    ).all()
    return [(int(cid), val) for cid, val in rows]


def sum_expenses_by_category(
    db: Session, *, start: dt.date, end: dt.date
) -> list[tuple[int, Decimal]]:
    """Return (category_id, sum(amount)) for EXPENSE transactions grouped by category.

    Notes:
        - Values are signed (negative amounts for expenses).
        - Ignores rows where category_id is NULL.
    """
    rows = db.execute(
        select(Transaction.category_id, func.coalesce(func.sum(Transaction.amount), 0))
        .where(Transaction.kind == "EXPENSE")
        .where(Transaction.category_id.is_not(None))
        .where(Transaction.date.between(start, end))
        .group_by(Transaction.category_id)
    ).all()
    return [(int(cid), val) for cid, val in rows]


def get_category_names(db: Session, *, category_ids: list[int]) -> dict[int, str]:
    """Return mapping {category_id: name} for the given ids (include inactive)."""
    if not category_ids:
        return {}

    rows = db.execute(select(Category.id, Category.name).where(Category.id.in_(category_ids))).all()
    return {int(cid): name for cid, name in rows}
