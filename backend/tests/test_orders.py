"""Tests for the checkout/orders flow and stock handling."""

import pytest


@pytest.fixture
def auth_headers(client):
    token = client.post(
        "/api/auth/login", json={"username": "admin", "password": "admin"}
    ).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_create_order_success(client, seeded_db):
    product = seeded_db["product"]
    res = client.post(
        "/api/orders",
        json={
            "customer_name": "Jane Doe",
            "customer_email": "jane@example.com",
            "items": [{"product_id": product.id, "quantity": 2}],
        },
    )
    assert res.status_code == 201
    body = res.json()
    assert body["status"] == "pending"
    assert body["total"] == round(299.99 * 2, 2)
    assert body["items"][0]["product_name"] == product.name
    assert body["items"][0]["quantity"] == 2


def test_create_order_decrements_stock(client, seeded_db):
    product_id = seeded_db["product"].id
    client.post(
        "/api/orders",
        json={
            "customer_name": "Jane",
            "customer_email": "jane@example.com",
            "items": [{"product_id": product_id, "quantity": 3}],
        },
    )
    res = client.get(f"/api/products/{product_id}")
    assert res.json()["stock"] == 47  # 50 - 3


def test_create_order_insufficient_stock(client, seeded_db):
    product_id = seeded_db["product"].id
    res = client.post(
        "/api/orders",
        json={
            "customer_name": "Greedy",
            "customer_email": "g@example.com",
            "items": [{"product_id": product_id, "quantity": 999}],
        },
    )
    assert res.status_code == 409


def test_create_order_unknown_product(client):
    res = client.post(
        "/api/orders",
        json={
            "customer_name": "Nobody",
            "customer_email": "n@example.com",
            "items": [{"product_id": 9999, "quantity": 1}],
        },
    )
    assert res.status_code == 400


def test_create_order_validation(client):
    res = client.post(
        "/api/orders",
        json={"customer_name": "X", "customer_email": "e@e.com", "items": []},
    )
    assert res.status_code == 422  # empty items / too-short name


def test_create_order_rejects_invalid_email(client, seeded_db):
    product_id = seeded_db["product"].id
    res = client.post(
        "/api/orders",
        json={
            "customer_name": "Иван Петров",
            "customer_email": "not-an-email",
            "items": [{"product_id": product_id, "quantity": 1}],
        },
    )
    assert res.status_code == 422


# --- Admin order management -------------------------------------------------

def test_list_orders_requires_auth(client):
    assert client.get("/api/orders").status_code == 401


def test_admin_list_and_get_order(client, seeded_db, auth_headers):
    product_id = seeded_db["product"].id
    created = client.post(
        "/api/orders",
        json={
            "customer_name": "Buyer",
            "customer_email": "b@example.com",
            "items": [{"product_id": product_id, "quantity": 1}],
        },
    ).json()

    listed = client.get("/api/orders", headers=auth_headers)
    assert listed.status_code == 200
    assert listed.json()["total"] == 1

    got = client.get(f"/api/orders/{created['id']}", headers=auth_headers)
    assert got.status_code == 200
    assert got.json()["id"] == created["id"]


def test_update_order_status(client, seeded_db, auth_headers):
    product_id = seeded_db["product"].id
    order_id = client.post(
        "/api/orders",
        json={
            "customer_name": "Buyer",
            "customer_email": "b@example.com",
            "items": [{"product_id": product_id, "quantity": 1}],
        },
    ).json()["id"]

    ok = client.patch(
        f"/api/orders/{order_id}/status",
        headers=auth_headers,
        json={"status": "shipped"},
    )
    assert ok.status_code == 200
    assert ok.json()["status"] == "shipped"

    bad = client.patch(
        f"/api/orders/{order_id}/status",
        headers=auth_headers,
        json={"status": "teleported"},
    )
    assert bad.status_code == 400
