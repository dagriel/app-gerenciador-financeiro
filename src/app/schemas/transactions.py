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

    date: dt.date = Field(..., examples=["2026-01-15"])
    description: str = Field(
        default="",
        max_length=255,
        description="Descrição opcional (máx 255 caracteres).",
        examples=["Supermercado"],
    )
    amount: MoneyDecimal = Field(
        ...,
        description=(
            "Valor monetário. Despesa < 0; Receita > 0. Preferencialmente enviar como string."
        ),
        examples=["-150.50", "5000.00"],
    )
    kind: TxKind = Field(..., examples=["EXPENSE"])
    account_id: int = Field(..., examples=[1])
    category_id: int | None = Field(default=None, examples=[1])


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

    date: dt.date = Field(..., examples=["2026-01-20"])
    description: str = Field(
        default="",
        max_length=255,
        description="Descrição opcional (máx 255 caracteres).",
        examples=["Movimentação"],
    )
    amount_abs: MoneyDecimal = Field(
        ...,
        gt=0,
        description="Valor absoluto da transferência (sempre positivo). Preferencialmente string.",
        examples=["100.00"],
    )
    from_account_id: int = Field(..., examples=[1])
    to_account_id: int = Field(..., examples=[2])


class TransferOut(BaseModel):
    """Schema for transfer response."""

    pair_id: str = Field(..., examples=["c6c6a7e6-6c4d-4fbb-9c3b-0c4e9f0b7c8a"])
    out_id: int = Field(..., examples=[10])
    in_id: int = Field(..., examples=[11])
