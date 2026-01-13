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


def test_account_requires_api_key(client):
    """Test that accounts endpoint requires API key."""
    r = client.get("/accounts")
    assert r.status_code == 401
