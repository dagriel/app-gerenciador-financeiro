"""Unit of Work (transaction boundary) for request-scoped database operations.

This UoW is the application's transaction boundary and DI carrier.

Architecture goals:
- Services/use-cases should not import SQLAlchemy nor deal with `Session` directly.
- Services should depend on domain ports (Protocols), and UoW provides concrete adapters.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from sqlalchemy.orm import Session

from app.domain.ports.accounts import AccountRepository
from app.domain.ports.budgets import BudgetRepository
from app.domain.ports.categories import CategoryRepository
from app.domain.ports.reports import ReportRepository
from app.domain.ports.transactions import TransactionRepository
from app.repositories.adapters import (
    SqlAlchemyAccountRepository,
    SqlAlchemyBudgetRepository,
    SqlAlchemyCategoryRepository,
    SqlAlchemyReportRepository,
    SqlAlchemyTransactionRepository,
)


@dataclass
class UnitOfWork:
    """A minimal Unit of Work wrapper around a SQLAlchemy Session.

    Notes:
        - API boundary controls commit/rollback (see api/deps.get_uow).
        - Use `flush()` when you need PKs before the final commit.
        - Services should prefer `uow.accounts/uow.categories/...` over `uow.session`.
    """

    session: Session

    # Repository adapters (ports)
    accounts: AccountRepository = field(init=False)
    categories: CategoryRepository = field(init=False)
    budgets: BudgetRepository = field(init=False)
    transactions: TransactionRepository = field(init=False)
    reports: ReportRepository = field(init=False)

    def __post_init__(self) -> None:
        self.accounts = SqlAlchemyAccountRepository(self.session)
        self.categories = SqlAlchemyCategoryRepository(self.session)
        self.budgets = SqlAlchemyBudgetRepository(self.session)
        self.transactions = SqlAlchemyTransactionRepository(self.session)
        self.reports = SqlAlchemyReportRepository(self.session)

    def flush(self) -> None:
        self.session.flush()

    def commit(self) -> None:
        self.session.commit()

    def rollback(self) -> None:
        self.session.rollback()
