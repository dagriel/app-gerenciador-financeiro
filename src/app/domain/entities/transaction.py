from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from decimal import Decimal


@dataclass(slots=True)
class Transaction:
    """Domain entity for a financial transaction (pure Python, no ORM)."""

    id: int
    date: dt.date
    description: str
    amount: Decimal
    kind: str  # INCOME | EXPENSE | TRANSFER
    account_id: int
    category_id: int | None
    transfer_pair_id: str | None
