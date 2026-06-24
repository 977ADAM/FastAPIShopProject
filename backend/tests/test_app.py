"""End-to-end API tests covering root, products, categories and cart."""


def test_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


# --- Products ---------------------------------------------------------------

def test_list_products(client, seeded_db):
    response = client.get("/api/products")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["products"][0]["name"] == seeded_db["product"].name


def test_get_product(client, seeded_db):
    product_id = seeded_db["product"].id
    response = client.get(f"/api/products/{product_id}")
    assert response.status_code == 200
    assert response.json()["id"] == product_id


def test_get_product_not_found(client):
    response = client.get("/api/products/9999")
    assert response.status_code == 404


def test_products_by_category(client, seeded_db):
    category_id = seeded_db["category"].id
    response = client.get(f"/api/products/category/{category_id}")
    assert response.status_code == 200
    assert response.json()["total"] == 1


# --- Categories -------------------------------------------------------------

def test_list_categories(client):
    response = client.get("/api/categories")
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_get_category(client, seeded_db):
    category_id = seeded_db["category"].id
    response = client.get(f"/api/categories/{category_id}")
    assert response.status_code == 200
    assert response.json()["slug"] == "electronics"


def test_get_category_not_found(client):
    response = client.get("/api/categories/9999")
    assert response.status_code == 404


# --- Cart -------------------------------------------------------------------

def test_add_to_cart(client, seeded_db):
    product_id = seeded_db["product"].id
    response = client.post(
        "/api/cart/add",
        json={"product_id": product_id, "quantity": 2, "cart": {}},
    )
    assert response.status_code == 200
    assert response.json()["cart"] == {str(product_id): 2}


def test_add_to_cart_unknown_product(client):
    response = client.post(
        "/api/cart/add",
        json={"product_id": 9999, "quantity": 1, "cart": {}},
    )
    assert response.status_code == 404


def test_cart_details_totals(client, seeded_db):
    product_id = seeded_db["product"].id
    response = client.post("/api/cart", json={str(product_id): 2})
    assert response.status_code == 200
    data = response.json()
    assert data["items_count"] == 2
    assert data["total"] == round(299.99 * 2, 2)


def test_update_cart_item(client, seeded_db):
    product_id = seeded_db["product"].id
    response = client.put(
        "/api/cart/update",
        json={"product_id": product_id, "quantity": 5, "cart": {str(product_id): 2}},
    )
    assert response.status_code == 200
    assert response.json()["cart"] == {str(product_id): 5}


def test_remove_from_cart(client, seeded_db):
    product_id = seeded_db["product"].id
    response = client.request(
        "DELETE",
        f"/api/cart/remove/{product_id}",
        json={"cart": {str(product_id): 2}},
    )
    assert response.status_code == 200
    assert response.json()["cart"] == {}
