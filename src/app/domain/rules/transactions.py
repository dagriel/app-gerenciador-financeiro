"""Domain rules for transactions.

Regras de domínio devem ser puras (sem I/O, sem acesso a banco) e receber apenas
os dados necessários para validar invariantes.

Essas funções levantam `BadRequestError` com `ErrorMessage` para manter o
contrato de erro estável (ProblemDetail).
"""

from __future__ import annotations

from decimal import Decimal

from app.domain.error_messages import ErrorMessage
from app.domain.errors import BadRequestError


def validate_transaction_payload(
    *,
    kind: str,
    amount: Decimal,
    category_id: int | None,
) -> None:
    """Validate payload invariants for INCOME/EXPENSE transactions (no DB required)."""
    if kind == "TRANSFER":
        raise BadRequestError(ErrorMessage.TX_USE_TRANSFER_ENDPOINT)

    if kind == "INCOME" and amount <= 0:
        raise BadRequestError(ErrorMessage.TX_INCOME_REQUIRES_AMOUNT_GT_0)

    if kind == "EXPENSE" and amount >= 0:
        raise BadRequestError(ErrorMessage.TX_EXPENSE_REQUIRES_AMOUNT_LT_0)

    if category_id is None:
        raise BadRequestError(ErrorMessage.TX_CATEGORY_ID_REQUIRED)


def validate_category_compatibility(*, kind: str, category_kind: str | None) -> None:
    """Validate that the category exists/is active and matches the transaction kind."""
    if category_kind is None:
        raise BadRequestError(ErrorMessage.CATEGORY_INVALID_OR_INACTIVE)

    if kind == "INCOME" and category_kind != "INCOME":
        raise BadRequestError(ErrorMessage.TX_CATEGORY_INCOMPATIBLE_INCOME)

    if kind == "EXPENSE" and category_kind != "EXPENSE":
        raise BadRequestError(ErrorMessage.TX_CATEGORY_INCOMPATIBLE_EXPENSE)


def validate_new_transaction(
    *,
    kind: str,
    amount: Decimal,
    category_id: int | None,
    category_kind: str | None,
) -> None:
    """Validate invariants for creating an INCOME/EXPENSE transaction."""
    validate_transaction_payload(kind=kind, amount=amount, category_id=category_id)
    validate_category_compatibility(kind=kind, category_kind=category_kind)


def validate_new_transfer(
    *,
    amount_abs: Decimal,
    from_account_id: int,
    to_account_id: int,
) -> None:
    """Validate invariants for creating a transfer request (without DB access)."""
    if from_account_id == to_account_id:
        raise BadRequestError(ErrorMessage.TRANSFER_SAME_ACCOUNTS)

    if amount_abs <= 0:
        raise BadRequestError(ErrorMessage.TRANSFER_AMOUNT_ABS_GT_0)
