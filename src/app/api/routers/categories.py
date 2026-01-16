"""Categories router - CRUD for categories.

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
from app.schemas.categories import CategoryCreate, CategoryOut, CategoryUpdate
from app.services.categories import (
    create_category,
    delete_category,
    list_categories,
    update_category,
)

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("", response_model=list[CategoryOut], responses=error_responses(401, 422))
def list_categories_endpoint(
    include_inactive: bool = Query(default=False),
    uow: UnitOfWork = Depends(get_uow),
):
    return list_categories(uow, include_inactive=include_inactive)


@router.post(
    "",
    response_model=CategoryOut,
    status_code=201,
    responses=error_responses(401, 409, 422),
)
def create_category_endpoint(payload: CategoryCreate, uow: UnitOfWork = Depends(get_uow)):
    return create_category(
        uow,
        name=payload.name,
        kind=payload.kind.value,
        group=payload.group.value,
    )


@router.put(
    "/{category_id}",
    response_model=CategoryOut,
    responses=error_responses(401, 404, 409, 422),
)
def update_category_endpoint(
    category_id: int,
    payload: CategoryUpdate,
    uow: UnitOfWork = Depends(get_uow),
):
    return update_category(
        uow,
        category_id=category_id,
        name=payload.name,
        kind=payload.kind.value if payload.kind is not None else None,
        group=payload.group.value if payload.group is not None else None,
        active=payload.active,
    )


@router.delete("/{category_id}", status_code=204, responses=error_responses(401, 404, 422))
def delete_category_endpoint(category_id: int, uow: UnitOfWork = Depends(get_uow)) -> None:
    delete_category(uow, category_id=category_id)
    return None
