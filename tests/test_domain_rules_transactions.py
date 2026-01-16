from __future__ import annotations

from decimal import Decimal

import pytest

from app.core.error_messages import ErrorMessage
from app.core.exceptions import BadRequestError
from app.domain.rules.transactions import (
    validate_category_compatibility,
    validate_new_transfer,
    validate_transaction_payload,
)


def test_validate_transaction_payload_rejects_transfer_kind() -> None:
    with pytest.raises(BadRequestError) as exc:
        validate_transaction_payload(kind="TRANSFER", amount=Decimal("10.00"), category_id=1)

    assert exc.value.detail == ErrorMessage.TX_USE_TRANSFER_ENDPOINT
    assert exc.value.code == ErrorMessage.TX_USE_TRANSFER_ENDPOINT.name


def test_validate_transaction_payload_income_requires_amount_gt_0() -> None:
    with pytest.raises(BadRequestError) as exc:
        validate_transaction_payload(kind="INCOME", amount=Decimal("0.00"), category_id=1)

    assert exc.value.detail == ErrorMessage.TX_INCOME_REQUIRES_AMOUNT_GT_0
    assert exc.value.code == ErrorMessage.TX_INCOME_REQUIRES_AMOUNT_GT_0.name


def test_validate_transaction_payload_expense_requires_amount_lt_0() -> None:
    with pytest.raises(BadRequestError) as exc:
        validate_transaction_payload(kind="EXPENSE", amount=Decimal("0.00"), category_id=1)

    assert exc.value.detail == ErrorMessage.TX_EXPENSE_REQUIRES_AMOUNT_LT_0
    assert exc.value.code == ErrorMessage.TX_EXPENSE_REQUIRES_AMOUNT_LT_0.name


def test_validate_transaction_payload_requires_category_id() -> None:
    with pytest.raises(BadRequestError) as exc:
        validate_transaction_payload(kind="INCOME", amount=Decimal("10.00"), category_id=None)

    assert exc.value.detail == ErrorMessage.TX_CATEGORY_ID_REQUIRED
    assert exc.value.code == ErrorMessage.TX_CATEGORY_ID_REQUIRED.name


def test_validate_category_compatibility_requires_active_category() -> None:
    with pytest.raises(BadRequestError) as exc:
        validate_category_compatibility(kind="INCOME", category_kind=None)

    assert exc.value.detail == ErrorMessage.CATEGORY_INVALID_OR_INACTIVE
    assert exc.value.code == ErrorMessage.CATEGORY_INVALID_OR_INACTIVE.name


def test_validate_category_compatibility_income_requires_income_category() -> None:
    with pytest.raises(BadRequestError) as exc:
        validate_category_compatibility(kind="INCOME", category_kind="EXPENSE")

    assert exc.value.detail == ErrorMessage.TX_CATEGORY_INCOMPATIBLE_INCOME
    assert exc.value.code == ErrorMessage.TX_CATEGORY_INCOMPATIBLE_INCOME.name


def test_validate_category_compatibility_expense_requires_expense_category() -> None:
    with pytest.raises(BadRequestError) as exc:
        validate_category_compatibility(kind="EXPENSE", category_kind="INCOME")

    assert exc.value.detail == ErrorMessage.TX_CATEGORY_INCOMPATIBLE_EXPENSE
    assert exc.value.code == ErrorMessage.TX_CATEGORY_INCOMPATIBLE_EXPENSE.name


def test_validate_new_transfer_rejects_same_accounts() -> None:
    with pytest.raises(BadRequestError) as exc:
        validate_new_transfer(amount_abs=Decimal("10.00"), from_account_id=1, to_account_id=1)

    assert exc.value.detail == ErrorMessage.TRANSFER_SAME_ACCOUNTS
    assert exc.value.code == ErrorMessage.TRANSFER_SAME_ACCOUNTS.name


def test_validate_new_transfer_requires_positive_amount_abs() -> None:
    with pytest.raises(BadRequestError) as exc:
        validate_new_transfer(amount_abs=Decimal("0.00"), from_account_id=1, to_account_id=2)

    assert exc.value.detail == ErrorMessage.TRANSFER_AMOUNT_ABS_GT_0
    assert exc.value.code == ErrorMessage.TRANSFER_AMOUNT_ABS_GT_0.name
