from __future__ import annotations

import datetime as dt

import pytest

from app.core.error_messages import ErrorMessage
from app.core.exceptions import BadRequestError
from app.domain.rules.reports import month_range


def test_month_range_returns_first_and_last_day() -> None:
    start, end = month_range("2026-02")
    assert start == dt.date(2026, 2, 1)
    assert end == dt.date(2026, 2, 28)


@pytest.mark.parametrize(
    "month, expected",
    [
        ("2026/01", ErrorMessage.MONTH_FORMAT),
        ("2026-13", ErrorMessage.MONTH_RANGE),
        ("1800-01", ErrorMessage.MONTH_YEAR_RANGE),
    ],
)
def test_month_range_invalid_month_maps_to_bad_request(
    month: str, expected: ErrorMessage
) -> None:
    with pytest.raises(BadRequestError) as exc:
        month_range(month)

    assert exc.value.detail == expected
    assert exc.value.code == expected.name
