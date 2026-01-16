"""Transaction repository.

Centralizes Transaction persistence/queries.

Objetivo arquitetural:
- Repositories falam com ORM/SQLAlchemy.
- Services trabalham com Domain Entities (pure Python), sem importar `app.db.models`.

SQLAlchemy style:
- Prefer SQLAlchemy 2.0 `select()`/`delete()` + `Session.scalars()`/`Session.execute()`.
"""

from __future__ import annotations

import datetime as dt
from decimal import Decimal
from typing import cast

from sqlalchemy import delete, select
from sqlalchemy.engine import CursorResult
from sqlalchemy.orm import Session

from app.db.models import Transaction as TransactionModel
from app.domain.entities.transaction import Transaction as TransactionEntity


def _to_domain(model: TransactionModel) -> TransactionEntity:
    return TransactionEntity(
        id=model.id,
        date=model.date,
        description=model.description,
        amount=model.amount,
        kind=model.kind,
        account_id=model.account_id,
        category_id=model.category_id,
        transfer_pair_id=model.transfer_pair_id,
    )


def get_transaction(db: Session, transaction_id: int) -> TransactionEntity | None:
    stmt = select(TransactionModel).where(TransactionModel.id == transaction_id)
    model = db.scalars(stmt).one_or_none()
    return _to_domain(model) if model else None


def list_transactions(
    db: Session,
    *,
    from_date: dt.date | None,
    to_date: dt.date | None,
    account_id: int | None,
    category_id: int | None,
    kind: str | None,
) -> list[TransactionEntity]:
    stmt = select(TransactionModel)

    if from_date and to_date:
        stmt = stmt.where(TransactionModel.date.between(from_date, to_date))

    if account_id is not None:
        stmt = stmt.where(TransactionModel.account_id == account_id)

    if category_id is not None:
        stmt = stmt.where(TransactionModel.category_id == category_id)

    if kind is not None:
        stmt = stmt.where(TransactionModel.kind == kind)

    stmt = stmt.order_by(TransactionModel.date.desc(), TransactionModel.id.desc())
    return [_to_domain(m) for m in db.scalars(stmt).all()]


def create_transaction(
    db: Session,
    *,
    date: dt.date,
    description: str,
    amount: Decimal,
    kind: str,
    account_id: int,
    category_id: int | None,
    transfer_pair_id: str | None = None,
) -> TransactionEntity:
    model = TransactionModel(
        date=date,
        description=description,
        amount=amount,
        kind=kind,
        account_id=account_id,
        category_id=category_id,
        transfer_pair_id=transfer_pair_id,
    )
    db.add(model)
    db.flush()  # populate PK without committing
    return _to_domain(model)


def create_transfer_pair(
    db: Session,
    *,
    date: dt.date,
    description: str,
    amount_abs: Decimal,
    from_account_id: int,
    to_account_id: int,
    pair_id: str,
) -> tuple[TransactionEntity, TransactionEntity]:
    out_model = TransactionModel(
        date=date,
        description=description,
        amount=-amount_abs,
        kind="TRANSFER",
        account_id=from_account_id,
        category_id=None,
        transfer_pair_id=pair_id,
    )
    in_model = TransactionModel(
        date=date,
        description=description,
        amount=amount_abs,
        kind="TRANSFER",
        account_id=to_account_id,
        category_id=None,
        transfer_pair_id=pair_id,
    )

    db.add_all([out_model, in_model])
    db.flush()  # populate PKs without committing
    return _to_domain(out_model), _to_domain(in_model)


def delete_transaction_by_id(db: Session, *, transaction_id: int) -> bool:
    res = cast(CursorResult, db.execute(delete(TransactionModel).where(TransactionModel.id == transaction_id)))
    return bool(res.rowcount)


def delete_transfer_pair(db: Session, *, transfer_pair_id: str) -> int:
    res = cast(
        CursorResult,
        db.execute(delete(TransactionModel).where(TransactionModel.transfer_pair_id == transfer_pair_id)),
    )
    return int(res.rowcount or 0)
