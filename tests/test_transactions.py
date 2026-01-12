"""Tests for transactions endpoints."""


def test_create_income(client, headers):
    """Test creating an income transaction."""
    # Setup: create account and category
    acc = client.post("/accounts", json={"name": "Banco", "type": "BANK"}, headers=headers).json()
    cat = client.post(
        "/categories",
        json={"name": "Salário", "kind": "INCOME", "group": "ESSENTIAL"},
        headers=headers,
    ).json()

    # Create income
    r = client.post(
        "/transactions",
        json={
            "date": "2026-01-15",
            "description": "Salário Janeiro",
            "amount": 5000.0,
            "kind": "INCOME",
            "account_id": acc["id"],
            "category_id": cat["id"],
        },
        headers=headers,
    )
    assert r.status_code == 201
    assert r.json()["amount"] == 5000.0
    assert r.json()["kind"] == "INCOME"


def test_create_expense(client, headers):
    """Test creating an expense transaction."""
    # Setup
    acc = client.post(
        "/accounts", json={"name": "Carteira", "type": "CASH"}, headers=headers
    ).json()
    cat = client.post(
        "/categories",
        json={"name": "Alimentação", "kind": "EXPENSE", "group": "ESSENTIAL"},
        headers=headers,
    ).json()

    # Create expense
    r = client.post(
        "/transactions",
        json={
            "date": "2026-01-16",
            "description": "Supermercado",
            "amount": -150.50,
            "kind": "EXPENSE",
            "account_id": acc["id"],
            "category_id": cat["id"],
        },
        headers=headers,
    )
    assert r.status_code == 201
    assert r.json()["amount"] == -150.50
    assert r.json()["kind"] == "EXPENSE"


def test_income_requires_positive_amount(client, headers):
    """Test that INCOME requires positive amount."""
    acc = client.post("/accounts", json={"name": "Banco", "type": "BANK"}, headers=headers).json()
    cat = client.post(
        "/categories",
        json={"name": "Salário", "kind": "INCOME", "group": "ESSENTIAL"},
        headers=headers,
    ).json()

    r = client.post(
        "/transactions",
        json={
            "date": "2026-01-15",
            "description": "Test",
            "amount": -100.0,
            "kind": "INCOME",
            "account_id": acc["id"],
            "category_id": cat["id"],
        },
        headers=headers,
    )
    assert r.status_code == 400


def test_expense_requires_negative_amount(client, headers):
    """Test that EXPENSE requires negative amount."""
    acc = client.post("/accounts", json={"name": "Banco", "type": "BANK"}, headers=headers).json()
    cat = client.post(
        "/categories",
        json={"name": "Alimentação", "kind": "EXPENSE", "group": "ESSENTIAL"},
        headers=headers,
    ).json()

    r = client.post(
        "/transactions",
        json={
            "date": "2026-01-15",
            "description": "Test",
            "amount": 100.0,
            "kind": "EXPENSE",
            "account_id": acc["id"],
            "category_id": cat["id"],
        },
        headers=headers,
    )
    assert r.status_code == 400


def test_list_transactions_with_date_filter(client, headers):
    """Test listing transactions with date filter."""
    acc = client.post("/accounts", json={"name": "Banco", "type": "BANK"}, headers=headers).json()
    cat = client.post(
        "/categories",
        json={"name": "Salário", "kind": "INCOME", "group": "ESSENTIAL"},
        headers=headers,
    ).json()

    # Create transactions in different dates
    client.post(
        "/transactions",
        json={
            "date": "2026-01-10",
            "amount": 1000.0,
            "kind": "INCOME",
            "account_id": acc["id"],
            "category_id": cat["id"],
        },
        headers=headers,
    )
    client.post(
        "/transactions",
        json={
            "date": "2026-02-10",
            "amount": 2000.0,
            "kind": "INCOME",
            "account_id": acc["id"],
            "category_id": cat["id"],
        },
        headers=headers,
    )

    # Filter by January
    r = client.get("/transactions?from_date=2026-01-01&to_date=2026-01-31", headers=headers)
    assert r.status_code == 200
    assert len(r.json()) == 1
    assert r.json()[0]["amount"] == 1000.0
