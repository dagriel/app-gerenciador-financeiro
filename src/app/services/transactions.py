"""Transaction service (use-cases) - business rules for transactions and transfers.

Architecture goal:
- depend on ports (`uow.transactions`, `uow.accounts`, `uow.categories`) instead of
  concrete repositories or SQLAlchemy.
"""

from __future__ import annotations

import datetime as dt

from app.core.error_messages import ErrorMessage
from app.core.exceptions import BadRequestError, NotFoundError
from app.db.uow import UnitOfWork
from app.domain.entities.transaction import Transaction as TransactionEntity
from app.domain.rules.transactions import (
    validate_category_compatibility,
    validate_transaction_payload,
)
from app.schemas.transactions import TransactionCreate, TransferCreate, TxKind
from app.services.transfers import create_transfer


def list_transactions(
    uow: UnitOfWork,
    *,
    from_date: dt.date | None,
    to_date: dt.date | None,
    account_id: int | None,
    category_id: int | None,
    kind: TxKind | None,
) -> list[TransactionEntity]:
    """List transactions with optional filters."""
    if (from_date is None) ^ (to_date is None):
        raise BadRequestError(ErrorMessage.TX_FROM_TO_BOTH_REQUIRED)

    kind_value = kind.value if kind is not None else None

    return uow.transactions.list_transactions(
        from_date=from_date,
        to_date=to_date,
        account_id=account_id,
        category_id=category_id,
        kind=kind_value,
    )


def create_transaction(uow: UnitOfWork, payload: TransactionCreate) -> TransactionEntity:
    """Create an INCOME or EXPENSE transaction."""
    validate_transaction_payload(
        kind=payload.kind.value,
        amount=payload.amount,
        category_id=payload.category_id,
    )

    # After domain validation, category_id is guaranteed to be present.
    assert payload.category_id is not None
    category_id = payload.category_id

    # Validate account exists and is active
    if not uow.accounts.get_active_account(payload.account_id):
        raise BadRequestError(ErrorMessage.ACCOUNT_INVALID_OR_INACTIVE)

    # Validate category exists, is active, and matches kind
    cat = uow.categories.get_active_category(category_id)
    validate_category_compatibility(
        kind=payload.kind.value,
        category_kind=cat.kind if cat else None,
    )

    return uow.transactions.create_transaction(
        date=payload.date,
        description=payload.description,
        amount=payload.amount,
        kind=payload.kind.value,
        account_id=payload.account_id,
        category_id=payload.category_id,
    )


def create_transfer_transaction(uow: UnitOfWork, payload: TransferCreate) -> dict:
    """Create a transfer between two accounts (creates two linked transactions)."""
    return create_transfer(
        uow,
        date=payload.date,
        description=payload.description,
        amount_abs=payload.amount_abs,
        from_account_id=payload.from_account_id,
        to_account_id=payload.to_account_id,
    )


def delete_transaction(uow: UnitOfWork, transaction_id: int) -> None:
    """Delete a transaction (and its transfer pair, if applicable)."""
    tx = uow.transactions.get_transaction(transaction_id)
    if not tx:
        raise NotFoundError(ErrorMessage.TX_NOT_FOUND)

    if tx.kind == "TRANSFER" and tx.transfer_pair_id:
        uow.transactions.delete_transfer_pair(transfer_pair_id=tx.transfer_pair_id)
        return None

    deleted = uow.transactions.delete_transaction_by_id(transaction_id=transaction_id)
    if not deleted:
        # Rare race condition: was deleted after we fetched it.
        raise NotFoundError(ErrorMessage.TX_NOT_FOUND)

    return None
