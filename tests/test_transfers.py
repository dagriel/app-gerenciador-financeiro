"""Tests for transfer functionality."""


def test_transfer_creates_two_transactions(client, headers):
    """Test that transfer creates two linked transactions."""
    # Setup accounts
    a1 = client.post(
        "/accounts", json={"name": "Carteira", "type": "CASH"}, headers=headers
    ).json()["id"]
    a2 = client.post("/accounts", json={"name": "Banco", "type": "BANK"}, headers=headers).json()[
        "id"
    ]

    # Create transfer
    r = client.post(
        "/transactions/transfer",
        json={
            "date": "2026-01-01",
            "description": "Mover saldo",
            "amount_abs": 100.0,
            "from_account_id": a1,
            "to_account_id": a2,
        },
        headers=headers,
    )
    assert r.status_code == 201
    data = r.json()
    assert "pair_id" in data
    assert "out_id" in data
    assert "in_id" in data

    # Verify both transactions exist
    r = client.get("/transactions", headers=headers)
    assert r.status_code == 200
    txs = r.json()
    pair_txs = [t for t in txs if t["transfer_pair_id"] == data["pair_id"]]
    assert len(pair_txs) == 2

    # Verify amounts (money is returned as string)
    amounts = sorted([t["amount"] for t in pair_txs])
    assert amounts == ["-100.00", "100.00"]


def test_delete_transfer_deletes_pair(client, headers):
    """Test that deleting one transfer transaction deletes both."""
    # Setup
    a1 = client.post(
        "/accounts", json={"name": "Carteira", "type": "CASH"}, headers=headers
    ).json()["id"]
    a2 = client.post("/accounts", json={"name": "Banco", "type": "BANK"}, headers=headers).json()[
        "id"
    ]

    # Create transfer
    r = client.post(
        "/transactions/transfer",
        json={
            "date": "2026-01-01",
            "description": "Test transfer",
            "amount_abs": 50.0,
            "from_account_id": a1,
            "to_account_id": a2,
        },
        headers=headers,
    )
    pair_id = r.json()["pair_id"]

    # Get one transaction ID
    r = client.get("/transactions", headers=headers)
    txs = r.json()
    tx_id = next(t["id"] for t in txs if t["transfer_pair_id"] == pair_id)

    # Delete one transaction
    r = client.delete(f"/transactions/{tx_id}", headers=headers)
    assert r.status_code == 204

    # Verify both are gone
    r = client.get("/transactions", headers=headers)
    txs = r.json()
    assert all(t["transfer_pair_id"] != pair_id for t in txs)


def test_transfer_same_account_rejected(client, headers):
    """Test that transfer between same account is rejected."""
    acc = client.post("/accounts", json={"name": "Banco", "type": "BANK"}, headers=headers).json()[
        "id"
    ]

    r = client.post(
        "/transactions/transfer",
        json={
            "date": "2026-01-01",
            "description": "Invalid",
            "amount_abs": 10.0,
            "from_account_id": acc,
            "to_account_id": acc,
        },
        headers=headers,
    )
    assert r.status_code == 400


def test_transfer_negative_amount_rejected(client, headers):
    """Test that transfer with negative amount is rejected."""
    a1 = client.post(
        "/accounts", json={"name": "Carteira", "type": "CASH"}, headers=headers
    ).json()["id"]
    a2 = client.post("/accounts", json={"name": "Banco", "type": "BANK"}, headers=headers).json()[
        "id"
    ]

    r = client.post(
        "/transactions/transfer",
        json={
            "date": "2026-01-01",
            "description": "Invalid",
            "amount_abs": -10.0,
            "from_account_id": a1,
            "to_account_id": a2,
        },
        headers=headers,
    )
    assert r.status_code == 422  # Pydantic validation error
