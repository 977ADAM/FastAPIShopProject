"""Tests for JWT auth and the protected admin CRUD endpoints."""

import pytest


@pytest.fixture
def admin_token(client):
    response = client.post(
        "/api/auth/login", json={"username": "admin", "password": "admin"}
    )
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.fixture
def auth_headers(admin_token):
    return {"Authorization": f"Bearer {admin_token}"}


# --- Auth -------------------------------------------------------------------

def test_login_success(client):
    response = client.post(
        "/api/auth/login", json={"username": "admin", "password": "admin"}
    )
    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]


def test_login_wrong_password(client):
    response = client.post(
        "/api/auth/login", json={"username": "admin", "password": "nope"}
    )
    assert response.status_code == 401


def test_write_requires_auth(client, seeded_db):
    response = client.post(
        "/api/products",
        json={
            "name": "No Auth Product",
            "price": 10.0,
            "category_id": seeded_db["category"].id,
        },
    )
    assert response.status_code == 401  # missing bearer credentials


def test_write_rejects_bad_token(client, seeded_db):
    response = client.post(
        "/api/products",
        headers={"Authorization": "Bearer not-a-real-token"},
        json={
            "name": "Bad Token Product",
            "price": 10.0,
            "category_id": seeded_db["category"].id,
        },
    )
    assert response.status_code == 401


# --- Product CRUD -----------------------------------------------------------

def test_create_product(client, seeded_db, auth_headers):
    response = client.post(
        "/api/products",
        headers=auth_headers,
        json={
            "name": "Mechanical Keyboard",
            "description": "Clicky keys",
            "price": 120.0,
            "category_id": seeded_db["category"].id,
            "image_url": "https://example.com/kb.jpg",
        },
    )
    assert response.status_code == 201
    assert response.json()["name"] == "Mechanical Keyboard"


def test_create_product_unknown_category(client, auth_headers):
    response = client.post(
        "/api/products",
        headers=auth_headers,
        json={"name": "Orphan Product", "price": 5.0, "category_id": 9999},
    )
    assert response.status_code == 400


def test_update_product(client, seeded_db, auth_headers):
    product_id = seeded_db["product"].id
    response = client.put(
        f"/api/products/{product_id}",
        headers=auth_headers,
        json={"price": 199.99},
    )
    assert response.status_code == 200
    assert response.json()["price"] == 199.99


def test_delete_product(client, seeded_db, auth_headers):
    product_id = seeded_db["product"].id
    response = client.delete(f"/api/products/{product_id}", headers=auth_headers)
    assert response.status_code == 204
    assert client.get(f"/api/products/{product_id}").status_code == 404


# --- Category CRUD ----------------------------------------------------------

def test_create_category(client, auth_headers):
    response = client.post(
        "/api/categories",
        headers=auth_headers,
        json={"name": "Gardening", "slug": "gardening"},
    )
    assert response.status_code == 201
    assert response.json()["slug"] == "gardening"


def test_create_category_duplicate_slug(client, auth_headers):
    response = client.post(
        "/api/categories",
        headers=auth_headers,
        json={"name": "Electronics", "slug": "electronics"},
    )
    assert response.status_code == 409


def test_delete_empty_category(client, auth_headers):
    created = client.post(
        "/api/categories",
        headers=auth_headers,
        json={"name": "Temporary", "slug": "temporary"},
    ).json()
    response = client.delete(f"/api/categories/{created['id']}", headers=auth_headers)
    assert response.status_code == 204


def test_delete_category_with_products_conflict(client, seeded_db, auth_headers):
    category_id = seeded_db["category"].id
    response = client.delete(f"/api/categories/{category_id}", headers=auth_headers)
    assert response.status_code == 409
