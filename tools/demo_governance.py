#!/usr/bin/env python3
"""Demonstration MS-1 lisible par le PO : lot de regles, registre, epinglage.

Cree des donnees dans une transaction, valide et approuve un lot, epingle une
demande, montre un refus et les quatre niveaux d'autorisation, puis annule tout.
"""

from __future__ import annotations

import os
from datetime import UTC, datetime, timedelta
from uuid import uuid4

from sqlalchemy import create_engine, text

from agent.governance.api import GovernanceDenied, GovernanceService
from agent.platform.clock import FixedClock

DEFAULT_URL = "postgresql+psycopg://agent:agent@localhost:55432/agent"


def template_content() -> dict[str, object]:
    return {
        "template": {"key": "note", "version": 1},
        "elements": [{"key": "objectifs", "mandatory": True, "on_missing": "block"}],
        "files": {},
    }


def control_content() -> dict[str, object]:
    return {
        "controls": [{"id": "CT-01", "definition": "Controle minimal", "mandatory_for": ["note"]}]
    }


def registry_content() -> dict[str, object]:
    return {
        "sources": [
            {
                "key": "inis",
                "kind": "inis",
                "priority": 1,
                "authorizations": {
                    "access": {"allowed": True},
                    "use": {"allowed": True, "purposes": ["deliverable_production"]},
                    "integration": {"allowed": True, "categories": ["public", "internal"]},
                    "diffusion": {"allowed": True, "recipients": ["internal"]},
                },
                "classification": "internal",
                "validity": {"default_period_days": None},
                "restrictions": [],
            }
        ]
    }


def rule_pack_content() -> dict[str, object]:
    return {
        "meta": {"key": "rules", "version": 1, "language": "fr", "title": "Regles exemple"},
        "deliverable_types": [
            {
                "key": "note",
                "template": {"key": "note", "version": 1},
                "allowed_formats": ["md"],
                "required_outputs": ["deliverable"],
                "approval": {"required": False, "approver": "responsible"},
                "mandatory_controls": ["CT-01"],
            }
        ],
        "quality": {"criteria": []},
        "priority_rules": [{"id": "prio-1", "order": ["inis"]}],
        "transformations": [{"id": "tf_date_iso", "type": "TF-04", "function": "normalize_date"}],
        "calculations": [],
        "rules": [{"id": "min_amount", "formula": 'dec(inputs.amount) >= dec("100")'}],
        "rule_tests": [
            {
                "id": "rt-1",
                "formula": 'dec(inputs.amount) >= dec("100")',
                "inputs": {"amount": "150"},
                "expected": True,
            }
        ],
    }


def main() -> int:
    url = os.environ.get("AGENT_DATABASE_URL", DEFAULT_URL)
    workspace, responsible_id, user_id, request_id = uuid4(), uuid4(), uuid4(), uuid4()
    now = datetime.now(UTC)
    effective = now + timedelta(days=1)
    engine = create_engine(url)
    with engine.connect() as connection:
        transaction = connection.begin()
        try:
            connection.execute(
                text("SELECT set_config('app.workspace_id', :value, true)"),
                {"value": str(workspace)},
            )
            connection.execute(text("SELECT set_config('app.role', 'system', true)"))
            connection.execute(
                text("INSERT INTO workspaces (id, name, created_at) VALUES (:id, :name, :at)"),
                {"id": workspace, "name": "Demonstration gouvernance", "at": now},
            )
            connection.execute(
                text(
                    """
                    INSERT INTO users (id, workspace_id, display_name, role, created_at)
                    VALUES (:id, :workspace_id, :name, :role, :at)
                    """
                ),
                {
                    "id": responsible_id,
                    "workspace_id": workspace,
                    "name": "Personne responsable",
                    "role": "responsible",
                    "at": now,
                },
            )
            connection.execute(
                text(
                    """
                    INSERT INTO users (id, workspace_id, display_name, role, created_at)
                    VALUES (:id, :workspace_id, :name, :role, :at)
                    """
                ),
                {
                    "id": user_id,
                    "workspace_id": workspace,
                    "name": "Utilisateur ordinaire",
                    "role": "user",
                    "at": now,
                },
            )
            connection.execute(
                text(
                    """
                    INSERT INTO requests
                      (id, workspace_id, author_id, original_text, state, created_at)
                    VALUES
                      (:id, :workspace_id, :author_id, 'Demande de demonstration',
                       'received', :at)
                    """
                ),
                {"id": request_id, "workspace_id": workspace, "author_id": user_id, "at": now},
            )

            service = GovernanceService(connection, workspace, clock=FixedClock(now))
            responsible = service.actor(responsible_id)
            ordinary = service.actor(user_id)

            print("1. Creation et approbation du modele et du catalogue de controles")
            for artifact_type, key, content in (
                ("template", "note", template_content()),
                ("control_catalog", "catalog", control_content()),
            ):
                draft = service.create_draft(responsible, artifact_type, key, content, "demo")
                assert service.validate(draft.id).ok
                service.approve(responsible, draft.id, effective, "decision DH-07")

            print("2. Creation du lot de regles, validation 9 etapes, approbation")
            rule = service.create_draft(
                responsible, "rule_pack", "rules", rule_pack_content(), "lot exemple"
            )
            report = service.validate(rule.id)
            print(f"   - etapes : {len(report.steps)}, resultat : {'OK' if report.ok else 'ECHEC'}")
            approved = service.approve(responsible, rule.id, effective, "decision DH-07")
            print(
                f"   - version {approved.version} approuvee, date d'effet {approved.effective_from}"
            )

            print("3. Creation et approbation du registre des sources")
            registry = service.create_draft(
                responsible, "source_registry", "registry", registry_content(), "registre demo"
            )
            assert service.validate(registry.id).ok
            service.approve(responsible, registry.id, effective, "decision DH-07")
            authorizations = service.source_authorizations(registry.id, "inis")
            print(f"   - niveaux : {', '.join(sorted(authorizations))}")

            print("4. Epinglage de la demande sur le lot approuve")
            service.pin_request(responsible, request_id, [rule.id])
            impact = service.impact(rule.id)
            print(f"   - demandes epinglees : {len(impact.pinned_requests)}")

            print("5. Tentative de modification par un utilisateur ordinaire")
            try:
                service.create_draft(
                    ordinary, "source_registry", "registry", registry_content(), "tentative"
                )
                print("   - ECHEC DE LA DEMONSTRATION : la modification a ete acceptee")
            except GovernanceDenied as exc:
                print(f"   - refusee : {exc}")

            print("6. Fin : transaction annulee, aucune donnee de demonstration conservee.")
            return 0
        finally:
            transaction.rollback()
            engine.dispose()


if __name__ == "__main__":
    raise SystemExit(main())
