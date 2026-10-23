"""Configuration par variables d'environnement, validee au demarrage (ET-008).

Aucune valeur secrete n'est presente dans le depot. Une configuration invalide
empeche le demarrage (refus par defaut).
"""

from __future__ import annotations

import os
import re
from enum import StrEnum
from typing import Any, Self
from uuid import UUID

from pydantic import Field, SecretStr, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_DATABASE_SCHEMES = ("postgresql+psycopg://", "postgresql+psycopg_async://")
_WORKSPACE_NIL = UUID("00000000-0000-0000-0000-000000000000")


class ConfigError(RuntimeError):
    """Configuration absente ou invalide : le demarrage doit echouer."""


class Environment(StrEnum):
    LOCAL = "local"
    CI = "ci"
    PREPROD = "preprod"
    PROD = "prod"


class Role(StrEnum):
    """Deux roles, une seule image applicative (ET-007)."""

    API = "api"
    WORKER = "worker"


class LogLevel(StrEnum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


class Settings(BaseSettings):
    """Schema de configuration (ET-008). Prefixe : AGENT_."""

    model_config = SettingsConfigDict(
        env_prefix="AGENT_",
        env_file=None,
        extra="forbid",
        frozen=True,
        case_sensitive=False,
    )

    environment: Environment = Environment.LOCAL
    role: Role = Role.API
    database_url: str = "postgresql+psycopg://agent:agent@localhost:55432/agent"
    log_level: LogLevel = LogLevel.INFO
    workspace_id: UUID = _WORKSPACE_NIL
    ledger_verify_interval_seconds: int = Field(default=900, ge=60, le=86_400)
    secret_key: SecretStr | None = None
    otel_endpoint: str | None = None
    api_host: str = "127.0.0.1"
    api_port: int = Field(default=8000, ge=1, le=65_535)

    @field_validator("database_url")
    @classmethod
    def _validate_database_url(cls, value: str) -> str:
        if not value.startswith(_DATABASE_SCHEMES):
            raise ValueError(
                "database_url doit utiliser le pilote psycopg 3 (postgresql+psycopg://)"
            )
        if not re.match(r"^postgresql\+psycopg(?:_async)?://[^\s]+$", value):
            raise ValueError("database_url malformee")
        return value

    @model_validator(mode="before")
    @classmethod
    def _reject_unknown_environment_keys(cls, data: Any) -> Any:
        """Une variable AGENT_* inconnue est une faute de configuration."""
        known = {f"AGENT_{name.upper()}" for name in cls.model_fields}
        unknown = sorted(
            key
            for key in os.environ
            if key.upper().startswith("AGENT_") and key.upper() not in known
        )
        if unknown:
            raise ValueError(f"variables de configuration inconnues : {', '.join(unknown)}")
        return data

    @model_validator(mode="after")
    def _production_requires_secret(self) -> Self:
        if self.environment is Environment.PROD and self.secret_key is None:
            raise ValueError("secret_key obligatoire en production")
        return self


def load_settings(**overrides: object) -> Settings:
    """Charge et valide la configuration ; leve ConfigError si invalide."""
    try:
        return Settings(**overrides)  # type: ignore[arg-type]
    except Exception as exc:  # pydantic ValidationError et erreurs d'environnement
        raise ConfigError(str(exc)) from exc
