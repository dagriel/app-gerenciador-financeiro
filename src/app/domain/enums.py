"""Domain enums (framework-agnostic).

These enums are part of the domain model. They intentionally mirror the persisted/string
values used by the API contract and the database, but live in the domain layer to avoid
coupling to `app.schemas.*`.

Notes:
- We use `StrEnum` so values behave like strings (useful for comparisons and JSON).
"""

from __future__ import annotations

from enum import StrEnum


class AccountType(StrEnum):
    BANK = "BANK"
    CASH = "CASH"


class CategoryKind(StrEnum):
    INCOME = "INCOME"
    EXPENSE = "EXPENSE"


class CategoryGroup(StrEnum):
    ESSENTIAL = "ESSENTIAL"
    LIFESTYLE = "LIFESTYLE"
    FUTURE = "FUTURE"
    OTHER = "OTHER"


class TransactionKind(StrEnum):
    INCOME = "INCOME"
    EXPENSE = "EXPENSE"
    TRANSFER = "TRANSFER"
