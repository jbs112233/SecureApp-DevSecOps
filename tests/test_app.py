
def register_and_login(client, username, password="SecureTestPassword123!"):
    register_response = client.post(
        "/auth/register",
        json={"username": username, "password": password},
    )
    assert register_response.status_code == 201

    login_response = client.post(
        "/auth/token",
        json={"username": username, "password": password},
    )
    assert login_response.status_code == 200

    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


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
    headers = register_and_login(client, "itemowner")
    payload = {
        "name": "Security Book",
        "description": "A book about application security",
        "price": 29.99,
    }

    create_response = client.post("/items", json=payload, headers=headers)

    assert create_response.status_code == 201

    created_item = create_response.json()
    assert created_item["name"] == "Security Book"

    item_id = created_item["id"]
    get_response = client.get(f"/items/{item_id}", headers=headers)

    assert get_response.status_code == 200
    assert get_response.json() == created_item


def test_unauthenticated_user_cannot_create_item(client):
    response = client.post(
        "/items",
        json={
            "name": "Unauthorized Item",
            "description": "Must not be created",
            "price": 10.0,
        },
    )

    assert response.status_code == 401


def test_different_user_cannot_retrieve_item(client):
    owner_headers = register_and_login(client, "firstowner")
    other_headers = register_and_login(client, "secondowner")

    create_response = client.post(
        "/items",
        json={
            "name": "Private Item",
            "description": "Belongs to the first user",
            "price": 25.0,
        },
        headers=owner_headers,
    )
    assert create_response.status_code == 201

    item_id = create_response.json()["id"]
    response = client.get(f"/items/{item_id}", headers=other_headers)

    assert response.status_code == 404
    assert response.json()["detail"] == "Item not found"


def test_rejects_invalid_item_price(client):
    headers = register_and_login(client, "pricevalidator")

    response = client.post(
        "/items",
        headers=headers,
        json={
            "name": "Invalid Item",
            "description": "This should fail validation",
            "price": -10,
        },
    )

    assert response.status_code == 422


def test_missing_item_returns_404(client):
    headers = register_and_login(client, "missingitemuser")

    response = client.get("/items/999999", headers=headers)

    assert response.status_code == 404
    assert response.json()["detail"] == "Item not found"


def test_item_persists_across_requests(client):
    headers = register_and_login(client, "persistenceuser")

    response = client.post(
        "/items",
        headers=headers,
        json={
            "name": "Persistence Test",
            "description": "Saved in the test database",
            "price": 15.0,
        },
    )

    assert response.status_code == 201
    item_id = response.json()["id"]

    retrieved = client.get(f"/items/{item_id}", headers=headers)

    assert retrieved.status_code == 200
    assert retrieved.json()["name"] == "Persistence Test"


def test_denied_cross_user_access_does_not_affect_owner_item(client):
    owner_headers = register_and_login(client, "isolationowner")
    other_headers = register_and_login(client, "isolationother")

    create_response = client.post(
        "/items",
        json={
            "name": "Owner's Private Item",
            "description": "Must remain accessible to its owner",
            "price": 42.0,
        },
        headers=owner_headers,
    )
    assert create_response.status_code == 201

    item_id = create_response.json()["id"]

    denied_response = client.get(
        f"/items/{item_id}",
        headers=other_headers,
    )
    assert denied_response.status_code == 404

    owner_response = client.get(
        f"/items/{item_id}",
        headers=owner_headers,
    )
    assert owner_response.status_code == 200
    assert owner_response.json()["id"] == item_id
    assert owner_response.json()["name"] == "Owner's Private Item"
