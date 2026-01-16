"""Ports (interfaces) for the domain/application layers.

These protocols allow the application layer (services/use-cases) to depend on
abstractions rather than concrete infrastructure (e.g., SQLAlchemy repositories).

Why here?
- They live in the domain package so they can be imported without pulling
  infrastructure dependencies.
- Infrastructure implements these ports (adapters).
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from app.domain.entities.account import Account


@runtime_checkable
class AccountRepository(Protocol):
    def list_accounts(self, *, include_inactive: bool) -> list[Account]: ...

    def get_account(self, account_id: int) -> Account | None: ...

    def get_account_by_name_type(self, *, name: str, type_: str) -> Account | None: ...

    def get_other_account_by_name_type(
        self,
        *,
        account_id: int,
        name: str,
        type_: str,
    ) -> Account | None: ...

    def get_active_account(self, account_id: int) -> Account | None: ...

    def create_account(self, *, name: str, type_: str) -> Account: ...

    def update_account(
        self,
        *,
        account_id: int,
        name: str | None,
        type_: str | None,
        active: bool | None,
    ) -> Account | None: ...
