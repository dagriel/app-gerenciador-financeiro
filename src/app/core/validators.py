"""Small validation helpers shared across the application."""

from __future__ import annotations

from dataclasses import dataclass

from app.core.error_messages import ErrorMessage


@dataclass(frozen=True)
class ParsedMonth:
    year: int
    month: int


def parse_month_str(month: str) -> ParsedMonth:
    """Parse a YYYY-MM string and validate month range.

    Args:
        month: Month in YYYY-MM format.

    Returns:
        ParsedMonth with year and month.

    Raises:
        ValueError: If the string is not in YYYY-MM format or month is out of range.
    """
    try:
        y_str, m_str = month.split("-")
        year = int(y_str)
        mon = int(m_str)
    except Exception as exc:  # noqa: BLE001 - keep broad to normalize errors
        raise ValueError(ErrorMessage.MONTH_FORMAT) from exc

    if mon < 1 or mon > 12:
        raise ValueError(ErrorMessage.MONTH_RANGE)

    # keep a minimal sanity check for year (avoid very small/negative values)
    if year < 1900 or year > 3000:
        raise ValueError(ErrorMessage.MONTH_YEAR_RANGE)

    return ParsedMonth(year=year, month=mon)
