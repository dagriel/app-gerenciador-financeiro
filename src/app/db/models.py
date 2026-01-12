"""Database models."""

import datetime as dt
import uuid
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Account(Base):
    """Bank account or wallet."""

    __tablename__ = "accounts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    type: Mapped[str] = mapped_column(String(40), default="BANK", nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime, default=dt.datetime.utcnow, nullable=False
    )


class Category(Base):
    """Transaction category."""

    __tablename__ = "categories"
    __table_args__ = (UniqueConstraint("name", name="uq_category_name"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    kind: Mapped[str] = mapped_column(String(20), nullable=False)  # INCOME | EXPENSE
    group: Mapped[str] = mapped_column(
        String(20), nullable=False
    )  # ESSENTIAL | LIFESTYLE | FUTURE | OTHER
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class Transaction(Base):
    """Financial transaction (income, expense, or transfer)."""

    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    date: Mapped[dt.date] = mapped_column(Date, index=True, nullable=False)
    description: Mapped[str] = mapped_column(String(255), default="", nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)

    kind: Mapped[str] = mapped_column(String(20), nullable=False)  # INCOME | EXPENSE | TRANSFER
    account_id: Mapped[int] = mapped_column(ForeignKey("accounts.id"), index=True, nullable=False)
    category_id: Mapped[int | None] = mapped_column(
        ForeignKey("categories.id"), index=True, nullable=True
    )

    transfer_pair_id: Mapped[str | None] = mapped_column(String(36), index=True, nullable=True)
    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime, default=dt.datetime.utcnow, nullable=False
    )

    account = relationship("Account")
    category = relationship("Category")


class Budget(Base):
    """Monthly budget for a category."""

    __tablename__ = "budgets"
    __table_args__ = (UniqueConstraint("month", "category_id", name="uq_budget_month_category"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    month: Mapped[str] = mapped_column(String(7), index=True, nullable=False)  # YYYY-MM
    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id"), index=True, nullable=False
    )
    amount_planned: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)

    category = relationship("Category")


def new_pair_id() -> str:
    """Generate a new UUID for transfer pair tracking."""
    return str(uuid.uuid4())
