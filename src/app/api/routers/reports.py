"""Reports router - Financial reports and summaries."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.services.reports import monthly_summary

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/monthly-summary")
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
    return monthly_summary(db, month)
