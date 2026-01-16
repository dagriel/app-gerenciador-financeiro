from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class Category:
    """Domain entity for a category (pure Python, no ORM)."""

    id: int
    name: str
    kind: str  # INCOME | EXPENSE
    group: str  # ESSENTIAL | LIFESTYLE | FUTURE | OTHER
    active: bool
