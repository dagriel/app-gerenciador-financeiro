"""Transfer service - handles transfer transactions."""

from __future__ import annotations

import datetime as dt
from decimal import Decimal

from app.core.error_messages import ErrorMessage
from app.core.exceptions import BadRequestError
from app.db.uow import UnitOfWork
from app.domain.ids import new_transfer_pair_id
from app.domain.rules.transactions import validate_new_transfer


def create_transfer(
    uow: UnitOfWork,
    *,
    date: dt.date,
    description: str,
    amount_abs: Decimal,
    from_account_id: int,
    to_account_id: int,
) -> dict:
    """Create a transfer (2 linked transactions).

    Notes:
        This service DOES NOT commit. The caller (API UnitOfWork or script) controls the
        transaction boundary.

    Raises:
        BadRequestError: For invalid business rules (same account, inactive accounts, etc.)
    """
    # Domain-level invariants (no DB required).
    validate_new_transfer(
        amount_abs=amount_abs, from_account_id=from_account_id, to_account_id=to_account_id
    )

    # Validate accounts exist and are active (keep behavior consistent with /transactions).
    if not uow.accounts.get_active_account(from_account_id):
        raise BadRequestError(ErrorMessage.TRANSFER_FROM_ACCOUNT_INVALID)

    if not uow.accounts.get_active_account(to_account_id):
        raise BadRequestError(ErrorMessage.TRANSFER_TO_ACCOUNT_INVALID)

    pair = new_transfer_pair_id()

    out_tx, in_tx = uow.transactions.create_transfer_pair(
        date=date,
        description=description,
        amount_abs=amount_abs,
        from_account_id=from_account_id,
        to_account_id=to_account_id,
        pair_id=pair,
    )

    return {"pair_id": pair, "out_id": out_tx.id, "in_id": in_tx.id}
