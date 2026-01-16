"""Transactions router - CRUD for transactions including transfers.

This router is intentionally thin:
- Pydantic handles structural validation (422)
- Services handle business rules (DomainError -> ProblemDetail)
- UnitOfWork dependency handles commit/rollback
"""

from __future__ import annotations

import datetime as dt

from fastapi import APIRouter, Depends, Query

from app.api.deps import get_uow
from app.api.openapi import error_responses
from app.db.uow import UnitOfWork
from app.schemas.transactions import (
    TransactionCreate,
    TransactionOut,
    TransferCreate,
    TransferOut,
    TxKind,
)
from app.services.transactions import (
    create_transaction,
    create_transfer_transaction,
    delete_transaction,
    list_transactions,
)

router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.get("", response_model=list[TransactionOut], responses=error_responses(400, 401, 422))
def list_transactions_endpoint(
    from_date: dt.date | None = Query(
        default=None,
        description="Data inicial (YYYY-MM-DD). Deve ser enviada junto com to_date.",
        examples=["2026-01-01"],
    ),
    to_date: dt.date | None = Query(
        default=None,
        description="Data final (YYYY-MM-DD). Deve ser enviada junto com from_date.",
        examples=["2026-01-31"],
    ),
    account_id: int | None = Query(
        default=None,
        description="Filtrar por ID da conta.",
        examples=[1],
    ),
    category_id: int | None = Query(
        default=None,
        description="Filtrar por ID da categoria.",
        examples=[1],
    ),
    kind: TxKind | None = Query(
        default=None,
        description="Filtrar por tipo de transação.",
        examples=["EXPENSE"],
    ),
    uow: UnitOfWork = Depends(get_uow),
):
    return list_transactions(
        uow,
        from_date=from_date,
        to_date=to_date,
        account_id=account_id,
        category_id=category_id,
        kind=kind,
    )


@router.post(
    "",
    response_model=TransactionOut,
    status_code=201,
    responses=error_responses(400, 401, 422),
)
def create_transaction_endpoint(payload: TransactionCreate, uow: UnitOfWork = Depends(get_uow)):
    return create_transaction(uow, payload)


@router.post(
    "/transfer",
    response_model=TransferOut,
    status_code=201,
    responses=error_responses(400, 401, 422),
)
def transfer_endpoint(payload: TransferCreate, uow: UnitOfWork = Depends(get_uow)) -> dict:
    return create_transfer_transaction(uow, payload)


@router.delete("/{transaction_id}", status_code=204, responses=error_responses(401, 404, 422))
def delete_transaction_endpoint(
    transaction_id: int,
    uow: UnitOfWork = Depends(get_uow),
) -> None:
    delete_transaction(uow, transaction_id)
    return None
