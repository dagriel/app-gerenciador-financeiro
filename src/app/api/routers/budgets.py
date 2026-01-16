"""Budgets router - CRUD for monthly budgets.

This router is intentionally thin:
- Pydantic handles structural validation (422)
- Services handle business rules (DomainError -> ProblemDetail)
- UnitOfWork dependency handles commit/rollback
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from app.api.deps import get_uow
from app.api.openapi import error_responses
from app.db.uow import UnitOfWork
from app.schemas.budgets import BudgetOut, BudgetUpsert
from app.services.budgets import delete_budget, list_budgets, upsert_budget

router = APIRouter(prefix="/budgets", tags=["budgets"])


@router.get("", response_model=list[BudgetOut], responses=error_responses(400, 401, 422))
def list_budgets_endpoint(
    month: str = Query(
        ...,
        description="Mês no formato YYYY-MM.",
        examples=["2026-01"],
    ),
    uow: UnitOfWork = Depends(get_uow),
):
    return list_budgets(uow, month=month)


@router.post(
    "",
    response_model=BudgetOut,
    status_code=201,
    responses=error_responses(400, 401, 422),
)
def upsert_budget_endpoint(payload: BudgetUpsert, uow: UnitOfWork = Depends(get_uow)):
    return upsert_budget(
        uow,
        month=payload.month,
        category_id=payload.category_id,
        amount_planned=payload.amount_planned,
    )


@router.delete("/{budget_id}", status_code=204, responses=error_responses(401, 404, 422))
def delete_budget_endpoint(budget_id: int, uow: UnitOfWork = Depends(get_uow)) -> None:
    delete_budget(uow, budget_id=budget_id)
    return None
