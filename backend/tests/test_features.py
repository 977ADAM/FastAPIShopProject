"""Tests for pagination/search, rate limiting and image upload."""

import io

import pytest

from app.limiter import limiter


@pytest.fixture
def auth_headers(client):
    token = client.post(
        "/api/auth/login", json={"username": "admin", "password": "admin"}
    ).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def _make_product(client, headers, name, category_id):
    return client.post(
        "/api/products",
        headers=headers,
        json={"name": name, "price": 9.99, "category_id": category_id},
    )


# --- Pagination & search ----------------------------------------------------

def test_search_filters_by_name(client, seeded_db, auth_headers):
    cat = seeded_db["category"].id
    _make_product(client, auth_headers, "Blue Sneakers", cat)
    _make_product(client, auth_headers, "Red Sneakers", cat)

    res = client.get("/api/products", params={"search": "blue"})
    assert res.status_code == 200
    data = res.json()
    assert data["total"] == 1
    assert data["products"][0]["name"] == "Blue Sneakers"


def test_pagination_limit_and_total(client, seeded_db, auth_headers):
    cat = seeded_db["category"].id
    for i in range(4):
        _make_product(client, auth_headers, f"Widget number {i}", cat)

    res = client.get("/api/products", params={"limit": 2, "offset": 0})
    data = res.json()
    assert len(data["products"]) == 2
    # 1 seeded + 4 created
    assert data["total"] == 5


# --- Rate limiting ----------------------------------------------------------

def test_login_rate_limited(client):
    limiter.enabled = True
    limiter.reset()
    try:
        codes = [
            client.post(
                "/api/auth/login", json={"username": "admin", "password": "admin"}
            ).status_code
            for _ in range(6)
        ]
    finally:
        limiter.enabled = False
        limiter.reset()
    assert codes[-1] == 429
    assert 200 in codes


# --- Image upload -----------------------------------------------------------

def test_upload_image(client, auth_headers, tmp_path, monkeypatch):
    from app import config
    from app.routes import uploads

    monkeypatch.setattr(config.settings, "images_dir", str(tmp_path))
    monkeypatch.setattr(uploads.settings, "images_dir", str(tmp_path))

    res = client.post(
        "/api/uploads/image",
        headers=auth_headers,
        files={"file": ("pic.png", io.BytesIO(b"\x89PNG\r\n\x1a\n"), "image/png")},
    )
    assert res.status_code == 201
    assert res.json()["image_url"].startswith("/static/images/")


def test_upload_rejects_non_image(client, auth_headers):
    res = client.post(
        "/api/uploads/image",
        headers=auth_headers,
        files={"file": ("note.txt", io.BytesIO(b"hello"), "text/plain")},
    )
    assert res.status_code == 400


def test_upload_requires_auth(client):
    res = client.post(
        "/api/uploads/image",
        files={"file": ("pic.png", io.BytesIO(b"x"), "image/png")},
    )
    assert res.status_code == 401
