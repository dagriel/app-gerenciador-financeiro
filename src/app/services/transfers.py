"""Transfer service - handles transfer transactions."""

import datetime as dt
from decimal import Decimal

from sqlalchemy.orm import Session

from app.core.error_messages import ErrorMessage
from app.db.models import Account, Transaction, new_pair_id


def create_transfer(
    db: Session,
    *,
    date: dt.date,
    description: str,
    amount_abs: Decimal,
    from_account_id: int,
    to_account_id: int,
) -> dict:
    """Create a transfer (2 linked transactions).

    Args:
        db: Database session
        date: Transfer date
        description: Transfer description
        amount_abs: Absolute amount (must be > 0)
        from_account_id: Source account ID
        to_account_id: Destination account ID

    Returns:
        Dict with pair_id, out_id, and in_id

    Raises:
        ValueError: If accounts are the same or amount_abs <= 0
    """
    if from_account_id == to_account_id:
        raise ValueError(ErrorMessage.TRANSFER_SAME_ACCOUNTS)
    if amount_abs <= 0:
        raise ValueError(ErrorMessage.TRANSFER_AMOUNT_ABS_GT_0)

    # Validate accounts exist and are active (keep behavior consistent with /transactions).
    from_acc = (
        db.query(Account)
        .filter(Account.id == from_account_id, Account.active.is_(True))
        .one_or_none()
    )
    if not from_acc:
        raise ValueError(ErrorMessage.TRANSFER_FROM_ACCOUNT_INVALID)

    to_acc = (
        db.query(Account)
        .filter(Account.id == to_account_id, Account.active.is_(True))
        .one_or_none()
    )
    if not to_acc:
        raise ValueError(ErrorMessage.TRANSFER_TO_ACCOUNT_INVALID)

    pair = new_pair_id()

    out_tx = Transaction(
        date=date,
        description=description,
        amount=-amount_abs,
        kind="TRANSFER",
        account_id=from_account_id,
        category_id=None,
        transfer_pair_id=pair,
    )
    in_tx = Transaction(
        date=date,
        description=description,
        amount=amount_abs,
        kind="TRANSFER",
        account_id=to_account_id,
        category_id=None,
        transfer_pair_id=pair,
    )

    db.add_all([out_tx, in_tx])
    db.commit()
    db.refresh(out_tx)
    db.refresh(in_tx)

    return {"pair_id": pair, "out_id": out_tx.id, "in_id": in_tx.id}
