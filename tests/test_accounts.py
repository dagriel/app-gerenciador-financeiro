"""Tests for accounts endpoints."""


def test_accounts_crud(client, headers):
    """Test complete CRUD flow for accounts."""
    # Create
    r = client.post("/accounts", json={"name": "Banco", "type": "BANK"}, headers=headers)
    assert r.status_code == 201
    acc_id = r.json()["id"]
    assert r.json()["name"] == "Banco"

    # List
    r = client.get("/accounts", headers=headers)
    assert r.status_code == 200
    assert any(a["id"] == acc_id for a in r.json())

    # Update
    r = client.put(f"/accounts/{acc_id}", json={"name": "Banco Atualizado"}, headers=headers)
    assert r.status_code == 200
    assert r.json()["name"] == "Banco Atualizado"

    # Delete (soft delete)
    r = client.delete(f"/accounts/{acc_id}", headers=headers)
    assert r.status_code == 204

    # Default list should exclude inactive
    r = client.get("/accounts", headers=headers)
    assert r.status_code == 200
    assert all(a["id"] != acc_id for a in r.json())

    # include_inactive should include it
    r = client.get("/accounts?include_inactive=true", headers=headers)
    assert r.status_code == 200
    assert any(a["id"] == acc_id for a in r.json())


def test_accounts_unique_name_type_conflict(client, headers):
    """Creating/updating an account with the same (name,type) must return 409."""
    # Create the first account
    r = client.post("/accounts", json={"name": "Banco", "type": "BANK"}, headers=headers)
    assert r.status_code == 201
    acc1_id = r.json()["id"]

    # Creating the same (name,type) again must conflict
    r = client.post("/accounts", json={"name": "Banco", "type": "BANK"}, headers=headers)
    assert r.status_code == 409
    assert r.json()["code"] == "ACCOUNT_ALREADY_EXISTS"

    # Create a second different account
    r = client.post("/accounts", json={"name": "Carteira", "type": "CASH"}, headers=headers)
    assert r.status_code == 201
    acc2_id = r.json()["id"]
    assert acc2_id != acc1_id

    # Updating account2 to collide with account1 must conflict
    r = client.put(
        f"/accounts/{acc2_id}",
        json={"name": "Banco", "type": "BANK"},
        headers=headers,
    )
    assert r.status_code == 409
    assert r.json()["code"] == "ACCOUNT_ALREADY_EXISTS"


def test_account_requires_api_key(client):
    """Test that accounts endpoint requires API key."""
    r = client.get("/accounts")
    assert r.status_code == 401
