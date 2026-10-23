"""ET-008 : configuration validee, refus par defaut, aucun secret dans le depot."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from agent.platform.config import (
    ConfigError,
    Environment,
    Role,
    Settings,
    load_settings,
)


def test_defaults_are_local_and_api() -> None:
    settings = Settings()
    assert settings.environment is Environment.LOCAL
    assert settings.role is Role.API
    assert settings.database_url.startswith("postgresql+psycopg://")


def test_invalid_database_scheme_is_rejected() -> None:
    with pytest.raises(ValidationError):
        Settings(database_url="sqlite:///local.db")


def test_production_requires_secret() -> None:
    with pytest.raises(ValidationError):
        Settings(environment=Environment.PROD, secret_key=None)


def test_load_settings_wraps_validation_error() -> None:
    with pytest.raises(ConfigError):
        load_settings(database_url="mysql://nope")


def test_environment_variables_are_read(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("AGENT_ROLE", "worker")
    monkeypatch.setenv("AGENT_ENVIRONMENT", "ci")
    settings = Settings()
    assert settings.role is Role.WORKER
    assert settings.environment is Environment.CI


def test_unknown_variable_is_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("AGENT_UNKNOWN_SETTING", "1")
    with pytest.raises(ValidationError):
        Settings()
