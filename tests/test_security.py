
import logging

from app import limiter


def test_security_headers_on_root(client):
    response = client.get("/")

    assert response.status_code == 200
    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["x-frame-options"] == "DENY"
    assert response.headers["referrer-policy"] == "no-referrer"
    assert response.headers["permissions-policy"] == (
        "camera=(), microphone=(), geolocation=()"
    )


def test_security_headers_on_health(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["x-frame-options"] == "DENY"


def test_invalid_item_input_is_rejected(client):
    response = client.post(
        "/items",
        json={
            "name": "",
            "description": "Invalid item",
            "price": -1,
        },
    )

    assert response.status_code == 422


def test_item_creation_logs_events(client, caplog):
    import logging

    caplog.set_level(logging.INFO, logger="secureapp")

    response = client.post(
        "/items",
        json={
            "name": "Logging regression test",
            "description": "This description should not appear in logs",
            "price": 10.0,
        },
    )

    print("Response status:", response.status_code)
    print(
        "Captured records:",
        [
            (record.name, record.levelname, record.getMessage())
            for record in caplog.records
        ],
    )

    assert response.status_code == 201
    assert any(
        record.name == "secureapp"
        and "Item created: item_id=" in record.getMessage()
        for record in caplog.records
    )
    assert all(
        "This description should not appear in logs"
        not in record.getMessage()
        for record in caplog.records
    )



def test_item_creation_rate_limit(client):
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


def test_item_creation_logs_events(client, caplog):
    caplog.set_level(logging.INFO, logger="secureapp")

    response = client.post(
        "/items",
        json={
            "name": "Logging regression test",
            "description": "This description should not appear in logs",
            "price": 10.0,
        },
    )

    assert response.status_code == 201

