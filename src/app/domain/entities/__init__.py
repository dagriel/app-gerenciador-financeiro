"""Domain entities (pure Python / no ORM).

These entities represent the domain state independently from persistence concerns.
Repositories are responsible for mapping ORM models <-> domain entities.
"""

from __future__ import annotations

from app.domain.entities.account import Account
from app.domain.entities.budget import Budget
from app.domain.entities.category import Category
from app.domain.entities.transaction import Transaction

__all__ = ["Account", "Category", "Transaction", "Budget"]
