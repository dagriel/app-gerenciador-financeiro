"""Accounts router - CRUD for accounts."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.error_messages import ErrorMessage
from app.db.models import Account
from app.schemas.accounts import AccountCreate, AccountOut, AccountUpdate

router = APIRouter(prefix="/accounts", tags=["accounts"])


@router.get("", response_model=list[AccountOut])
def list_accounts(
    include_inactive: bool = Query(default=False),
    db: Session = Depends(get_db),
) -> list[Account]:
    """List accounts.

    By default, only active accounts are returned. Set include_inactive=true to include inactive.

    Args:
        include_inactive: Whether to include inactive accounts in the result.
        db: Database session

    Returns:
        List of accounts
    """
    q = db.query(Account)
    if not include_inactive:
        q = q.filter(Account.active == True)  # noqa: E712
    return q.order_by(Account.id.asc()).all()


@router.post("", response_model=AccountOut, status_code=201)
def create_account(payload: AccountCreate, db: Session = Depends(get_db)) -> Account:
    """Create a new account.

    Args:
        payload: Account creation data
        db: Database session

    Returns:
        Created account
    """
    acc = Account(name=payload.name, type=payload.type)
    db.add(acc)
    db.commit()
    db.refresh(acc)
    return acc


@router.put("/{account_id}", response_model=AccountOut)
def update_account(
    account_id: int, payload: AccountUpdate, db: Session = Depends(get_db)
) -> Account:
    """Update an account.

    Args:
        account_id: Account ID
        payload: Update data
        db: Database session

    Returns:
        Updated account

    Raises:
        HTTPException: If account not found
    """
    acc = db.query(Account).filter(Account.id == account_id).one_or_none()
    if not acc:
        raise HTTPException(status_code=404, detail=ErrorMessage.ACCOUNT_NOT_FOUND)

    if payload.name is not None:
        acc.name = payload.name
    if payload.type is not None:
        acc.type = payload.type
    if payload.active is not None:
        acc.active = payload.active

    db.commit()
    db.refresh(acc)
    return acc


@router.delete("/{account_id}", status_code=204)
def delete_account(account_id: int, db: Session = Depends(get_db)) -> None:
    """Soft delete an account (mark as inactive).

    Args:
        account_id: Account ID
        db: Database session

    Raises:
        HTTPException: If account not found
    """
    acc = db.query(Account).filter(Account.id == account_id).one_or_none()
    if not acc:
        raise HTTPException(status_code=404, detail=ErrorMessage.ACCOUNT_NOT_FOUND)

    acc.active = False
    db.commit()
