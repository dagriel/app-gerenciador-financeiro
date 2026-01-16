from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal


@dataclass(slots=True)
class Budget:
    """Domain entity for a monthly budget (pure Python, no ORM)."""

    id: int
    month: str  # YYYY-MM
    category_id: int
    amount_planned: Decimal
