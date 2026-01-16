"""Account service (use-cases).

Application-layer orchestration for accounts.

Architecture goal:
- depend on ports (`uow.accounts`) instead of concrete repositories or SQLAlchemy.
"""

from __future__ import annotations

from app.core.error_messages import ErrorMessage
from app.core.exceptions import ConflictError, NotFoundError
from app.db.uow import UnitOfWork
from app.domain.entities.account import Account as AccountEntity


def list_accounts(uow: UnitOfWork, *, include_inactive: bool) -> list[AccountEntity]:
    return uow.accounts.list_accounts(include_inactive=include_inactive)


def create_account(uow: UnitOfWork, *, name: str, type_: str) -> AccountEntity:
    exists = uow.accounts.get_account_by_name_type(name=name, type_=type_)
    if exists:
        raise ConflictError(ErrorMessage.ACCOUNT_ALREADY_EXISTS)

    # Repository translates DB uniqueness violations to ConflictError (DomainError).
    return uow.accounts.create_account(name=name, type_=type_)


def update_account(
    uow: UnitOfWork,
    *,
    account_id: int,
    name: str | None,
    type_: str | None,
    active: bool | None,
) -> AccountEntity:
    acc = uow.accounts.get_account(account_id)
    if not acc:
        raise NotFoundError(ErrorMessage.ACCOUNT_NOT_FOUND)

    next_name = name if name is not None else acc.name
    next_type = type_ if type_ is not None else acc.type

    # Uniqueness rule: (name, type) must be unique.
    if (next_name != acc.name) or (next_type != acc.type):
        collision = uow.accounts.get_other_account_by_name_type(
            account_id=account_id,
            name=next_name,
            type_=next_type,
        )
        if collision:
            raise ConflictError(ErrorMessage.ACCOUNT_ALREADY_EXISTS)

    updated = uow.accounts.update_account(
        account_id=account_id,
        name=name,
        type_=type_,
        active=active,
    )

    if not updated:
        # Should be rare: account deleted between reads.
        raise NotFoundError(ErrorMessage.ACCOUNT_NOT_FOUND)

    return updated


def delete_account(uow: UnitOfWork, *, account_id: int) -> None:
    acc = uow.accounts.get_account(account_id)
    if not acc:
        raise NotFoundError(ErrorMessage.ACCOUNT_NOT_FOUND)

    uow.accounts.update_account(account_id=account_id, name=None, type_=None, active=False)
    return None
