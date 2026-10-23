#!/usr/bin/env python3
"""Demonstration MS-2 : demande -> clarification -> faisabilite -> statut.

Les reponses LLM sont rejouees ; aucun fournisseur externe n'est appele.
Toutes les donnees sont annulees a la fin.
"""

from __future__ import annotations

import os
from datetime import UTC, datetime, timedelta
from uuid import uuid4

from sqlalchemy import create_engine, text

from agent.governance.api import GovernanceService
from agent.llm_gateway.api import LlmResponse, ReplayAdapter
from agent.platform.clock import FixedClock
from agent.requests.api import RequestService
from demo_governance import control_content, registry_content, template_content

DEFAULT_URL = "postgresql+psycopg://agent:agent@localhost:55432/agent"


def rule_content() -> dict[str, object]:
    return {
        "meta": {"key": "rules", "version": 1, "language": "fr", "title": "Regles demo"},
        "deliverable_types": [
            {
                "key": "note",
                "template": {"key": "note", "version": 1},
                "allowed_formats": ["pdf", "md"],
                "mandatory_controls": ["CT-01"],
            }
        ],
        "quality": {},
        "priority_rules": [{"id": "p", "order": ["inis"]}],
        "transformations": [],
        "calculations": [],
        "rules": [],
    }


def main() -> int:
    url = os.environ.get("AGENT_DATABASE_URL", DEFAULT_URL)
    workspace, responsible_id, user_id = uuid4(), uuid4(), uuid4()
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
                {"id": workspace, "name": "Demonstration demande", "at": now},
            )
            for user, name, role in (
                (responsible_id, "Personne responsable", "responsible"),
                (user_id, "Utilisateur", "user"),
            ):
                connection.execute(
                    text(
                        "INSERT INTO users (id, workspace_id, display_name, role, created_at) "
                        "VALUES (:id, :workspace_id, :name, :role, :at)"
                    ),
                    {"id": user, "workspace_id": workspace, "name": name, "role": role, "at": now},
                )

            gov = GovernanceService(connection, workspace, clock=FixedClock(now))
            responsible = gov.actor(responsible_id)
            for artifact_type, key, content in (
                ("template", "note", template_content()),
                ("control_catalog", "catalog", control_content()),
                ("rule_pack", "rules", rule_content()),
                ("source_registry", "registry", registry_content()),
            ):
                draft = gov.create_draft(responsible, artifact_type, key, content, "demo")
                assert gov.validate(draft.id).ok
                gov.approve(responsible, draft.id, effective, "decision DH-07")

            adapter = ReplayAdapter(
                {
                    "LT-01": LlmResponse(
                        output={
                            "candidate_type": "note",
                            "objective": "Produire une note de suivi",
                            "context": "suivi evaluation",
                            "purpose": "informer",
                            "constraints": [],
                            "parameters": [
                                {
                                    "name": "period",
                                    "value": "2024",
                                    "justification_quote": "2024",
                                }
                            ],
                            "ambiguities": [
                                {"parameter": "scope", "reason": "perimetre", "blocking": True}
                            ],
                            "multiple_deliverables_detected": False,
                            "requested_format": "pdf",
                        }
                    ),
                    "LT-02": LlmResponse(
                        output={
                            "questions": [
                                {
                                    "parameter": "scope",
                                    "text": "Quel est le perimetre geographique ?",
                                    "why_needed": (
                                        "Le perimetre conditionne les donnees du livrable."
                                    ),
                                }
                            ]
                        }
                    ),
                }
            )
            requests = RequestService(connection, workspace, clock=FixedClock(now), adapter=adapter)
            submitted = requests.submit(user_id, "Rapport de suivi-evaluation 2024 en PDF")
            assert submitted.request is not None
            request = submitted.request
            print(f"1. Demande recue : {request.id}")
            print(
                f"   - etat : {request.state}, type : {request.deliverable_type}, "
                f"format : {request.target_format}"
            )
            print(f"2. Questions : {len(submitted.questions)}")
            for question in submitted.questions:
                print(f"   - {question.question_text} ({question.why_needed})")
            request = requests.clarify(request.id, user_id, {"scope": "national"})
            print(f"3. Reponse enregistree : etat {request.state}")
            report = requests.assess_feasibility(request.id, user_id)
            print(f"4. Diagnostic : {report.outcome}, dimensions : {len(report.parts)}")
            pins = requests.governance.pins_for_request(request.id)
            print(f"5. Versions epinglees : {len(pins)}")
            status = requests.status(request.id, user_id)
            print(f"6. Statut : {status.current_step}")
            print(f"   - etapes terminees : {', '.join(status.steps_done)}")
            print(f"   - prochaine action : {status.next_action}")
            print(f"   - axes separes : {status.statuses}")
            print("7. Fin : transaction annulee, aucune donnee conservee.")
            return 0
        finally:
            transaction.rollback()
            engine.dispose()


if __name__ == "__main__":
    raise SystemExit(main())
