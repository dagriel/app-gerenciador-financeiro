"""Tests for budgets and reports endpoints."""


def test_budget_upsert(client, headers):
    """Test creating and updating budgets."""
    # Setup category
    cat = client.post(
        "/categories",
        json={"name": "Alimentação", "kind": "EXPENSE", "group": "ESSENTIAL"},
        headers=headers,
    ).json()

    # Create budget
    r = client.post(
        "/budgets",
        json={"month": "2026-01", "category_id": cat["id"], "amount_planned": 500.0},
        headers=headers,
    )
    assert r.status_code == 201
    assert r.json()["amount_planned"] == "500.00"

    # Update (upsert)
    r = client.post(
        "/budgets",
        json={"month": "2026-01", "category_id": cat["id"], "amount_planned": 600.0},
        headers=headers,
    )
    assert r.status_code == 201
    assert r.json()["amount_planned"] == "600.00"

    # List budgets for month
    r = client.get("/budgets?month=2026-01", headers=headers)
    assert r.status_code == 200
    assert len(r.json()) == 1


def test_budget_expense_only(client, headers):
    """Test that budgets only work for expense categories."""
    cat = client.post(
        "/categories",
        json={"name": "Salário", "kind": "INCOME", "group": "ESSENTIAL"},
        headers=headers,
    ).json()

    r = client.post(
        "/budgets",
        json={"month": "2026-01", "category_id": cat["id"], "amount_planned": 5000.0},
        headers=headers,
    )
    assert r.status_code == 400


def test_monthly_summary_report(client, headers):
    """Test monthly summary report with income, expense, and budget."""
    # Setup
    acc = client.post("/accounts", json={"name": "Banco", "type": "BANK"}, headers=headers).json()
    cat_income = client.post(
        "/categories",
        json={"name": "Salário", "kind": "INCOME", "group": "ESSENTIAL"},
        headers=headers,
    ).json()
    cat_expense = client.post(
        "/categories",
        json={"name": "Alimentação", "kind": "EXPENSE", "group": "ESSENTIAL"},
        headers=headers,
    ).json()

    # Create budget
    client.post(
        "/budgets",
        json={
            "month": "2026-01",
            "category_id": cat_expense["id"],
            "amount_planned": 500.0,
        },
        headers=headers,
    )

    # Create transactions
    client.post(
        "/transactions",
        json={
            "date": "2026-01-05",
            "amount": 3000.0,
            "kind": "INCOME",
            "account_id": acc["id"],
            "category_id": cat_income["id"],
        },
        headers=headers,
    )
    client.post(
        "/transactions",
        json={
            "date": "2026-01-10",
            "amount": -450.0,
            "kind": "EXPENSE",
            "account_id": acc["id"],
            "category_id": cat_expense["id"],
        },
        headers=headers,
    )

    # Get report
    r = client.get("/reports/monthly-summary?month=2026-01", headers=headers)
    assert r.status_code == 200
    data = r.json()

    assert data["month"] == "2026-01"
    assert data["income_total"] == "3000.00"
    assert data["expense_total"] == "450.00"
    assert data["balance"] == "2550.00"

    # Check category breakdown
    cat_data = next(c for c in data["by_category"] if c["category_id"] == cat_expense["id"])
    assert cat_data["planned"] == "500.00"
    assert cat_data["realized"] == "450.00"
    assert cat_data["deviation"] == "-50.00"  # spent less than planned


def test_monthly_summary_empty_month(client, headers):
    """Test monthly summary for month with no transactions."""
    r = client.get("/reports/monthly-summary?month=2026-12", headers=headers)
    assert r.status_code == 200
    data = r.json()

    assert data["income_total"] == "0.00"
    assert data["expense_total"] == "0.00"
    assert data["balance"] == "0.00"
    assert len(data["by_category"]) == 0
