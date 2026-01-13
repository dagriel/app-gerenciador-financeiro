"""Reports router - Financial reports and summaries."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.reports import MonthlySummaryOut
from app.services.reports import monthly_summary

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/monthly-summary", response_model=MonthlySummaryOut)
def report_monthly_summary(month: str, db: Session = Depends(get_db)) -> dict:
    """Get monthly financial summary with budget comparison.

    Args:
        month: Month in YYYY-MM format
        db: Database session

    Returns:
        Dict with:
        - month: The queried month
        - income_total: Total income
        - expense_total: Total expenses (absolute value)
        - balance: Net balance (income - expenses)
        - by_category: List of categories with planned vs realized vs deviation
    """
    try:
        return monthly_summary(db, month)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
