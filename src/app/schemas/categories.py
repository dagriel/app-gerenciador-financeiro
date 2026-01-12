"""Category schemas."""

from enum import StrEnum

from pydantic import BaseModel, ConfigDict


class CategoryKind(StrEnum):
    """Category kind enum."""

    INCOME = "INCOME"
    EXPENSE = "EXPENSE"


class CategoryGroup(StrEnum):
    """Category group enum."""

    ESSENTIAL = "ESSENTIAL"
    LIFESTYLE = "LIFESTYLE"
    FUTURE = "FUTURE"
    OTHER = "OTHER"


class CategoryCreate(BaseModel):
    """Schema for creating a category."""

    name: str
    kind: CategoryKind
    group: CategoryGroup


class CategoryUpdate(BaseModel):
    """Schema for updating a category."""

    name: str | None = None
    kind: CategoryKind | None = None
    group: CategoryGroup | None = None
    active: bool | None = None


class CategoryOut(BaseModel):
    """Schema for category response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    kind: CategoryKind
    group: CategoryGroup
    active: bool
