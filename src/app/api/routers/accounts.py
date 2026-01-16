"""Accounts router - CRUD for accounts.

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
from app.schemas.accounts import AccountCreate, AccountOut, AccountUpdate
from app.services.accounts import create_account, delete_account, list_accounts, update_account

router = APIRouter(prefix="/accounts", tags=["accounts"])


@router.get("", response_model=list[AccountOut], responses=error_responses(401, 422))
def list_accounts_endpoint(
    include_inactive: bool = Query(default=False),
    uow: UnitOfWork = Depends(get_uow),
):
    return list_accounts(uow, include_inactive=include_inactive)


@router.post(
    "",
    response_model=AccountOut,
    status_code=201,
    responses=error_responses(401, 409, 422),
)
def create_account_endpoint(payload: AccountCreate, uow: UnitOfWork = Depends(get_uow)):
    return create_account(uow, name=payload.name, type_=payload.type)


@router.put(
    "/{account_id}",
    response_model=AccountOut,
    responses=error_responses(401, 404, 409, 422),
)
def update_account_endpoint(
    account_id: int,
    payload: AccountUpdate,
    uow: UnitOfWork = Depends(get_uow),
):
    return update_account(
        uow,
        account_id=account_id,
        name=payload.name,
        type_=payload.type,
        active=payload.active,
    )


@router.delete("/{account_id}", status_code=204, responses=error_responses(401, 404, 422))
def delete_account_endpoint(account_id: int, uow: UnitOfWork = Depends(get_uow)) -> None:
    delete_account(uow, account_id=account_id)
    return None
