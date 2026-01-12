"""Transactions router - CRUD for transactions including transfers."""

import datetime as dt
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.db.models import Account, Category, Transaction
from app.schemas.transactions import TransactionCreate, TransactionOut, TransferCreate, TxKind
from app.services.transfers import create_transfer

router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.get("", response_model=list[TransactionOut])
def list_transactions(
    from_date: dt.date | None = Query(default=None),
    to_date: dt.date | None = Query(default=None),
    account_id: int | None = None,
    category_id: int | None = None,
    kind: TxKind | None = None,
    db: Session = Depends(get_db),
) -> list[Transaction]:
    """List transactions with optional filters.

    Args:
        from_date: Start date filter
        to_date: End date filter
        account_id: Filter by account
        category_id: Filter by category
        kind: Filter by transaction kind
        db: Database session

    Returns:
        List of transactions matching filters

    Raises:
        HTTPException: If from_date or to_date provided without the other
    """
    q = db.query(Transaction)

    if (from_date is None) ^ (to_date is None):
        raise HTTPException(status_code=400, detail="Informe from_date e to_date juntos")

    if from_date and to_date:
        q = q.filter(Transaction.date.between(from_date, to_date))

    if account_id is not None:
        q = q.filter(Transaction.account_id == account_id)

    if category_id is not None:
        q = q.filter(Transaction.category_id == category_id)

    if kind is not None:
        q = q.filter(Transaction.kind == kind.value)

    return q.order_by(Transaction.date.desc(), Transaction.id.desc()).all()


@router.post("", response_model=TransactionOut, status_code=201)
def create_transaction(payload: TransactionCreate, db: Session = Depends(get_db)) -> Transaction:
    """Create a new transaction (income or expense).

    Use /transactions/transfer for transfers between accounts.

    Args:
        payload: Transaction creation data
        db: Database session

    Returns:
        Created transaction

    Raises:
        HTTPException: For validation errors
    """
    if payload.kind == TxKind.TRANSFER:
        raise HTTPException(
            status_code=400, detail="Use /transactions/transfer para transferências"
        )

    if payload.kind == TxKind.INCOME and payload.amount <= 0:
        raise HTTPException(status_code=400, detail="INCOME requer amount > 0")

    if payload.kind == TxKind.EXPENSE and payload.amount >= 0:
        raise HTTPException(status_code=400, detail="EXPENSE requer amount < 0")

    if payload.category_id is None:
        raise HTTPException(status_code=400, detail="category_id é obrigatório para INCOME/EXPENSE")

    # Validate account exists and is active
    acc = (
        db.query(Account)
        .filter(Account.id == payload.account_id, Account.active == True)  # noqa: E712
        .one_or_none()
    )
    if not acc:
        raise HTTPException(status_code=400, detail="Conta inválida/inativa")

    # Validate category exists, is active, and matches kind
    cat = (
        db.query(Category)
        .filter(Category.id == payload.category_id, Category.active == True)  # noqa: E712
        .one_or_none()
    )
    if not cat:
        raise HTTPException(status_code=400, detail="Categoria inválida/inativa")

    if payload.kind == TxKind.INCOME and cat.kind != "INCOME":
        raise HTTPException(status_code=400, detail="Categoria incompatível com INCOME")
    if payload.kind == TxKind.EXPENSE and cat.kind != "EXPENSE":
        raise HTTPException(status_code=400, detail="Categoria incompatível com EXPENSE")

    # Convert float to Decimal safely
    tx = Transaction(
        date=payload.date,
        description=payload.description,
        amount=Decimal(str(payload.amount)),
        kind=payload.kind.value,
        account_id=payload.account_id,
        category_id=payload.category_id,
    )
    db.add(tx)
    db.commit()
    db.refresh(tx)
    return tx


@router.post("/transfer", status_code=201)
def transfer(payload: TransferCreate, db: Session = Depends(get_db)) -> dict:
    """Create a transfer between two accounts.

    This creates two linked transactions (one out, one in) with the same transfer_pair_id.

    Args:
        payload: Transfer creation data
        db: Database session

    Returns:
        Dict with pair_id, out_id, and in_id

    Raises:
        HTTPException: For validation errors
    """
    try:
        return create_transfer(
            db,
            date=payload.date,
            description=payload.description,
            amount_abs=Decimal(str(payload.amount_abs)),
            from_account_id=payload.from_account_id,
            to_account_id=payload.to_account_id,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.delete("/{transaction_id}", status_code=204)
def delete_transaction(transaction_id: int, db: Session = Depends(get_db)) -> None:
    """Delete a transaction.

    For transfers, this automatically deletes both linked transactions (the pair).

    Args:
        transaction_id: Transaction ID to delete
        db: Database session

    Raises:
        HTTPException: If transaction not found
    """
    tx = db.query(Transaction).filter(Transaction.id == transaction_id).one_or_none()
    if not tx:
        raise HTTPException(status_code=404, detail="Transação não encontrada")

    # If it's a transfer, delete the entire pair
    if tx.kind == "TRANSFER" and tx.transfer_pair_id:
        db.query(Transaction).filter(Transaction.transfer_pair_id == tx.transfer_pair_id).delete(
            synchronize_session=False
        )
        db.commit()
        return None

    # Regular transaction: just delete it
    db.delete(tx)
    db.commit()
