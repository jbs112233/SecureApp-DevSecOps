
from sqlalchemy import select

from database import get_db
from models import User


def test_inactive_user_cannot_use_existing_token(client):
    registration = client.post(
        "/auth/register",
        json={
            "username": "inactiveuser01",
            "password": "a-strong-test-password-123",
        },
    )
    assert registration.status_code == 201
    user_id = registration.json()["id"]

    login = client.post(
        "/auth/token",
        json={
            "username": "inactiveuser01",
            "password": "a-strong-test-password-123",
        },
    )
    assert login.status_code == 200
    token = login.json()["access_token"]


    db_generator = client.app.dependency_overrides[get_db]()
    db = next(db_generator)
    try:
        user = db.scalar(select(User).where(User.id == user_id))
        assert user is not None
        user.is_active = False
        db.commit()
    finally:
        db_generator.close()

    response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 401


def test_register_creates_regular_user(client):
    response = client.post(
        "/auth/register",
        json={
            "username": "authuser01",
            "password": "a-strong-test-password-123",
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "authuser01"
    assert data["role"] == "user"
    assert data["is_active"] is True
    assert "password_hash" not in data


def test_register_rejects_duplicate_username(client):
    payload = {
        "username": "duplicate01",
        "password": "a-strong-test-password-123",
    }

    first = client.post("/auth/register", json=payload)
    second = client.post("/auth/register", json=payload)

    assert first.status_code == 201
    assert second.status_code == 409


def test_login_returns_access_token(client):
    client.post(
        "/auth/register",
        json={
            "username": "loginuser01",
            "password": "a-strong-test-password-123",
        },
    )

    response = client.post(
        "/auth/token",
        json={
            "username": "loginuser01",
            "password": "a-strong-test-password-123",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data["access_token"], str)
    assert data["token_type"] == "bearer"


def test_login_rejects_wrong_password(client):
    client.post(
        "/auth/register",
        json={
            "username": "wrongpass01",
            "password": "a-strong-test-password-123",
        },
    )

    response = client.post(
        "/auth/token",
        json={
            "username": "wrongpass01",
            "password": "incorrect-password-123",
        },
    )

    assert response.status_code == 401


def test_current_user_requires_token(client):
    response = client.get("/auth/me")

    assert response.status_code == 401


def test_current_user_accepts_valid_token(client):
    client.post(
        "/auth/register",
        json={
            "username": "profileuser01",
            "password": "a-strong-test-password-123",
        },
    )

    login_response = client.post(
        "/auth/token",
        json={
            "username": "profileuser01",
            "password": "a-strong-test-password-123",
        },
    )
    token = login_response.json()["access_token"]

    response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json()["username"] == "profileuser01"
    assert response.json()["role"] == "user"


from datetime import timedelta

from auth import create_access_token


def test_expired_token_is_rejected(client):
    client.post(
        "/auth/register",
        json={
            "username": "expireduser01",
            "password": "a-strong-test-password-123",
        },
    )


    token = create_access_token(
        subject="1",
        role="user",
        expires_delta=timedelta(minutes=-1),
    )

    response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 401


def test_invalid_token_is_rejected(client):
    response = client.get(
        "/auth/me",
        headers={"Authorization": "Bearer not-a-valid-jwt"},
    )

    assert response.status_code == 401


def test_registration_cannot_assign_admin_role(client):
    response = client.post(
        "/auth/register",
        json={
            "username": "rolecheck01",
            "password": "a-strong-test-password-123",
            "role": "admin",
        },
    )

    assert response.status_code == 201
    assert response.json()["role"] == "user"


def test_registration_rejects_short_password(client):
    response = client.post(
        "/auth/register",
        json={
            "username": "shortpass01",
            "password": "short",
        },
    )

    assert response.status_code == 422


def test_registration_rejects_invalid_username(client):
    response = client.post(
        "/auth/register",
        json={
            "username": "bad username!",
            "password": "a-strong-test-password-123",
        },
    )

    assert response.status_code == 422


def test_login_rate_limit(client):
    from auth_routes import limiter

    limiter._storage.reset()

    responses = [
        client.post(
            "/auth/token",
            json={
                "username": "ratelimituser",
                "password": "incorrect-password-123",
            },
        )
        for _ in range(6)
    ]

    assert all(
        response.status_code == 401
        for response in responses[:5]
    ), [response.status_code for response in responses]

    assert responses[5].status_code == 429

    
def test_inactive_user_cannot_login(client):
    password = "a-strong-test-password-123"

    registration = client.post(
        "/auth/register",
        json={
            "username": "inactive_login01",
            "password": password,
        },
    )
    assert registration.status_code == 201

    user_id = registration.json()["id"]

    db_generator = client.app.dependency_overrides[get_db]()
    db = next(db_generator)
    try:
        user = db.scalar(select(User).where(User.id == user_id))
        assert user is not None
        user.is_active = False
        db.commit()
    finally:
        db_generator.close()

    response = client.post(
        "/auth/token",
        json={
            "username": "inactive_login01",
            "password": password,
        },
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Account is inactive"

def test_login_errors_do_not_reveal_username_existence(client):
    existing_username = "genericerror01"
    password = "a-strong-test-password-123"

    registration = client.post(
        "/auth/register",
        json={
            "username": existing_username,
            "password": password,
        },
    )
    assert registration.status_code == 201

    wrong_password = client.post(
        "/auth/token",
        json={
            "username": existing_username,
            "password": "incorrect-password-123",
        },
    )

    unknown_username = client.post(
        "/auth/token",
        json={
            "username": "unknownuser01",
            "password": password,
        },
    )

    assert wrong_password.status_code == 401
    assert unknown_username.status_code == 401
    assert wrong_password.json()["detail"] == "Invalid username or password"
    assert unknown_username.json()["detail"] == "Invalid username or password"