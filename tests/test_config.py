
import importlib

import config


def test_default_rate_limit(monkeypatch):
    monkeypatch.delenv("SECUREAPP_RATE_LIMIT", raising=False)

    reloaded_config = importlib.reload(config)

    assert reloaded_config.RATE_LIMIT == "5/minute"


def test_rate_limit_can_be_overridden(monkeypatch):
    monkeypatch.setenv("SECUREAPP_RATE_LIMIT", "10/minute")

    reloaded_config = importlib.reload(config)

    assert reloaded_config.RATE_LIMIT == "10/minute"
