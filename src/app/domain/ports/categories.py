"""Category repository port."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from app.domain.entities.category import Category


@runtime_checkable
class CategoryRepository(Protocol):
    def list_categories(self, *, include_inactive: bool) -> list[Category]: ...

    def get_category(self, category_id: int) -> Category | None: ...

    def get_active_category(self, category_id: int) -> Category | None: ...

    def get_category_by_name(self, name: str) -> Category | None: ...

    def get_other_category_with_name(self, *, category_id: int, name: str) -> Category | None: ...

    def create_category(self, *, name: str, kind: str, group: str) -> Category: ...

    def update_category(
        self,
        *,
        category_id: int,
        name: str | None,
        kind: str | None,
        group: str | None,
        active: bool | None,
    ) -> Category | None: ...
