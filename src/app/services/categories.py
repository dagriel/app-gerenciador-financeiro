"""Category service (use-cases).

Application-layer orchestration for categories.

Architecture goal:
- depend on ports (`uow.categories`) instead of concrete repositories or SQLAlchemy.
"""

from __future__ import annotations

from app.core.error_messages import ErrorMessage
from app.core.exceptions import ConflictError, NotFoundError
from app.db.uow import UnitOfWork
from app.domain.entities.category import Category as CategoryEntity


def list_categories(uow: UnitOfWork, *, include_inactive: bool) -> list[CategoryEntity]:
    return uow.categories.list_categories(include_inactive=include_inactive)


def create_category(uow: UnitOfWork, *, name: str, kind: str, group: str) -> CategoryEntity:
    exists = uow.categories.get_category_by_name(name)
    if exists:
        raise ConflictError(ErrorMessage.CATEGORY_ALREADY_EXISTS)

    # Repository translates DB uniqueness violations to ConflictError (DomainError).
    return uow.categories.create_category(name=name, kind=kind, group=group)


def update_category(
    uow: UnitOfWork,
    *,
    category_id: int,
    name: str | None,
    kind: str | None,
    group: str | None,
    active: bool | None,
) -> CategoryEntity:
    cat = uow.categories.get_category(category_id)
    if not cat:
        raise NotFoundError(ErrorMessage.CATEGORY_NOT_FOUND)

    if name is not None:
        exists = uow.categories.get_other_category_with_name(category_id=category_id, name=name)
        if exists:
            raise ConflictError(ErrorMessage.CATEGORY_ALREADY_EXISTS)

    updated = uow.categories.update_category(
        category_id=category_id,
        name=name,
        kind=kind,
        group=group,
        active=active,
    )

    if not updated:
        raise NotFoundError(ErrorMessage.CATEGORY_NOT_FOUND)

    return updated


def delete_category(uow: UnitOfWork, *, category_id: int) -> None:
    cat = uow.categories.get_category(category_id)
    if not cat:
        raise NotFoundError(ErrorMessage.CATEGORY_NOT_FOUND)

    uow.categories.update_category(
        category_id=category_id,
        name=None,
        kind=None,
        group=None,
        active=False,
    )
    return None
