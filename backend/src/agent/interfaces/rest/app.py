"""Squelette d'API FastAPI - MS-0, sans logique metier (DR-07).

FORGE est le nom de l'infrastructure et peut apparaitre dans le frontend
(Q-001). Les livrables et messages produits par le systeme restent neutres.
"""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, ConfigDict
from sqlalchemy import create_engine

from agent import __version__
from agent.interfaces.rest.governance import router as governance_router
from agent.platform.config import Settings, load_settings

FORGE_TITLE = "FORGE - Framework for Orchestrated Report Generation and Evaluation"

_LANDING = """<!doctype html>
<html lang="fr">
<head><meta charset="utf-8"><title>FORGE</title></head>
<body>
  <header><h1>FORGE</h1>
  <p>Framework for Orchestrated Report Generation and Evaluation</p></header>
  <main><p>Console de gouvernance : <a href="/governance">acceder</a>.</p></main>
</body>
</html>
"""


class Health(BaseModel):
    """Reponse de sante minimale ; ne revele aucune donnee interne."""

    model_config = ConfigDict(frozen=True)

    status: str
    version: str
    role: str
    environment: str


def create_app(settings: Settings | None = None) -> FastAPI:
    """Construit l'application ; la configuration est validee au demarrage."""
    current = settings if settings is not None else load_settings()
    app = FastAPI(title=FORGE_TITLE, version=__version__)
    app.state.settings = current
    app.state.engine = create_engine(current.database_url)
    app.include_router(governance_router)

    @app.get("/healthz", response_model=Health, tags=["system"])
    def healthz() -> Health:
        return Health(
            status="ok",
            version=__version__,
            role=current.role.value,
            environment=current.environment.value,
        )

    @app.get("/", response_class=HTMLResponse, include_in_schema=False)
    def landing() -> str:
        return _LANDING

    return app


app = create_app()
