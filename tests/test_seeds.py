"""Tests for MVP seeds (idempotency + report validation)."""

from __future__ import annotations

from sqlalchemy import func, select

from app.db.models import Account, Budget, Category, Transaction
from app.db.seed import seed_all
from app.db.session import get_session


def _count(db, model) -> int:  # noqa: ANN001
    return int(db.execute(select(func.count()).select_from(model)).scalar_one())


def test_seed_upsert_idempotent_for_core_tables(client):  # noqa: ARG001
    # Ensure a clean deterministic dataset
    with get_session() as db:
        seed_all(db, month="2026-01", reset=True, with_sample_transactions=False)

    with get_session() as db:
        assert _count(db, Account) == 2
        assert _count(db, Category) == 7
        assert _count(db, Budget) == 4
        assert _count(db, Transaction) == 0

    # Run again in upsert mode and ensure no duplication
    with get_session() as db:
        seed_all(db, month="2026-01", reset=False, with_sample_transactions=False)

    with get_session() as db:
        assert _count(db, Account) == 2
        assert _count(db, Category) == 7
        assert _count(db, Budget) == 4
        assert _count(db, Transaction) == 0


def test_seed_with_transactions_produces_consistent_monthly_report(client, headers):
    # Seed with sample transactions and a transfer
    with get_session() as db:
        seed_all(db, month="2026-01", reset=True, with_sample_transactions=True)

    # Totals must match the seed dataset (TRANSFERS do not affect report)
    r = client.get("/reports/monthly-summary?month=2026-01", headers=headers)
    assert r.status_code == 200
    data = r.json()

    assert data["income_total"] == "5800.00"  # 5000 + 800
    assert data["expense_total"] == "910.00"  # 450 + 120 + 90 + 250
    assert data["balance"] == "4890.00"  # 5800 - 910

    by_cat = {c["category_name"]: c for c in data["by_category"]}

    # planned & realized categories
    assert by_cat["Alimentação"]["planned"] == "600.00"
    assert by_cat["Alimentação"]["realized"] == "450.00"
    assert by_cat["Alimentação"]["deviation"] == "-150.00"

    assert by_cat["Transporte"]["planned"] == "300.00"
    assert by_cat["Transporte"]["realized"] == "120.00"
    assert by_cat["Transporte"]["deviation"] == "-180.00"

    assert by_cat["Lazer"]["planned"] == "200.00"
    assert by_cat["Lazer"]["realized"] == "90.00"
    assert by_cat["Lazer"]["deviation"] == "-110.00"

    # planned-only category must appear (planned map union realized map)
    assert by_cat["Saúde"]["planned"] == "150.00"
    assert by_cat["Saúde"]["realized"] == "0.00"
    assert by_cat["Saúde"]["deviation"] == "-150.00"

    # realized-only category (no budget) must appear with planned=0
    assert by_cat["Educação"]["planned"] == "0.00"
    assert by_cat["Educação"]["realized"] == "250.00"
    assert by_cat["Educação"]["deviation"] == "250.00"


def test_seed_upsert_skips_transactions_if_db_already_has_any(client):  # noqa: ARG001
    with get_session() as db:
        seed_all(db, month="2026-01", reset=True, with_sample_transactions=True)

    with get_session() as db:
        tx_count_before = _count(db, Transaction)

    # Upsert again with transactions: should skip to avoid duplication
    with get_session() as db:
        report = seed_all(db, month="2026-01", reset=False, with_sample_transactions=True)
        assert report.skipped_transactions_reason is not None

    with get_session() as db:
        assert _count(db, Transaction) == tx_count_before
