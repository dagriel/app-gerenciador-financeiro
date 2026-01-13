"""Shared schema types.

This module keeps Pydantic-specific helpers (validators/serializers) in the schemas layer.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Annotated

from pydantic import BeforeValidator, PlainSerializer

from app.core.money import quantize_money, serialize_money, to_decimal


def _to_money_decimal(v: object) -> Decimal:
    return quantize_money(to_decimal(v))


MoneyDecimal = Annotated[
    Decimal,
    BeforeValidator(_to_money_decimal),
    PlainSerializer(serialize_money, return_type=str, when_used="json"),
]
