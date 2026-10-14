
def test_root_returns_application_status(client):
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["application"] == "SecureApp"
    assert response.json()["status"] == "running"


def test_health_check(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_create_and_retrieve_item(client):
    payload = {
        "name": "Security Book",
        "description": "A book about application security",
        "price": 29.99,
    }

    create_response = client.post("/items", json=payload)

    assert create_response.status_code == 201

    created_item = create_response.json()
    assert created_item["name"] == "Security Book"

    item_id = created_item["id"]
    get_response = client.get(f"/items/{item_id}")

    assert get_response.status_code == 200
    assert get_response.json() == created_item


def test_rejects_invalid_item_price(client):
    response = client.post(
        "/items",
        json={
            "name": "Invalid Item",
            "description": "This should fail validation",
            "price": -10,
        },
    )

    assert response.status_code == 422


def test_missing_item_returns_404(client):
    response = client.get("/items/999999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Item not found"


def test_item_persists_across_requests(client):
    response = client.post(
        "/items",
        json={
            "name": "Persistence Test",
            "description": "Saved in SQLite",
            "price": 15.0,
        },
    )

    assert response.status_code == 201
    item_id = response.json()["id"]

    retrieved = client.get(f"/items/{item_id}")

    assert retrieved.status_code == 200
    assert retrieved.json()["name"] == "Persistence Test"
