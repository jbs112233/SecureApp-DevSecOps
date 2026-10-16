
import importlib

import pytest
import config


def test_default_rate_limit(monkeypatch):
    monkeypatch.delenv("SECUREAPP_RATE_LIMIT", raising=False)

    reloaded_config = importlib.reload(config)

    assert reloaded_config.RATE_LIMIT == "5/minute"


def test_rate_limit_can_be_overridden(monkeypatch):
    monkeypatch.setenv("SECUREAPP_RATE_LIMIT", "10/minute")

    reloaded_config = importlib.reload(config)

    assert reloaded_config.RATE_LIMIT == "10/minute"


def test_invalid_access_token_minutes_is_rejected(monkeypatch):
    monkeypatch.setenv("SECUREAPP_SECRET_KEY", "a" * 32)
    monkeypatch.setenv("SECUREAPP_ACCESS_TOKEN_MINUTES", "thirty")

    with pytest.raises(
        RuntimeError,
        match="must be a valid integer",
    ):
        importlib.reload(config)


@pytest.mark.parametrize("invalid_minutes", ["0", "-1"])
def test_nonpositive_access_token_minutes_is_rejected(
    monkeypatch,
    invalid_minutes,
):
    monkeypatch.setenv("SECUREAPP_SECRET_KEY", "a" * 32)
    monkeypatch.setenv(
        "SECUREAPP_ACCESS_TOKEN_MINUTES",
        invalid_minutes,
    )

    with pytest.raises(
        RuntimeError,
        match="must be greater than zero",
    ):
        importlib.reload(config)


def test_short_secret_key_is_rejected(monkeypatch):
    monkeypatch.setenv("SECUREAPP_SECRET_KEY", "too-short")
    monkeypatch.setenv("SECUREAPP_ACCESS_TOKEN_MINUTES", "30")

    with pytest.raises(
        RuntimeError,
        match="must contain at least 32 characters",
    ):
        importlib.reload(config)


def test_missing_secret_key_is_rejected(monkeypatch):
    monkeypatch.setenv("SECUREAPP_SECRET_KEY", "")
    monkeypatch.setenv("SECUREAPP_ACCESS_TOKEN_MINUTES", "30")

    with pytest.raises(
        RuntimeError,
        match="must contain at least 32 characters",
    ):
        importlib.reload(config)



def test_secret_key_with_minimum_length_is_accepted(monkeypatch):
    monkeypatch.setenv("SECUREAPP_SECRET_KEY", "a" * 32)
    monkeypatch.setenv("SECUREAPP_ACCESS_TOKEN_MINUTES", "30")

    reloaded_config = importlib.reload(config)

    assert reloaded_config.SECRET_KEY == "a" * 32
