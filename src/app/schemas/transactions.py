"""Transaction schemas."""

import datetime as dt
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.types import MoneyDecimal


class TxKind(StrEnum):
    """Transaction kind enum."""

    INCOME = "INCOME"
    EXPENSE = "EXPENSE"
    TRANSFER = "TRANSFER"


class TransactionCreate(BaseModel):
    """Schema for creating a transaction."""

    date: dt.date
    description: str = ""
    amount: MoneyDecimal = Field(..., description="Despesa < 0; Receita > 0.")
    kind: TxKind
    account_id: int
    category_id: int | None = None


class TransactionOut(BaseModel):
    """Schema for transaction response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    date: dt.date
    description: str
    amount: MoneyDecimal
    kind: TxKind
    account_id: int
    category_id: int | None
    transfer_pair_id: str | None


class TransferCreate(BaseModel):
    """Schema for creating a transfer."""

    date: dt.date
    description: str = ""
    amount_abs: MoneyDecimal = Field(..., gt=0)
    from_account_id: int
    to_account_id: int


class TransferOut(BaseModel):
    """Schema for transfer response."""

    pair_id: str
    out_id: int
    in_id: int
