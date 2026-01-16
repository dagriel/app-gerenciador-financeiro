"""Budget repository.

Centraliza queries e operações de persistência para budgets.

Objetivo arquitetural:
- Repositories falam com ORM/SQLAlchemy.
- Services trabalham com Domain Entities (pure Python), sem importar `app.db.models`.

SQLAlchemy style:
- Prefer SQLAlchemy 2.0 `select()` + `Session.scalars()`.
"""

from __future__ import annotations

from decimal import Decimal

from typing import cast

from sqlalchemy import delete, select
from sqlalchemy.engine import CursorResult
from sqlalchemy.orm import Session

from app.db.models import Budget as BudgetModel
from app.domain.entities.budget import Budget as BudgetEntity


def _to_domain(model: BudgetModel) -> BudgetEntity:
    return BudgetEntity(
        id=model.id,
        month=model.month,
        category_id=model.category_id,
        amount_planned=model.amount_planned,
    )


def list_budgets_by_month(db: Session, *, month: str) -> list[BudgetEntity]:
    stmt = select(BudgetModel).where(BudgetModel.month == month).order_by(BudgetModel.id.asc())
    return [_to_domain(m) for m in db.scalars(stmt).all()]


def get_budget(db: Session, budget_id: int) -> BudgetEntity | None:
    stmt = select(BudgetModel).where(BudgetModel.id == budget_id)
    model = db.scalars(stmt).one_or_none()
    return _to_domain(model) if model else None


def get_budget_by_month_category(db: Session, *, month: str, category_id: int) -> BudgetEntity | None:
    stmt = select(BudgetModel).where(BudgetModel.month == month, BudgetModel.category_id == category_id)
    model = db.scalars(stmt).one_or_none()
    return _to_domain(model) if model else None


def upsert_budget(
    db: Session,
    *,
    month: str,
    category_id: int,
    amount_planned: Decimal,
) -> BudgetEntity:
    """Create or update a budget row for (month, category_id)."""
    stmt = select(BudgetModel).where(BudgetModel.month == month, BudgetModel.category_id == category_id)
    model = db.scalars(stmt).one_or_none()

    if model:
        model.amount_planned = amount_planned
        db.flush()
        return _to_domain(model)

    model = BudgetModel(month=month, category_id=category_id, amount_planned=amount_planned)
    db.add(model)
    db.flush()
    return _to_domain(model)


def delete_budget(db: Session, *, budget_id: int) -> bool:
    """Delete budget by id. Returns True if a row was deleted."""
    res = cast(CursorResult, db.execute(delete(BudgetModel).where(BudgetModel.id == budget_id)))
    return bool(res.rowcount)
