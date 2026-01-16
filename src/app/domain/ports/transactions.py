"""Transaction repository port."""

from __future__ import annotations

import datetime as dt
from decimal import Decimal
from typing import Protocol, runtime_checkable

from app.domain.entities.transaction import Transaction


@runtime_checkable
class TransactionRepository(Protocol):
    def get_transaction(self, transaction_id: int) -> Transaction | None: ...

    def list_transactions(
        self,
        *,
        from_date: dt.date | None,
        to_date: dt.date | None,
        account_id: int | None,
        category_id: int | None,
        kind: str | None,
    ) -> list[Transaction]: ...

    def create_transaction(
        self,
        *,
        date: dt.date,
        description: str,
        amount: Decimal,
        kind: str,
        account_id: int,
        category_id: int | None,
        transfer_pair_id: str | None = None,
    ) -> Transaction: ...

    def create_transfer_pair(
        self,
        *,
        date: dt.date,
        description: str,
        amount_abs: Decimal,
        from_account_id: int,
        to_account_id: int,
        pair_id: str,
    ) -> tuple[Transaction, Transaction]: ...

    def delete_transaction_by_id(self, *, transaction_id: int) -> bool: ...

    def delete_transfer_pair(self, *, transfer_pair_id: str) -> int: ...
