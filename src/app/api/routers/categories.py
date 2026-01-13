"""Categories router - CRUD for categories."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.error_messages import ErrorMessage
from app.db.models import Category
from app.schemas.categories import CategoryCreate, CategoryOut, CategoryUpdate

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("", response_model=list[CategoryOut])
def list_categories(
    include_inactive: bool = Query(default=False),
    db: Session = Depends(get_db),
) -> list[Category]:
    """List categories.

    By default, only active categories are returned. Set include_inactive=true to include inactive.

    Args:
        include_inactive: Whether to include inactive categories in the result.
        db: Database session

    Returns:
        List of categories
    """
    q = db.query(Category)
    if not include_inactive:
        q = q.filter(Category.active == True)  # noqa: E712
    return q.order_by(Category.id.asc()).all()


@router.post("", response_model=CategoryOut, status_code=201)
def create_category(payload: CategoryCreate, db: Session = Depends(get_db)) -> Category:
    """Create a new category.

    Args:
        payload: Category creation data
        db: Database session

    Returns:
        Created category

    Raises:
        HTTPException: If category name already exists
    """
    exists = db.query(Category).filter(Category.name == payload.name).one_or_none()
    if exists:
        raise HTTPException(status_code=409, detail=ErrorMessage.CATEGORY_ALREADY_EXISTS)

    cat = Category(name=payload.name, kind=payload.kind.value, group=payload.group.value)
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return cat


@router.put("/{category_id}", response_model=CategoryOut)
def update_category(
    category_id: int, payload: CategoryUpdate, db: Session = Depends(get_db)
) -> Category:
    """Update a category.

    Args:
        category_id: Category ID
        payload: Update data
        db: Database session

    Returns:
        Updated category

    Raises:
        HTTPException: If category not found
    """
    cat = db.query(Category).filter(Category.id == category_id).one_or_none()
    if not cat:
        raise HTTPException(status_code=404, detail=ErrorMessage.CATEGORY_NOT_FOUND)

    if payload.name is not None:
        # Prevent 500 (unique constraint) and return a proper 409 instead.
        exists = (
            db.query(Category)
            .filter(Category.name == payload.name, Category.id != category_id)
            .one_or_none()
        )
        if exists:
            raise HTTPException(status_code=409, detail=ErrorMessage.CATEGORY_ALREADY_EXISTS)
        cat.name = payload.name
    if payload.kind is not None:
        cat.kind = payload.kind.value
    if payload.group is not None:
        cat.group = payload.group.value
    if payload.active is not None:
        cat.active = payload.active

    try:
        db.commit()
    except IntegrityError as e:
        db.rollback()
        # Safety net (race conditions): keep behavior consistent with create_category.
        raise HTTPException(status_code=409, detail=ErrorMessage.CATEGORY_ALREADY_EXISTS) from e
    db.refresh(cat)
    return cat


@router.delete("/{category_id}", status_code=204)
def delete_category(category_id: int, db: Session = Depends(get_db)) -> None:
    """Soft delete a category (mark as inactive).

    Args:
        category_id: Category ID
        db: Database session

    Raises:
        HTTPException: If category not found
    """
    cat = db.query(Category).filter(Category.id == category_id).one_or_none()
    if not cat:
        raise HTTPException(status_code=404, detail=ErrorMessage.CATEGORY_NOT_FOUND)

    cat.active = False
    db.commit()
