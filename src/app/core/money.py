"""Money helpers.

Módulo de compatibilidade: a implementação “fonte” agora está em `app.domain.money`.

Mantemos este módulo para preservar imports existentes (services/schemas) sem
forçar uma refatoração grande de uma vez.
"""

from __future__ import annotations

from app.domain.money import MONEY_QUANT, quantize_money, serialize_money, to_decimal

__all__ = ["MONEY_QUANT", "to_decimal", "quantize_money", "serialize_money"]
