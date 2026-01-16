"""Repository adapters (SQLAlchemy implementations of domain ports).

This module provides small OO wrappers around the existing function-based repositories.
The goal is to let the application layer depend on *ports* (Protocols) instead of on
SQLAlchemy or concrete persistence details.

Design notes:
- Services/use-cases should not import SQLAlchemy nor repository functions directly.
- `UnitOfWork` exposes these adapters as `uow.accounts`, `uow.categories`, etc.
"""

from __future__ import annotations

import datetime as dt
from decimal import Decimal

from sqlalchemy.orm import Session

from app.domain.entities.account import Account
from app.domain.entities.budget import Budget
from app.domain.entities.category import Category
from app.domain.entities.transaction import Transaction
from app.domain.ports.accounts import AccountRepository
from app.domain.ports.budgets import BudgetRepository
from app.domain.ports.categories import CategoryRepository
from app.domain.ports.reports import ReportRepository
from app.domain.ports.transactions import TransactionRepository
from app.repositories import accounts as accounts_repo
from app.repositories import budgets as budgets_repo
from app.repositories import categories as categories_repo
from app.repositories import reports as reports_repo
from app.repositories import transactions as transactions_repo


class SqlAlchemyAccountRepository(AccountRepository):
    def __init__(self, db: Session) -> None:
        self._db = db

    def list_accounts(self, *, include_inactive: bool) -> list[Account]:
        return accounts_repo.list_accounts(self._db, include_inactive=include_inactive)

    def get_account(self, account_id: int) -> Account | None:
        return accounts_repo.get_account(self._db, account_id)

    def get_account_by_name_type(self, *, name: str, type_: str) -> Account | None:
        return accounts_repo.get_account_by_name_type(self._db, name=name, type_=type_)

    def get_other_account_by_name_type(
        self,
        *,
        account_id: int,
        name: str,
        type_: str,
    ) -> Account | None:
        return accounts_repo.get_other_account_by_name_type(
            self._db,
            account_id=account_id,
            name=name,
            type_=type_,
        )

    def get_active_account(self, account_id: int) -> Account | None:
        return accounts_repo.get_active_account(self._db, account_id)

    def create_account(self, *, name: str, type_: str) -> Account:
        return accounts_repo.create_account(self._db, name=name, type_=type_)

    def update_account(
        self,
        *,
        account_id: int,
        name: str | None,
        type_: str | None,
        active: bool | None,
    ) -> Account | None:
        return accounts_repo.update_account(
            self._db,
            account_id=account_id,
            name=name,
            type_=type_,
            active=active,
        )


class SqlAlchemyCategoryRepository(CategoryRepository):
    def __init__(self, db: Session) -> None:
        self._db = db

    def list_categories(self, *, include_inactive: bool) -> list[Category]:
        return categories_repo.list_categories(self._db, include_inactive=include_inactive)

    def get_category(self, category_id: int) -> Category | None:
        return categories_repo.get_category(self._db, category_id)

    def get_active_category(self, category_id: int) -> Category | None:
        return categories_repo.get_active_category(self._db, category_id)

    def get_category_by_name(self, name: str) -> Category | None:
        return categories_repo.get_category_by_name(self._db, name)

    def get_other_category_with_name(self, *, category_id: int, name: str) -> Category | None:
        return categories_repo.get_other_category_with_name(self._db, category_id=category_id, name=name)

    def create_category(self, *, name: str, kind: str, group: str) -> Category:
        return categories_repo.create_category(self._db, name=name, kind=kind, group=group)

    def update_category(
        self,
        *,
        category_id: int,
        name: str | None,
        kind: str | None,
        group: str | None,
        active: bool | None,
    ) -> Category | None:
        return categories_repo.update_category(
            self._db,
            category_id=category_id,
            name=name,
            kind=kind,
            group=group,
            active=active,
        )


class SqlAlchemyBudgetRepository(BudgetRepository):
    def __init__(self, db: Session) -> None:
        self._db = db

    def list_budgets_by_month(self, *, month: str) -> list[Budget]:
        return budgets_repo.list_budgets_by_month(self._db, month=month)

    def get_budget(self, budget_id: int) -> Budget | None:
        return budgets_repo.get_budget(self._db, budget_id)

    def get_budget_by_month_category(self, *, month: str, category_id: int) -> Budget | None:
        return budgets_repo.get_budget_by_month_category(self._db, month=month, category_id=category_id)

    def upsert_budget(self, *, month: str, category_id: int, amount_planned: Decimal) -> Budget:
        return budgets_repo.upsert_budget(
            self._db,
            month=month,
            category_id=category_id,
            amount_planned=amount_planned,
        )

    def delete_budget(self, *, budget_id: int) -> bool:
        return budgets_repo.delete_budget(self._db, budget_id=budget_id)


class SqlAlchemyTransactionRepository(TransactionRepository):
    def __init__(self, db: Session) -> None:
        self._db = db

    def get_transaction(self, transaction_id: int) -> Transaction | None:
        return transactions_repo.get_transaction(self._db, transaction_id)

    def list_transactions(
        self,
        *,
        from_date: dt.date | None,
        to_date: dt.date | None,
        account_id: int | None,
        category_id: int | None,
        kind: str | None,
    ) -> list[Transaction]:
        return transactions_repo.list_transactions(
            self._db,
            from_date=from_date,
            to_date=to_date,
            account_id=account_id,
            category_id=category_id,
            kind=kind,
        )

    def create_transaction(
        self,
        *,
        date: dt.date,
        description: str,
        amount: Decimal,
        kind: str,
        account_id: int,
        category_id: int | None,
        transfer_pair_id: str | None = None,
    ) -> Transaction:
        return transactions_repo.create_transaction(
            self._db,
            date=date,
            description=description,
            amount=amount,
            kind=kind,
            account_id=account_id,
            category_id=category_id,
            transfer_pair_id=transfer_pair_id,
        )

    def create_transfer_pair(
        self,
        *,
        date: dt.date,
        description: str,
        amount_abs: Decimal,
        from_account_id: int,
        to_account_id: int,
        pair_id: str,
    ) -> tuple[Transaction, Transaction]:
        return transactions_repo.create_transfer_pair(
            self._db,
            date=date,
            description=description,
            amount_abs=amount_abs,
            from_account_id=from_account_id,
            to_account_id=to_account_id,
            pair_id=pair_id,
        )

    def delete_transaction_by_id(self, *, transaction_id: int) -> bool:
        return transactions_repo.delete_transaction_by_id(self._db, transaction_id=transaction_id)

    def delete_transfer_pair(self, *, transfer_pair_id: str) -> int:
        return transactions_repo.delete_transfer_pair(self._db, transfer_pair_id=transfer_pair_id)


class SqlAlchemyReportRepository(ReportRepository):
    def __init__(self, db: Session) -> None:
        self._db = db

    def sum_income(self, *, start: dt.date, end: dt.date) -> Decimal:
        return reports_repo.sum_income(self._db, start=start, end=end)

    def sum_expense(self, *, start: dt.date, end: dt.date) -> Decimal:
        return reports_repo.sum_expense(self._db, start=start, end=end)

    def list_budgets_for_month(self, *, month: str) -> list[tuple[int, Decimal]]:
        return reports_repo.list_budgets_for_month(self._db, month=month)

    def sum_expenses_by_category(self, *, start: dt.date, end: dt.date) -> list[tuple[int, Decimal]]:
        return reports_repo.sum_expenses_by_category(self._db, start=start, end=end)

    def get_category_names(self, *, category_ids: list[int]) -> dict[int, str]:
        return reports_repo.get_category_names(self._db, category_ids=category_ids)
