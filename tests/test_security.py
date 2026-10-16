

import logging

from app import limiter


def register_and_login(client, username, password="SecureTestPassword123!"):
    """Register a test user and return authorization headers."""
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


def test_security_headers_on_root(client):
    response = client.get("/")

    assert response.status_code == 200
    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["x-frame-options"] == "DENY"
    assert response.headers["referrer-policy"] == "no-referrer"
    assert (
        response.headers["permissions-policy"]
        == "camera=(), microphone=(), geolocation=()"
    )


def test_security_headers_on_health(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["x-frame-options"] == "DENY"


def test_invalid_item_input_is_rejected(client):
    headers = register_and_login(client, "invalidinputuser")

    response = client.post(
        "/items",
        headers=headers,
        json={
            "name": "",
            "description": "Invalid item",
            "price": -1,
        },
    )

    assert response.status_code == 422


def test_item_creation_logs_events(client, caplog):
    headers = register_and_login(client, "loggingtestuser")

    with caplog.at_level(logging.INFO, logger="secureapp"):
        response = client.post(
            "/items",
            headers=headers,
            json={
                "name": "Logging regression test",
                "description": (
                    "This description should not appear in logs"
                ),
                "price": 10.0,
            },
        )

    assert response.status_code == 201

    messages = [
        record.getMessage()
        for record in caplog.records
        if record.name == "secureapp"
    ]

    assert any(
        "Item created: item_id=" in message
        for message in messages
    )

    assert all(
        "This description should not appear in logs" not in message
        for message in messages
    )


def test_item_creation_rate_limit(client):
    limiter._storage.reset()
    headers = register_and_login(client, "ratelimituser")

    payload = {
        "name": "Rate Limit Test",
        "description": "Security Regression Test",
        "price": 10.0,
    }

    responses = [
        client.post("/items", json=payload, headers=headers)
        for _ in range(6)
    ]

    assert all(
        response.status_code == 201
        for response in responses[:5]
    ), [response.status_code for response in responses]

    assert responses[5].status_code == 429
