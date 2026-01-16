from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class Account:
    """Domain entity for an account (pure Python, no ORM)."""

    id: int
    name: str
    type: str
    active: bool
