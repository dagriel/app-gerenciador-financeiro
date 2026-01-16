from __future__ import annotations

from datetime import date
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

from babel.numbers import format_currency


def money_to_decimal(value: str) -> Decimal:
    """Converte string monetária vinda da API em Decimal quantizado (2 casas)."""
    try:
        dec = Decimal(value)
    except (InvalidOperation, TypeError) as exc:
        raise ValueError(f"Valor monetário inválido: {value!r}") from exc
    return dec.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def money_fmt_brl(value: str) -> str:
    """Formata string monetária da API em BRL pt-BR (apenas apresentação)."""
    dec = money_to_decimal(value)
    # Babel espera Decimal ou float; Decimal é o ideal.
    return format_currency(dec, "BRL", locale="pt_BR")


def today_month() -> str:
    d = date.today()
    return f"{d.year:04d}-{d.month:02d}"


def previous_month(month: str) -> str:
    """Recebe YYYY-MM e retorna o mês anterior (YYYY-MM)."""
    year_s, month_s = month.split("-")
    year = int(year_s)
    m = int(month_s)
    if m == 1:
        return f"{year - 1:04d}-12"
    return f"{year:04d}-{m - 1:02d}"


def last_n_months(n: int, *, from_month: str | None = None) -> list[str]:
    """Gera lista [YYYY-MM] dos últimos N meses (incluindo o mês base)."""
    if n <= 0:
        return []
    cur = from_month or today_month()
    out: list[str] = []
    for _ in range(n):
        out.append(cur)
        cur = previous_month(cur)
    return out
