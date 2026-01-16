"""Domain rules for reports.

Regras puras (sem I/O) e validações/invariantes relacionadas a relatórios.
"""

from __future__ import annotations

import calendar
import datetime as dt

from app.domain.error_messages import ErrorMessage
from app.domain.errors import BadRequestError
from app.domain.validators import parse_month_str


def month_range(month: str) -> tuple[dt.date, dt.date]:
    """Get first and last day of a month (YYYY-MM), with domain error mapping.

    Raises:
        BadRequestError: When month is invalid.
    """
    try:
        parsed = parse_month_str(month)
    except ValueError as e:
        # Preserve ErrorMessage for stable "code" in ProblemDetail.
        detail = e.args[0] if e.args and isinstance(e.args[0], ErrorMessage) else str(e)
        raise BadRequestError(detail) from e

    last_day = calendar.monthrange(parsed.year, parsed.month)[1]
    return dt.date(parsed.year, parsed.month, 1), dt.date(parsed.year, parsed.month, last_day)
