"""Domain Money (Value Object helpers).

Centraliza regras e helpers de dinheiro no domínio para evitar problemas de
precisão de float e manter normalização/serialização consistentes.

Obs.: o projeto ainda expõe `app.core.money` por compatibilidade, mas a
implementação “fonte” passa a ficar aqui.
"""

from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal, InvalidOperation
from typing import Any

MONEY_QUANT = Decimal("0.01")


def to_decimal(v: Any) -> Decimal:
    """Convert a JSON-like value to Decimal safely.

    Accepts: str | int | float | Decimal.
    Floats are normalized via str(v) to reduce binary-float artifacts.

    Raises:
        ValueError: When the input cannot be converted to Decimal.
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
