"""Money helpers (domain-level).

This module avoids floating point issues by normalizing values as Decimal and
quantizing to 2 decimal places.
"""

from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal, InvalidOperation
from typing import Any

MONEY_QUANT = Decimal("0.01")


def to_decimal(v: Any) -> Decimal:
    """Convert a JSON-like value to Decimal safely.

    Accepts: str | int | float | Decimal.
    Floats are normalized via str(v) to reduce binary-float artifacts.
    """
    if isinstance(v, Decimal):
        return v
    try:
        return Decimal(str(v))
    except (InvalidOperation, ValueError, TypeError) as exc:
        raise ValueError("valor monetário inválido") from exc


def quantize_money(v: Decimal) -> Decimal:
    """Force 2 decimal places using HALF_UP rounding."""
    return v.quantize(MONEY_QUANT, rounding=ROUND_HALF_UP)


def serialize_money(v: Decimal) -> str:
    """Serialize Decimal to string (2 decimal places) without scientific notation."""
    return format(quantize_money(v), "f")
