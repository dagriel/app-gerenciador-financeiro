"""Tests for categories endpoints."""


def test_categories_crud(client, headers):
    """Test complete CRUD flow for categories."""
    # Create
    r = client.post(
        "/categories",
        json={"name": "Alimentação", "kind": "EXPENSE", "group": "ESSENTIAL"},
        headers=headers,
    )
    assert r.status_code == 201
    cat_id = r.json()["id"]
    assert r.json()["name"] == "Alimentação"

    # List
    r = client.get("/categories", headers=headers)
    assert r.status_code == 200
    assert any(c["id"] == cat_id for c in r.json())

    # Update
    r = client.put(f"/categories/{cat_id}", json={"group": "LIFESTYLE"}, headers=headers)
    assert r.status_code == 200
    assert r.json()["group"] == "LIFESTYLE"

    # Delete (soft delete)
    r = client.delete(f"/categories/{cat_id}", headers=headers)
    assert r.status_code == 204


def test_category_name_unique(client, headers):
    """Test that category names must be unique."""
    client.post(
        "/categories",
        json={"name": "Transporte", "kind": "EXPENSE", "group": "ESSENTIAL"},
        headers=headers,
    )
    r = client.post(
        "/categories",
        json={"name": "Transporte", "kind": "EXPENSE", "group": "ESSENTIAL"},
        headers=headers,
    )
    assert r.status_code == 409
