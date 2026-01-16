"""Category repository.

Centraliza queries e operações de persistência para categorias.

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

from app.db.models import Category as CategoryModel
from app.domain.entities.category import Category as CategoryEntity
from app.domain.error_messages import ErrorMessage
from app.domain.errors import ConflictError


def _to_domain(model: CategoryModel) -> CategoryEntity:
    return CategoryEntity(
        id=model.id,
        name=model.name,
        kind=model.kind,
        group=model.group,
        active=model.active,
    )


def list_categories(db: Session, *, include_inactive: bool) -> list[CategoryEntity]:
    stmt = select(CategoryModel)
    if not include_inactive:
        stmt = stmt.where(CategoryModel.active.is_(True))
    stmt = stmt.order_by(CategoryModel.id.asc())
    return [_to_domain(m) for m in db.scalars(stmt).all()]


def get_category(db: Session, category_id: int) -> CategoryEntity | None:
    stmt = select(CategoryModel).where(CategoryModel.id == category_id)
    model = db.scalars(stmt).one_or_none()
    return _to_domain(model) if model else None


def get_active_category(db: Session, category_id: int) -> CategoryEntity | None:
    stmt = select(CategoryModel).where(CategoryModel.id == category_id, CategoryModel.active.is_(True))
    model = db.scalars(stmt).one_or_none()
    return _to_domain(model) if model else None


def get_category_by_name(db: Session, name: str) -> CategoryEntity | None:
    stmt = select(CategoryModel).where(CategoryModel.name == name)
    model = db.scalars(stmt).one_or_none()
    return _to_domain(model) if model else None


def get_other_category_with_name(db: Session, *, category_id: int, name: str) -> CategoryEntity | None:
    """Find a different category (id != category_id) with the same name (for uniqueness checks)."""
    stmt = select(CategoryModel).where(CategoryModel.name == name, CategoryModel.id != category_id)
    model = db.scalars(stmt).one_or_none()
    return _to_domain(model) if model else None


def create_category(db: Session, *, name: str, kind: str, group: str) -> CategoryEntity:
    model = CategoryModel(name=name, kind=kind, group=group)
    db.add(model)
    try:
        db.flush()
    except IntegrityError as e:
        raise ConflictError(ErrorMessage.CATEGORY_ALREADY_EXISTS) from e
    return _to_domain(model)


def update_category(
    db: Session,
    *,
    category_id: int,
    name: str | None,
    kind: str | None,
    group: str | None,
    active: bool | None,
) -> CategoryEntity | None:
    stmt = select(CategoryModel).where(CategoryModel.id == category_id)
    model = db.scalars(stmt).one_or_none()
    if not model:
        return None

    if name is not None:
        model.name = name
    if kind is not None:
        model.kind = kind
    if group is not None:
        model.group = group
    if active is not None:
        model.active = active

    try:
        db.flush()
    except IntegrityError as e:
        raise ConflictError(ErrorMessage.CATEGORY_ALREADY_EXISTS) from e
    return _to_domain(model)
