
from fastapi.testclient import TestClient

from app import app

client = TestClient(app)

from app import limiter

def test_root_returns_application_status():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["application"] == "SecureApp"
    assert response.json()["status"] == "running"


def test_health_check():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_create_and_retrieve_item():
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
    assert get_response.json()["id"] == item_id


def test_rejects_invalid_item_price():
    payload = {
        "name": "Invalid Item",
        "description": "This should fail validation",
        "price": -10,
    }

    response = client.post("/items", json=payload)

    assert response.status_code == 422


def test_missing_item_returns_404():
    response = client.get("/items/999999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Item not found"

def test_security_headers_on_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["x-frame-options"] == "DENY"
    assert response.headers["referrer-policy"] == "no-referrer"
    assert response.headers["permissions-policy"] == "camera=(), microphone=(), geolocation=()"


def test_security_headers_on_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["x-frame-options"] == "DENY" 


def test_item_creation_rate_limit():
    limiter._storage.reset()

    payload = {
        "name": "Rate limit test",
        "description": "Testing request limits",
        "price": 10.0,
    }

    responses = [
        client.post("/items", json=payload)
        for _ in range(6)
    ]

    assert all(
        response.status_code == 201
        for response in responses[:5]
    )
    assert responses[5].status_code == 429