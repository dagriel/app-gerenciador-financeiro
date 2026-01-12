"""Transaction schemas."""

import datetime as dt
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class TxKind(StrEnum):
    """Transaction kind enum."""

    INCOME = "INCOME"
    EXPENSE = "EXPENSE"
    TRANSFER = "TRANSFER"


class TransactionCreate(BaseModel):
    """Schema for creating a transaction."""

    date: dt.date
    description: str = ""
    amount: float = Field(..., description="Despesa < 0; Receita > 0.")
    kind: TxKind
    account_id: int
    category_id: int | None = None


class TransactionOut(BaseModel):
    """Schema for transaction response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    date: dt.date
    description: str
    amount: float
    kind: TxKind
    account_id: int
    category_id: int | None
    transfer_pair_id: str | None


class TransferCreate(BaseModel):
    """Schema for creating a transfer."""

    date: dt.date
    description: str = ""
    amount_abs: float = Field(..., gt=0)
    from_account_id: int
    to_account_id: int
