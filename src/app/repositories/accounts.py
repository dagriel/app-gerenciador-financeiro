"""Account repository.

Centraliza queries e operações de persistência para contas.

Objetivo arquitetural:
- Repositories falam com ORM/SQLAlchemy.
- Services trabalham com Domain Entities (pure Python), sem importar `app.db.models`.

SQLAlchemy style:
- Prefer SQLAlchemy 2.0 `select()` + `Session.scalars()`.
"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.models import Account as AccountModel
from app.domain.entities.account import Account as AccountEntity
from app.domain.error_messages import ErrorMessage
from app.domain.errors import ConflictError


def _to_domain(model: AccountModel) -> AccountEntity:
    return AccountEntity(
        id=model.id,
        name=model.name,
        type=model.type,
        active=model.active,
    )


def list_accounts(db: Session, *, include_inactive: bool) -> list[AccountEntity]:
    stmt = select(AccountModel)
    if not include_inactive:
        stmt = stmt.where(AccountModel.active.is_(True))
    stmt = stmt.order_by(AccountModel.id.asc())
    return [_to_domain(m) for m in db.scalars(stmt).all()]


def get_account(db: Session, account_id: int) -> AccountEntity | None:
    stmt = select(AccountModel).where(AccountModel.id == account_id)
    model = db.scalars(stmt).one_or_none()
    return _to_domain(model) if model else None


def get_account_by_name_type(db: Session, *, name: str, type_: str) -> AccountEntity | None:
    stmt = select(AccountModel).where(AccountModel.name == name).where(AccountModel.type == type_)
    model = db.scalars(stmt).one_or_none()
    return _to_domain(model) if model else None


def get_other_account_by_name_type(
    db: Session,
    *,
    account_id: int,
    name: str,
    type_: str,
) -> AccountEntity | None:
    stmt = (
        select(AccountModel)
        .where(AccountModel.id != account_id)
        .where(AccountModel.name == name)
        .where(AccountModel.type == type_)
    )
    model = db.scalars(stmt).one_or_none()
    return _to_domain(model) if model else None


def get_active_account(db: Session, account_id: int) -> AccountEntity | None:
    stmt = select(AccountModel).where(AccountModel.id == account_id, AccountModel.active.is_(True))
    model = db.scalars(stmt).one_or_none()
    return _to_domain(model) if model else None


def create_account(db: Session, *, name: str, type_: str) -> AccountEntity:
    model = AccountModel(name=name, type=type_)
    db.add(model)
    try:
        db.flush()  # populate PK without committing
    except IntegrityError as e:
        # Translate infrastructure exception to a domain error (keep services SQLAlchemy-free).
        raise ConflictError(ErrorMessage.ACCOUNT_ALREADY_EXISTS) from e
    return _to_domain(model)


def update_account(
    db: Session,
    *,
    account_id: int,
    name: str | None,
    type_: str | None,
    active: bool | None,
) -> AccountEntity | None:
    stmt = select(AccountModel).where(AccountModel.id == account_id)
    model = db.scalars(stmt).one_or_none()
    if not model:
        return None

    if name is not None:
        model.name = name
    if type_ is not None:
        model.type = type_
    if active is not None:
        model.active = active

    try:
        db.flush()
    except IntegrityError as e:
        raise ConflictError(ErrorMessage.ACCOUNT_ALREADY_EXISTS) from e
    return _to_domain(model)
