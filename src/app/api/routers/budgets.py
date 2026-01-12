"""Budgets router - CRUD for monthly budgets."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.db.models import Budget, Category
from app.schemas.budgets import BudgetOut, BudgetUpsert

router = APIRouter(prefix="/budgets", tags=["budgets"])


@router.get("", response_model=list[BudgetOut])
def list_budgets(month: str, db: Session = Depends(get_db)) -> list[Budget]:
    """List all budgets for a given month.

    Args:
        month: Month in YYYY-MM format
        db: Database session

    Returns:
        List of budgets for the month
    """
    return db.query(Budget).filter(Budget.month == month).order_by(Budget.id.asc()).all()


@router.post("", response_model=BudgetOut, status_code=201)
def upsert_budget(payload: BudgetUpsert, db: Session = Depends(get_db)) -> Budget:
    """Create or update a budget for a category in a month.

    Args:
        payload: Budget data
        db: Database session

    Returns:
        Created or updated budget

    Raises:
        HTTPException: For validation errors
    """
    # Validate category exists, is active, and is EXPENSE
    cat = (
        db.query(Category)
        .filter(Category.id == payload.category_id, Category.active == True)  # noqa: E712
        .one_or_none()
    )
    if not cat:
        raise HTTPException(status_code=400, detail="Categoria inválida/inativa")

    if cat.kind != "EXPENSE":
        raise HTTPException(
            status_code=400,
            detail="Orçamento só é suportado para categorias de despesa no MVP",
        )

    # Check if budget already exists (upsert logic)
    existing = (
        db.query(Budget)
        .filter(Budget.month == payload.month, Budget.category_id == payload.category_id)
        .one_or_none()
    )

    if existing:
        existing.amount_planned = payload.amount_planned
        db.commit()
        db.refresh(existing)
        return existing

    # Create new budget
    bud = Budget(
        month=payload.month,
        category_id=payload.category_id,
        amount_planned=payload.amount_planned,
    )
    db.add(bud)
    db.commit()
    db.refresh(bud)
    return bud


@router.delete("/{budget_id}", status_code=204)
def delete_budget(budget_id: int, db: Session = Depends(get_db)) -> None:
    """Delete a budget.

    Args:
        budget_id: Budget ID
        db: Database session

    Raises:
        HTTPException: If budget not found
    """
    bud = db.query(Budget).filter(Budget.id == budget_id).one_or_none()
    if not bud:
        raise HTTPException(status_code=404, detail="Orçamento não encontrado")

    db.delete(bud)
    db.commit()
