"""Console minimale de gouvernance et API JSON (SCR-15, SCR-17).

L'interface ne contient aucune regle metier : elle traduit les formulaires en
appels au service de gouvernance. FORGE est le nom de l'infrastructure et
apparait dans l'en-tete de la console (Q-001).
"""

from __future__ import annotations

import html
import json
from collections.abc import Iterator
from dataclasses import asdict
from datetime import datetime
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from sqlalchemy import Connection, text

from agent.governance.api import (
    ArtifactStatus,
    ArtifactType,
    ArtifactVersion,
    GovernanceDenied,
    GovernanceService,
    GovernanceValidationFailure,
    InvalidEffectiveDate,
    InvalidTransition,
)
from agent.platform.config import Settings

router = APIRouter()

FORGE_BANNER = """<header class="banner">
  <div><strong class="mark">FORGE</strong>
  <span>Framework for Orchestrated Report Generation and Evaluation</span></div>
  <nav><a href="/">Accueil</a><a href="/governance">Gouvernance</a><a href="/users">Utilisateurs</a></nav>
</header>"""

STYLE = """<style>
body{font-family:Segoe UI,Arial,sans-serif;margin:0;background:#f6f8fa;color:#17212b}
.banner{background:#17212b;color:#fff;padding:14px 24px;display:flex;justify-content:space-between;gap:20px;align-items:center;flex-wrap:wrap}
.banner .mark{font-size:1.3rem;letter-spacing:.08em}
.banner span{color:#c9d4df;margin-left:10px;font-size:.9rem}
.banner a{color:#fff;margin-left:14px;text-decoration:none}
main{max-width:1100px;margin:0 auto;padding:24px}
h1{font-size:1.5rem}h2{margin-top:30px}
table{width:100%;border-collapse:collapse;background:#fff;margin:10px 0 20px}
th,td{border:1px solid #d9e1e8;padding:7px 9px;text-align:left;font-size:.9rem;vertical-align:top}
th{background:#eef2f5}code{background:#eef2f5;padding:1px 4px;border-radius:4px}
.badge{display:inline-block;padding:1px 8px;border-radius:999px;font-size:.78rem;background:#eef2f5}
.badge.approved{background:#e7f6ec;color:#176b36}.badge.retired{background:#f2f5f7;color:#7b8794}
form{background:#fff;border:1px solid #d9e1e8;border-radius:8px;padding:14px;margin:12px 0}
label{display:block;margin-top:8px;font-size:.85rem}input,select,textarea{width:100%;padding:6px;margin-top:3px;border:1px solid #c7d2dc;border-radius:5px;box-sizing:border-box}
textarea{min-height:110px;font-family:Consolas,monospace;font-size:.8rem}
button{margin-top:10px;padding:7px 12px;border:0;border-radius:5px;background:#1f5f8b;color:#fff;cursor:pointer}
button.secondary{background:#5b6b7b}.hint{color:#5b6b7b;font-size:.85rem}
</style>"""


class DraftBody(BaseModel):
    artifact_type: str
    artifact_key: str
    content: dict[str, Any]
    motif: str = ""


class ApproveBody(BaseModel):
    effective_from: datetime
    reason: str


class PinBody(BaseModel):
    version_ids: list[UUID]


def _service(request: Request, connection: Connection) -> GovernanceService:
    settings: Settings = request.app.state.settings
    return GovernanceService(connection, settings.workspace_id)


def get_connection(request: Request) -> Iterator[Connection]:
    settings: Settings = request.app.state.settings
    engine = request.app.state.engine
    with engine.begin() as connection:
        connection.execute(
            text("SELECT set_config('app.workspace_id', :value, true)"),
            {"value": str(settings.workspace_id)},
        )
        connection.execute(text("SELECT set_config('app.role', 'system', true)"))
        yield connection


def _actor_id(value: str | None) -> UUID:
    if value is None:
        raise HTTPException(status_code=401, detail="En-tete X-Actor-Id requis.")
    try:
        return UUID(value)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="X-Actor-Id invalide.") from exc


def _artifact_dict(version: ArtifactVersion) -> dict[str, Any]:
    payload = asdict(version)
    payload["artifact_type"] = version.artifact_type.value
    payload["status"] = version.status.value
    payload["id"] = str(version.id)
    payload["workspace_id"] = str(version.workspace_id)
    payload["created_by"] = str(version.created_by)
    payload["approved_by_decision"] = (
        str(version.approved_by_decision) if version.approved_by_decision else None
    )
    return payload


def _guard(call: Any) -> Any:
    try:
        return call()
    except GovernanceDenied as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except GovernanceValidationFailure as exc:
        raise HTTPException(
            status_code=422,
            detail={"message": str(exc), "report": asdict(exc.report)},
        ) from exc
    except InvalidEffectiveDate as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except InvalidTransition as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.get("/api/governance/artifacts")
def api_list_artifacts(
    request: Request, connection: Connection = Depends(get_connection)
) -> list[dict[str, Any]]:
    service = _service(request, connection)
    return [_artifact_dict(item) for item in service.list_artifacts()]


@router.post("/api/governance/artifacts", status_code=201)
def api_create_artifact(
    body: DraftBody,
    request: Request,
    connection: Connection = Depends(get_connection),
    actor_header: str | None = Header(default=None, alias="X-Actor-Id"),
) -> dict[str, Any]:
    service = _service(request, connection)
    actor = _guard(lambda: service.actor(_actor_id(actor_header)))
    version = _guard(
        lambda: service.create_draft(
            actor, body.artifact_type, body.artifact_key, body.content, body.motif
        )
    )
    return _artifact_dict(version)


@router.post("/api/governance/artifacts/{version_id}/validate")
def api_validate(
    version_id: UUID,
    request: Request,
    connection: Connection = Depends(get_connection),
) -> dict[str, Any]:
    service = _service(request, connection)
    report = _guard(lambda: service.validate(version_id))
    return asdict(report)


@router.post("/api/governance/artifacts/{version_id}/approve")
def api_approve(
    version_id: UUID,
    body: ApproveBody,
    request: Request,
    connection: Connection = Depends(get_connection),
    actor_header: str | None = Header(default=None, alias="X-Actor-Id"),
) -> dict[str, Any]:
    service = _service(request, connection)
    actor = _guard(lambda: service.actor(_actor_id(actor_header)))
    version = _guard(lambda: service.approve(actor, version_id, body.effective_from, body.reason))
    return _artifact_dict(version)


@router.post("/api/requests/{request_id}/pins")
def api_pin(
    request_id: UUID,
    body: PinBody,
    request: Request,
    connection: Connection = Depends(get_connection),
    actor_header: str | None = Header(default=None, alias="X-Actor-Id"),
) -> list[dict[str, Any]]:
    service = _service(request, connection)
    actor = _guard(lambda: service.actor(_actor_id(actor_header)))
    pins = _guard(lambda: service.pin_request(actor, request_id, tuple(body.version_ids)))
    return [asdict(pin) for pin in pins]


@router.get("/api/governance/sources/{version_id}/{source_key}")
def api_source_authorizations(
    version_id: UUID,
    source_key: str,
    request: Request,
    connection: Connection = Depends(get_connection),
) -> dict[str, Any]:
    service = _service(request, connection)
    return dict(_guard(lambda: service.source_authorizations(version_id, source_key)))


def _render_governance(
    actors: tuple[Any, ...],
    artifacts: tuple[ArtifactVersion, ...],
    service: GovernanceService,
) -> str:
    actor_options = "".join(
        f'<option value="{html.escape(str(actor.id))}">{html.escape(actor.display_name)} '
        f"({html.escape(actor.role)})</option>"
        for actor in actors
    )
    rows = (
        "".join(
            f"<tr><td>{html.escape(str(item.id))}</td>"
            f"<td>{html.escape(item.artifact_type.value)}</td>"
            f"<td>{html.escape(item.artifact_key)}</td><td>{item.version}</td>"
            f'<td><span class="badge {html.escape(item.status.value)}">'
            f"{html.escape(item.status.value)}</span></td>"
            f"<td>{html.escape(item.effective_from or '-')}</td>"
            f'<td><button class="secondary" onclick="validateArtifact(\'{html.escape(str(item.id))}\')">'
            f"Valider</button> <button onclick=\"approveArtifact('{html.escape(str(item.id))}')\">"
            f"Approuver</button></td></tr>"
            for item in artifacts
        )
        or "<tr><td colspan='7'>Aucun artefact.</td></tr>"
    )

    source_rows: list[str] = []
    for item in artifacts:
        if (
            item.artifact_type is not ArtifactType.SOURCE_REGISTRY
            or item.status is not ArtifactStatus.APPROVED
        ):
            continue
        for source in item.content.get("sources", []):
            if not isinstance(source, dict):
                continue
            key = str(source.get("key", ""))
            try:
                auth = service.source_authorizations(item.id, key)
            except GovernanceDenied:
                continue
            cells = "".join(
                f"<td>{html.escape(json.dumps(auth.get(level, {}), ensure_ascii=False))}</td>"
                for level in ("access", "use", "integration", "diffusion")
            )
            source_rows.append(f"<tr><td>{html.escape(key)}</td>{cells}</tr>")
    sources = "".join(source_rows) or "<tr><td colspan='5'>Aucune source approuvee.</td></tr>"

    script = """<script>
async function call(path, method, body) {
  const actor = document.getElementById('actor').value;
  const headers = {'Content-Type': 'application/json', 'X-Actor-Id': actor};
  const response = await fetch(path, {method, headers, body: body ? JSON.stringify(body) : undefined});
  const text = await response.text();
  if (!response.ok) { alert(text); return; }
  location.reload();
}
function createArtifact(event) {
  event.preventDefault();
  const content = JSON.parse(document.getElementById('content').value);
  call('/api/governance/artifacts', 'POST', {
    artifact_type: document.getElementById('artifact_type').value,
    artifact_key: document.getElementById('artifact_key').value,
    content: content,
    motif: document.getElementById('motif').value
  });
}
function validateArtifact(id) {
  call('/api/governance/artifacts/' + id + '/validate', 'POST', null);
}
function approveArtifact(id) {
  const date = prompt('Date d effet (ISO 8601, ex. 2026-11-01T00:00:00Z):');
  const reason = prompt('Motif de la decision DH-07 :');
  if (!date || !reason) return;
  call('/api/governance/artifacts/' + id + '/approve', 'POST', {effective_from: date, reason});
}
</script>"""

    return f"""<!doctype html><html lang="fr"><head><meta charset="utf-8">
<title>FORGE - Gouvernance</title>{STYLE}</head><body>{FORGE_BANNER}
<main><h1>Gouvernance</h1>
<p class="hint">SCR-15 : registre, lots de regles, modeles, catalogue. L'acteur est choisi
pour la demonstration ; en production, son identite vient d'OIDC et son role de la base.</p>
<form onsubmit="createArtifact(event)">
<label>Acteur (la base determine son role)</label><select id="actor">{actor_options}</select>
<label>Type</label><select id="artifact_type"><option>rule_pack</option><option>template</option>
<option>source_registry</option><option>control_catalog</option></select>
<label>Cle</label><input id="artifact_key" required>
<label>Contenu JSON</label><textarea id="content" required>{{}}</textarea>
<label>Motif</label><input id="motif" required>
<button type="submit">Creer un brouillon</button></form>
<h2>Artefacts versionnes</h2>
<table><thead><tr><th>Id</th><th>Type</th><th>Cle</th><th>Version</th><th>Statut</th>
<th>Date d'effet</th><th>Actions</th></tr></thead><tbody>{rows}</tbody></table>
<h2>Registre des sources - autorisations AU-1 a AU-4</h2>
<table><thead><tr><th>Source</th><th>Acces</th><th>Usage</th><th>Integration</th><th>Diffusion</th></tr></thead>
<tbody>{sources}</tbody></table>
{script}</main></body></html>"""


@router.get("/governance", response_class=HTMLResponse)
def governance_page(request: Request, connection: Connection = Depends(get_connection)) -> str:
    service = _service(request, connection)
    return _render_governance(service.list_actors(), service.list_artifacts(), service)


@router.get("/users", response_class=HTMLResponse)
def users_page(request: Request, connection: Connection = Depends(get_connection)) -> str:
    service = _service(request, connection)
    actors = service.list_actors()
    responsible = sum(1 for actor in actors if actor.role == "responsible")
    rows = (
        "".join(
            f"<tr><td>{html.escape(str(actor.id))}</td><td>{html.escape(actor.display_name)}</td>"
            f"<td>{html.escape(actor.role)}</td></tr>"
            for actor in actors
        )
        or "<tr><td colspan='3'>Aucun utilisateur.</td></tr>"
    )
    return f"""<!doctype html><html lang="fr"><head><meta charset="utf-8">
<title>FORGE - Utilisateurs</title>{STYLE}</head><body>{FORGE_BANNER}
<main><h1>Utilisateurs et roles</h1>
<p class="hint">SCR-17 : une seule personne responsable active est attendue.</p>
<p>Personne(s) responsable(s) active(s) : <strong>{responsible}</strong></p>
<table><thead><tr><th>Id</th><th>Nom</th><th>Role</th></tr></thead><tbody>{rows}</tbody></table>
</main></body></html>"""
