
from fastapi.testclient import TestClient

from app import app, limiter

client = TestClient(app)


def test_security_headers_on_root():
    response = client.get("/")

    assert response.status_code == 200
    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["x-frame-options"] == "DENY"
    assert response.headers["referrer-policy"] == "no-referrer"
    assert response.headers["permissions-policy"] == (
        "camera=(), microphone=(), geolocation=()"
    )


def test_security_headers_on_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["x-frame-options"] == "DENY"


def test_invalid_item_input_is_rejected():
    response = client.post(
        "/items",
        json={
            "name": "",
            "description": "Invalid item",
            "price": -1,
        },
    )

    assert response.status_code == 422


def test_missing_item_returns_404():
    response = client.get("/items/999999")

    assert response.status_code == 404


def test_item_creation_rate_limit():
    limiter._storage.reset()

    payload = {
        "name": "Rate limit test",
        "description": "Security regression test",
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

    def test_item_creation_logs_events(caplog):
        import logging

        caplog.set_level(logging.INFO, logger="secureapp")

        payload = {
            "name": "logging regression test",
            "description": "this description should not appear in logs",
            "price": 10.0,
        }

        response = client.post("/items", json=payload)

        assert response.status_code == 201
        assert "Item created: item_id=" in caplog.text
        assert "this description should not appear in logs" not in caplog.text
        
