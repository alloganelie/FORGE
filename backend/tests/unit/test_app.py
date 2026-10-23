"""ET-002 : squelette FastAPI et nom FORGE reserve au frontend (Q-001)."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from agent.interfaces.rest.app import FORGE_TITLE, create_app
from agent.platform.config import Settings


@pytest.mark.spec("ET-002")
def test_health_endpoint() -> None:
    client = TestClient(create_app(Settings()))
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


@pytest.mark.spec("ET-002")
def test_landing_displays_forge() -> None:
    client = TestClient(create_app(Settings()))
    response = client.get("/")
    assert response.status_code == 200
    assert "FORGE" in response.text
    assert "Framework for Orchestrated Report Generation and Evaluation" in response.text


@pytest.mark.spec("ET-002")
def test_openapi_contract_is_exposed() -> None:
    app = create_app(Settings())
    schema = app.openapi()
    assert schema["info"]["title"] == FORGE_TITLE
    assert "/healthz" in schema["paths"]
