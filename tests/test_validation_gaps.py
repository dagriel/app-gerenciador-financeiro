"""Regression tests for previously identified MVP gaps.

These tests focus on returning proper client errors (4xx) instead of 500s and
keeping behavior consistent with domain rules.
"""


def test_reports_invalid_month_returns_400(client, headers):
    r = client.get("/reports/monthly-summary?month=2026-13", headers=headers)
    assert r.status_code == 400


def test_budgets_list_invalid_month_returns_400(client, headers):
    r = client.get("/budgets?month=2026-13", headers=headers)
    assert r.status_code == 400


def test_budgets_upsert_invalid_month_returns_422(client, headers):
    # Month format matches regex but month number is invalid -> schema validator should fail.
    r = client.post(
        "/budgets",
        json={"month": "2026-13", "category_id": 1, "amount_planned": 10.0},
        headers=headers,
    )
    assert r.status_code == 422


def test_update_category_name_conflict_returns_409(client, headers):
    c1 = client.post(
        "/categories",
        json={"name": "Alimentação", "kind": "EXPENSE", "group": "ESSENTIAL"},
        headers=headers,
    ).json()
    c2 = client.post(
        "/categories",
        json={"name": "Transporte", "kind": "EXPENSE", "group": "ESSENTIAL"},
        headers=headers,
    ).json()

    r = client.put(f"/categories/{c2['id']}", json={"name": c1["name"]}, headers=headers)
    assert r.status_code == 409


def test_transfer_with_nonexistent_account_returns_400(client, headers):
    # Create only one account, use a non-existent other account id
    a1 = client.post(
        "/accounts", json={"name": "Carteira", "type": "CASH"}, headers=headers
    ).json()["id"]

    r = client.post(
        "/transactions/transfer",
        json={
            "date": "2026-01-01",
            "description": "Invalid",
            "amount_abs": 10.0,
            "from_account_id": a1,
            "to_account_id": 999999,
        },
        headers=headers,
    )
    assert r.status_code == 400


def test_transfer_with_inactive_account_returns_400(client, headers):
    a1 = client.post(
        "/accounts", json={"name": "Carteira", "type": "CASH"}, headers=headers
    ).json()["id"]
    a2 = client.post("/accounts", json={"name": "Banco", "type": "BANK"}, headers=headers).json()[
        "id"
    ]

    # Soft delete destination account
    r = client.delete(f"/accounts/{a2}", headers=headers)
    assert r.status_code == 204

    r = client.post(
        "/transactions/transfer",
        json={
            "date": "2026-01-01",
            "description": "Invalid",
            "amount_abs": 10.0,
            "from_account_id": a1,
            "to_account_id": a2,
        },
        headers=headers,
    )
    assert r.status_code == 400


def test_missing_api_key_returns_401(client):
    r = client.get("/accounts")
    assert r.status_code == 401
