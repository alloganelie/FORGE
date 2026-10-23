"""Fixtures PostgreSQL reelles (ET-358 : jamais de base simulee)."""

from __future__ import annotations

import os
import subprocess
import sys
from collections.abc import Iterator
from datetime import UTC, datetime
from pathlib import Path
from uuid import UUID

import psycopg
import pytest
from sqlalchemy import Connection, create_engine, text
from sqlalchemy.engine import make_url

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_TEST_URL = "postgresql+psycopg://agent:agent@localhost:55432/agent_test"
TEST_DATABASE_URL = os.environ.get(
    "FORGE_TEST_DATABASE_URL", os.environ.get("AGENT_TEST_DATABASE_URL", DEFAULT_TEST_URL)
)
WORKSPACE_ID = UUID("11111111-1111-7111-8111-111111111111")
USER_ID = UUID("22222222-2222-7222-8222-222222222222")
OTHER_USER_ID = UUID("33333333-3333-7333-8333-333333333333")


def _raw_url(database: str) -> str:
    url = make_url(TEST_DATABASE_URL).set(drivername="postgresql", database=database)
    return url.render_as_string(hide_password=False)


def _ensure_database() -> None:
    admin = _raw_url("postgres")
    try:
        with psycopg.connect(admin, autocommit=True, connect_timeout=5) as connection:
            exists = connection.execute(
                "SELECT 1 FROM pg_database WHERE datname = %s", ("agent_test",)
            ).fetchone()
            if not exists:
                connection.execute("CREATE DATABASE agent_test")
    except psycopg.Error as exc:
        raise pytest.UsageError(
            f"PostgreSQL indisponible. Lancer 'make db-up' puis relancer les tests. Detail : {exc}"
        ) from exc


def _migrate() -> None:
    env = os.environ.copy()
    env["AGENT_DATABASE_URL"] = TEST_DATABASE_URL
    completed = subprocess.run(
        [sys.executable, "-m", "alembic", "-c", "backend/alembic.ini", "upgrade", "head"],
        cwd=ROOT,
        env=env,
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        raise pytest.UsageError(f"Migration impossible : {completed.stdout}\n{completed.stderr}")


@pytest.fixture(scope="session")
def database_url() -> str:
    _ensure_database()
    _migrate()
    return TEST_DATABASE_URL


@pytest.fixture
def db_connection(database_url: str) -> Iterator[Connection]:
    engine = create_engine(database_url)
    connection = engine.connect()
    transaction = connection.begin()
    try:
        connection.execute(
            text("SELECT set_config('app.workspace_id', :value, true)"),
            {"value": str(WORKSPACE_ID)},
        )
        connection.execute(
            text("SELECT set_config('app.user_id', :value, true)"),
            {"value": str(USER_ID)},
        )
        connection.execute(text("SELECT set_config('app.role', 'responsible', true)"))
        connection.execute(text("SELECT set_config('app.transition_id', '', true)"))
        yield connection
    finally:
        transaction.rollback()
        connection.close()
        engine.dispose()


@pytest.fixture
def seeded(db_connection: Connection) -> Connection:
    now = datetime(2026, 10, 23, 12, 0, tzinfo=UTC)
    db_connection.execute(
        text("INSERT INTO workspaces (id, name, created_at) VALUES (:id, :name, :at)"),
        {"id": WORKSPACE_ID, "name": "Espace de test", "at": now},
    )
    db_connection.execute(
        text(
            """
            INSERT INTO users (id, workspace_id, display_name, role, created_at)
            VALUES (:id, :workspace_id, :name, 'responsible', :at),
                   (:other_id, :workspace_id, :other_name, 'user', :at)
            """
        ),
        {
            "id": USER_ID,
            "other_id": OTHER_USER_ID,
            "workspace_id": WORKSPACE_ID,
            "name": "Personne responsable",
            "other_name": "Autre utilisateur",
            "at": now,
        },
    )
    db_connection.execute(
        text(
            """
            INSERT INTO requests
              (id, workspace_id, author_id, original_text, state, created_at)
            VALUES
              (:id, :workspace_id, :author_id, :text, 'received', :at)
            """
        ),
        {
            "id": UUID("44444444-4444-7444-8444-444444444444"),
            "workspace_id": WORKSPACE_ID,
            "author_id": USER_ID,
            "text": "Demande de test",
            "at": now,
        },
    )
    return db_connection
