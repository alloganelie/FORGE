#!/usr/bin/env python3
"""Prepare une base locale de demonstration pour la console de gouvernance.

Rattache des utilisateurs et des artefacts approuves a l'espace de travail
11111111-1111-7111-8111-111111111111. Aucune donnee reelle.
"""

from __future__ import annotations

import os
from datetime import UTC, datetime, timedelta
from uuid import UUID

from sqlalchemy import create_engine, text

from agent.governance.api import GovernanceService
from agent.platform.clock import FixedClock
from demo_governance import control_content, registry_content, rule_pack_content, template_content

DEFAULT_URL = "postgresql+psycopg://agent:agent@localhost:55432/agent"
WORKSPACE = UUID("11111111-1111-7111-8111-111111111111")
RESPONSIBLE = UUID("22222222-2222-7222-8222-222222222222")
USER = UUID("33333333-3333-7333-8333-333333333333")
REQUEST = UUID("44444444-4444-7444-8444-444444444444")


def main() -> int:
    url = os.environ.get("AGENT_DATABASE_URL", DEFAULT_URL)
    now = datetime.now(UTC)
    effective = now + timedelta(days=1)
    engine = create_engine(url)
    with engine.begin() as connection:
        connection.execute(
            text("SELECT set_config('app.workspace_id', :value, true)"),
            {"value": str(WORKSPACE)},
        )
        connection.execute(text("SELECT set_config('app.role', 'system', true)"))
        connection.execute(
            text(
                """
                INSERT INTO workspaces (id, name, created_at)
                VALUES (:id, :name, :at)
                ON CONFLICT (id) DO NOTHING
                """
            ),
            {"id": WORKSPACE, "name": "Demonstration gouvernance", "at": now},
        )
        for user_id, name, role in (
            (RESPONSIBLE, "Personne responsable", "responsible"),
            (USER, "Utilisateur ordinaire", "user"),
        ):
            connection.execute(
                text(
                    """
                    INSERT INTO users (id, workspace_id, display_name, role, created_at)
                    VALUES (:id, :workspace_id, :name, :role, :at)
                    ON CONFLICT (id) DO NOTHING
                    """
                ),
                {
                    "id": user_id,
                    "workspace_id": WORKSPACE,
                    "name": name,
                    "role": role,
                    "at": now,
                },
            )
        connection.execute(
            text(
                """
                INSERT INTO requests (id, workspace_id, author_id, original_text, state, created_at)
                VALUES (:id, :workspace_id, :author_id, 'Demande de demonstration', 'received', :at)
                ON CONFLICT (id) DO NOTHING
                """
            ),
            {"id": REQUEST, "workspace_id": WORKSPACE, "author_id": USER, "at": now},
        )

        service = GovernanceService(connection, WORKSPACE, clock=FixedClock(now))
        actor = service.actor(RESPONSIBLE)
        for artifact_type, key, content in (
            ("template", "note", template_content()),
            ("control_catalog", "catalog", control_content()),
            ("source_registry", "registry", registry_content()),
            ("rule_pack", "rules", rule_pack_content()),
        ):
            draft = service.create_draft(actor, artifact_type, key, content, "demo console")
            report = service.validate(draft.id)
            if not report.ok:
                print(f"Validation en echec pour {artifact_type} : {report}")
                return 1
            service.approve(actor, draft.id, effective, "decision DH-07 (demo)")
        latest_rule = max(
            (item for item in service.list_artifacts() if item.artifact_type == "rule_pack"),
            key=lambda item: item.version,
        )
        service.pin_request(actor, REQUEST, [latest_rule.id])
        print(f"Espace de travail : {WORKSPACE}")
        print(f"Personne responsable : {RESPONSIBLE}")
        print(f"Utilisateur ordinaire : {USER}")
        print(f"Demande de demonstration : {REQUEST}")
        print("Lancer la console avec :")
        print(f"  AGENT_WORKSPACE_ID={WORKSPACE}")
        print(
            "  .\\.venv\\Scripts\\python.exe -m uvicorn agent.interfaces.rest.app:app --port 8000"
        )
    engine.dispose()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
