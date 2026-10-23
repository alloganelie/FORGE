"""SCR-15, SCR-17, Q-001 : console minimale avec FORGE dans l'en-tete."""

from __future__ import annotations

from uuid import UUID

import pytest
from fastapi.testclient import TestClient

from agent.interfaces.rest.app import create_app
from agent.platform.config import Settings

WORKSPACE_ID = UUID("11111111-1111-7111-8111-111111111111")


@pytest.mark.integration
@pytest.mark.spec("ET-066")
def test_governance_console_renders_forge_and_sections(database_url: str) -> None:
    app = create_app(Settings(database_url=database_url, workspace_id=WORKSPACE_ID))
    client = TestClient(app)
    response = client.get("/governance")
    assert response.status_code == 200
    assert "FORGE" in response.text
    assert "Gouvernance" in response.text
    assert "Registre des sources" in response.text
    assert "autorisations AU-1 a AU-4" in response.text
    users = client.get("/users")
    assert users.status_code == 200
    assert "Utilisateurs et roles" in users.text
    assert "personne responsable" in users.text


@pytest.mark.integration
@pytest.mark.spec("ET-066")
def test_governance_api_requires_an_actor(database_url: str) -> None:
    app = create_app(Settings(database_url=database_url, workspace_id=WORKSPACE_ID))
    client = TestClient(app)
    response = client.post(
        "/api/governance/artifacts",
        json={
            "artifact_type": "source_registry",
            "artifact_key": "registry",
            "content": {"sources": []},
            "motif": "test",
        },
    )
    assert response.status_code == 401
