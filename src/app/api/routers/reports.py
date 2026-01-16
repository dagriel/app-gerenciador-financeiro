"""Reports router - Financial reports and summaries.

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
from app.schemas.reports import MonthlySummaryOut
from app.services.reports import monthly_summary

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get(
    "/monthly-summary",
    response_model=MonthlySummaryOut,
    responses=error_responses(400, 401, 422),
)
def report_monthly_summary(
    month: str = Query(
        ...,
        description="Mês no formato YYYY-MM.",
        examples=["2026-01"],
    ),
    uow: UnitOfWork = Depends(get_uow),
) -> dict:
    return monthly_summary(uow, month)
