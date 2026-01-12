"""Accounts router - CRUD for accounts."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.db.models import Account
from app.schemas.accounts import AccountCreate, AccountOut, AccountUpdate

router = APIRouter(prefix="/accounts", tags=["accounts"])


@router.get("", response_model=list[AccountOut])
def list_accounts(db: Session = Depends(get_db)) -> list[Account]:
    """List all accounts.

    Args:
        db: Database session

    Returns:
        List of accounts
    """
    return db.query(Account).order_by(Account.id.asc()).all()


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
        raise HTTPException(status_code=404, detail="Conta não encontrada")

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
        raise HTTPException(status_code=404, detail="Conta não encontrada")

    acc.active = False
    db.commit()
