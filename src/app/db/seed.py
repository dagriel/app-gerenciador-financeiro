"""Database seeds for the MVP.

This module provides an idempotent seeding routine (upsert-style) plus an optional
reset mode for deterministic demo/QA datasets.

Run (after applying migrations):
    python -m app.db.seed --reset --month 2026-01 --with-sample-transactions
"""

from __future__ import annotations

import argparse
import datetime as dt
from dataclasses import asdict, dataclass
from decimal import Decimal
from typing import Any

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.core.validators import parse_month_str
from app.db.models import Account, Budget, Category, Transaction
from app.db.uow import UnitOfWork
from app.services.transfers import create_transfer


@dataclass(frozen=True)
class SeedReport:
    month: str
    reset: bool
    with_sample_transactions: bool
    created_accounts: int
    updated_accounts: int
    created_categories: int
    updated_categories: int
    created_budgets: int
    updated_budgets: int
    created_transactions: int
    created_transfers: int
    skipped_transactions_reason: str | None = None


def _d(v: str | int | float | Decimal) -> Decimal:
    """Safely build Decimal from common literals (avoid float artifacts by using str())."""
    if isinstance(v, Decimal):
        return v
    if isinstance(v, int):
        return Decimal(v)
    if isinstance(v, float):
        # use repr to reduce float artifacts when tests pass floats
        return Decimal(str(v))
    return Decimal(v)


def _month_date(month: str, day: int) -> dt.date:
    parsed = parse_month_str(month)
    return dt.date(parsed.year, parsed.month, day)


def _reset_all(db: Session) -> None:
    """Hard reset all domain tables (safe for local single-user/dev seed).

    Order matters due to foreign keys.
    """
    db.execute(delete(Transaction))
    db.execute(delete(Budget))
    db.execute(delete(Category))
    db.execute(delete(Account))
    db.commit()


def _upsert_account(db: Session, *, name: str, type_: str) -> tuple[Account, bool]:
    """Upsert an Account using (name,type) as business key.

    Returns (account, created?).
    """
    existing = db.execute(
        select(Account).where(Account.name == name).where(Account.type == type_)
    ).scalar_one_or_none()

    if existing:
        changed = False
        if not existing.active:
            existing.active = True
            changed = True
        # Keep name/type aligned to the seed (defensive)
        if existing.name != name:
            existing.name = name
            changed = True
        if existing.type != type_:
            existing.type = type_
            changed = True
        if changed:
            db.add(existing)
        return existing, False

    acc = Account(name=name, type=type_, active=True)
    db.add(acc)
    db.flush()  # populate PK without committing yet
    return acc, True


def _upsert_category(
    db: Session, *, name: str, kind: str, group: str, active: bool = True
) -> tuple[Category, bool]:
    """Upsert Category using the DB unique key (name)."""
    existing = db.execute(select(Category).where(Category.name == name)).scalar_one_or_none()
    if existing:
        changed = False
        if existing.kind != kind:
            existing.kind = kind
            changed = True
        if existing.group != group:
            existing.group = group
            changed = True
        if existing.active != active:
            existing.active = active
            changed = True
        if changed:
            db.add(existing)
        return existing, False

    cat = Category(name=name, kind=kind, group=group, active=active)
    db.add(cat)
    db.flush()
    return cat, True


def _upsert_budget(
    db: Session, *, month: str, category_id: int, amount_planned: Decimal
) -> tuple[Budget, bool]:
    """Upsert Budget using (month, category_id)."""
    existing = db.execute(
        select(Budget)
        .where(Budget.month == month)
        .where(Budget.category_id == category_id)
    ).scalar_one_or_none()

    if existing:
        if existing.amount_planned != amount_planned:
            existing.amount_planned = amount_planned
            db.add(existing)
        return existing, False

    bud = Budget(month=month, category_id=category_id, amount_planned=amount_planned)
    db.add(bud)
    db.flush()
    return bud, True


def seed_all(
    db: Session,
    *,
    month: str,
    reset: bool = False,
    with_sample_transactions: bool = False,
) -> SeedReport:
    """Seed the database with a high-quality MVP dataset.

    This function is designed to be:
      - deterministic in reset mode
      - idempotent (no duplication) in upsert mode for accounts/categories/budgets
      - conservative for transactions in upsert mode (skips unless DB is empty)

    Args:
        db: SQLAlchemy session
        month: Month in YYYY-MM format
        reset: If True, delete all domain data before seeding
        with_sample_transactions: If True, also insert sample transactions and one transfer

    Returns:
        SeedReport with counts and any skip reasons
    """
    # Validate month with the same business rule used by the app
    parse_month_str(month)

    if reset:
        _reset_all(db)

    created_accounts = updated_accounts = 0
    created_categories = updated_categories = 0
    created_budgets = updated_budgets = 0
    created_transactions = 0
    created_transfers = 0
    skipped_reason: str | None = None

    # --- Accounts (minimum to cover transfers) ---
    accounts_seed = [
        {"name": "Carteira", "type": "CASH"},
        {"name": "Banco", "type": "BANK"},
    ]

    account_by_name_type: dict[tuple[str, str], Account] = {}
    for a in accounts_seed:
        acc, created = _upsert_account(db, name=a["name"], type_=a["type"])
        account_by_name_type[(a["name"], a["type"])] = acc
        if created:
            created_accounts += 1
        else:
            # We don't differentiate "no-op" vs "updated" perfectly without extra checks,
            # but we can treat any existing as potential update for reporting purposes.
            updated_accounts += 1

    # --- Categories (minimum to cover income/expense) ---
    categories_seed = [
        {"name": "Salário", "kind": "INCOME", "group": "ESSENTIAL"},
        {"name": "Freelance", "kind": "INCOME", "group": "OTHER"},
        {"name": "Alimentação", "kind": "EXPENSE", "group": "ESSENTIAL"},
        {"name": "Transporte", "kind": "EXPENSE", "group": "ESSENTIAL"},
        {"name": "Lazer", "kind": "EXPENSE", "group": "LIFESTYLE"},
        {"name": "Saúde", "kind": "EXPENSE", "group": "ESSENTIAL"},
        {"name": "Educação", "kind": "EXPENSE", "group": "FUTURE"},
    ]

    category_by_name: dict[str, Category] = {}
    for c in categories_seed:
        cat, created = _upsert_category(
            db,
            name=c["name"],
            kind=c["kind"],
            group=c["group"],
            active=True,
        )
        category_by_name[c["name"]] = cat
        if created:
            created_categories += 1
        else:
            updated_categories += 1

    # --- Budgets (expense only) ---
    budgets_seed = [
        {"category": "Alimentação", "amount_planned": _d("600.00")},
        {"category": "Transporte", "amount_planned": _d("300.00")},
        {"category": "Lazer", "amount_planned": _d("200.00")},
        {"category": "Saúde", "amount_planned": _d("150.00")},
    ]

    for b in budgets_seed:
        cat = category_by_name[b["category"]]
        if cat.kind != "EXPENSE":
            raise ValueError("Seed inválido: budget deve ser apenas para categoria EXPENSE.")
        bud, created = _upsert_budget(
            db,
            month=month,
            category_id=cat.id,
            amount_planned=b["amount_planned"],
        )
        if created:
            created_budgets += 1
        else:
            updated_budgets += 1
        _ = bud  # keep for debugging if needed

    db.commit()

    # --- Sample transactions / transfer ---
    if with_sample_transactions:
        # To prevent silent duplication in upsert mode, only seed transactions if DB is empty,
        # unless we're in reset mode (where duplication cannot happen).
        has_any_tx = db.execute(select(Transaction.id).limit(1)).first() is not None
        if has_any_tx and not reset:
            skipped_reason = (
                "DB já possui transações; pulando seed de transações para evitar duplicação."
            )
        else:
            banco = account_by_name_type[("Banco", "BANK")]
            carteira = account_by_name_type[("Carteira", "CASH")]

            tx_seed = [
                # incomes
                {
                    "date": _month_date(month, 5),
                    "description": "Salário (seed)",
                    "amount": _d("5000.00"),
                    "kind": "INCOME",
                    "account_id": banco.id,
                    "category_id": category_by_name["Salário"].id,
                },
                {
                    "date": _month_date(month, 12),
                    "description": "Freelance (seed)",
                    "amount": _d("800.00"),
                    "kind": "INCOME",
                    "account_id": banco.id,
                    "category_id": category_by_name["Freelance"].id,
                },
                # expenses
                {
                    "date": _month_date(month, 10),
                    "description": "Supermercado (seed)",
                    "amount": _d("-450.00"),
                    "kind": "EXPENSE",
                    "account_id": banco.id,
                    "category_id": category_by_name["Alimentação"].id,
                },
                {
                    "date": _month_date(month, 15),
                    "description": "Ônibus / combustível (seed)",
                    "amount": _d("-120.00"),
                    "kind": "EXPENSE",
                    "account_id": carteira.id,
                    "category_id": category_by_name["Transporte"].id,
                },
                {
                    "date": _month_date(month, 20),
                    "description": "Cinema (seed)",
                    "amount": _d("-90.00"),
                    "kind": "EXPENSE",
                    "account_id": banco.id,
                    "category_id": category_by_name["Lazer"].id,
                },
                # realized-only (no budget)
                {
                    "date": _month_date(month, 22),
                    "description": "Curso (seed)",
                    "amount": _d("-250.00"),
                    "kind": "EXPENSE",
                    "account_id": banco.id,
                    "category_id": category_by_name["Educação"].id,
                },
            ]

            for tx in tx_seed:
                # Domain sanity checks (same logic as router)
                if tx["kind"] == "INCOME" and tx["amount"] <= 0:
                    raise ValueError("Seed inválido: INCOME requer amount > 0.")
                if tx["kind"] == "EXPENSE" and tx["amount"] >= 0:
                    raise ValueError("Seed inválido: EXPENSE requer amount < 0.")

                db.add(
                    Transaction(
                        date=tx["date"],
                        description=tx["description"],
                        amount=tx["amount"],
                        kind=tx["kind"],
                        account_id=tx["account_id"],
                        category_id=tx["category_id"],
                    )
                )
                created_transactions += 1

            db.commit()

            # One transfer (does not affect reports, but validates pair behavior)
            uow = UnitOfWork(db)
            create_transfer(
                uow,
                date=_month_date(month, 8),
                description="Transferência Banco -> Carteira (seed)",
                amount_abs=_d("400.00"),
                from_account_id=banco.id,
                to_account_id=carteira.id,
            )
            db.commit()
            created_transfers += 1

    return SeedReport(
        month=month,
        reset=reset,
        with_sample_transactions=with_sample_transactions,
        created_accounts=created_accounts,
        updated_accounts=updated_accounts,
        created_categories=created_categories,
        updated_categories=updated_categories,
        created_budgets=created_budgets,
        updated_budgets=updated_budgets,
        created_transactions=created_transactions,
        created_transfers=created_transfers,
        skipped_transactions_reason=skipped_reason,
    )


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Seed do MVP APP-GERENCIADOR-FINANCEIRO (idempotente).")
    p.add_argument(
        "--month",
        required=True,
        help="Mês no formato YYYY-MM (ex.: 2026-01).",
    )
    p.add_argument(
        "--reset",
        action="store_true",
        help=(
            "Apaga dados (transactions/budgets/categories/accounts) e recria um dataset "
            "determinístico."
        ),
    )
    p.add_argument(
        "--with-sample-transactions",
        action="store_true",
        help="Inclui transações e 1 transferência de exemplo (útil para demo/QA/relatórios).",
    )
    return p


def main(argv: list[str] | None = None) -> dict[str, Any]:
    """CLI entry point. Returns the seed report as dict (useful for tests/scripts)."""
    from app.db.session import get_session

    args = _build_parser().parse_args(argv)
    with get_session() as db:
        report = seed_all(
            db,
            month=args.month,
            reset=args.reset,
            with_sample_transactions=args.with_sample_transactions,
        )
    data = asdict(report)
    # Basic human-friendly output
    print(data)
    return data


if __name__ == "__main__":  # pragma: no cover
    main()
