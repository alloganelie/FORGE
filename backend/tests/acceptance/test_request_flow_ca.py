"""CA-001 a CA-020, CA-135 a CA-144, CA-189, CA-190 (TST-01, TST-02).

Tests d'acceptation du squelette demande -> faisabilite, avec passerelle LLM
en rejeu strict (aucun fournisseur externe).
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID

import pytest
from sqlalchemy import Connection, text

from agent.governance.api import GovernanceService
from agent.llm_gateway.api import LlmResponse, ReplayAdapter
from agent.platform.clock import FixedClock
from agent.requests.api import RequestDenied, RequestService

WORKSPACE_ID = UUID("11111111-1111-7111-8111-111111111111")
RESPONSIBLE_ID = UUID("22222222-2222-7222-8222-222222222222")
USER_ID = UUID("33333333-3333-7333-8333-333333333333")
AUDITOR_ID = UUID("55555555-5555-7555-8555-555555555555")
NOW = datetime(2026, 10, 23, 12, 0, tzinfo=UTC)
EFFECTIVE = NOW + timedelta(days=1)


def lt01(**overrides: Any) -> dict[str, Any]:
    value: dict[str, Any] = {
        "candidate_type": "note",
        "objective": "Produire une note",
        "context": "Suivi evaluation",
        "purpose": "Informar",
        "constraints": [],
        "parameters": [
            {
                "name": "period",
                "value": "2024",
                "justification_quote": "2024",
            }
        ],
        "ambiguities": [],
        "multiple_deliverables_detected": False,
        "requested_format": "pdf",
    }
    value.update(overrides)
    return value


def adapter(output: dict[str, Any], questions: dict[str, Any] | None = None) -> ReplayAdapter:
    responses: dict[str, LlmResponse] = {"LT-01": LlmResponse(output=output)}
    if questions is not None:
        responses["LT-02"] = LlmResponse(output=questions)
    return ReplayAdapter(responses)


def service(
    connection: Connection, output: dict[str, Any], questions: dict[str, Any] | None = None
) -> RequestService:
    return RequestService(
        connection,
        WORKSPACE_ID,
        clock=FixedClock(NOW),
        adapter=adapter(output, questions),
    )


def seed_governance(
    connection: Connection, *, source_access: bool = True, uncertain: bool = False
) -> None:
    gov = GovernanceService(connection, WORKSPACE_ID, clock=FixedClock(NOW))
    responsible = gov.actor(RESPONSIBLE_ID)
    template = gov.create_draft(
        responsible,
        "template",
        "note",
        {
            "template": {"key": "note", "version": 1},
            "elements": [{"key": "objectifs", "mandatory": True, "on_missing": "block"}],
            "files": {},
        },
        "modele",
    )
    gov.approve(responsible, template.id, EFFECTIVE, "modele")
    control = gov.create_draft(
        responsible,
        "control_catalog",
        "catalog",
        {"controls": [{"id": "CT-01", "definition": "Controle", "mandatory_for": ["note"]}]},
        "catalogue",
    )
    gov.approve(responsible, control.id, EFFECTIVE, "catalogue")
    rule = gov.create_draft(
        responsible,
        "rule_pack",
        "rules",
        {
            "meta": {"key": "rules", "version": 1, "language": "fr", "title": "Regles"},
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
        },
        "regles",
    )
    gov.approve(responsible, rule.id, EFFECTIVE, "regles")
    source = gov.create_draft(
        responsible,
        "source_registry",
        "registry",
        {
            "sources": [
                {
                    "key": "inis",
                    "kind": "inis",
                    "priority": 1,
                    "authorizations": {
                        "access": {"allowed": source_access},
                        "use": {"allowed": True, "uncertain": uncertain},
                        "integration": {"allowed": True},
                        "diffusion": {"allowed": True},
                    },
                    "classification": "protected",
                    "validity": {},
                    "restrictions": [],
                }
            ]
        },
        "registre",
    )
    gov.approve(responsible, source.id, EFFECTIVE, "registre")


def add_auditor(connection: Connection) -> None:
    connection.execute(
        text(
            """
            INSERT INTO users (id, workspace_id, display_name, role, created_at)
            VALUES (:id, :workspace_id, 'Auditeur', 'auditor', :at)
            ON CONFLICT (id) DO NOTHING
            """
        ),
        {"id": AUDITOR_ID, "workspace_id": WORKSPACE_ID, "at": NOW},
    )


@pytest.mark.ca("CA-001")
@pytest.mark.tst("TST-01")
@pytest.mark.integration
def test_ca001_request_is_recorded_with_original_text(seeded: Connection) -> None:
    text_value = "Rapport de suivi-evaluation 2024 en PDF"
    result = service(seeded, lt01()).submit(USER_ID, text_value)
    assert result.request is not None
    assert result.request.original_text == text_value
    assert result.request.author_id == USER_ID
    assert result.request.state == "received"
    assert result.request.id is not None


@pytest.mark.ca("CA-002")
@pytest.mark.tst("TST-01")
@pytest.mark.integration
def test_ca002_type_and_format_are_separate(seeded: Connection) -> None:
    result = service(seeded, lt01()).submit(USER_ID, "Rapport 2024 en PDF")
    assert result.request is not None
    assert result.request.deliverable_type == "note"
    assert result.request.target_format == "pdf"


@pytest.mark.ca("CA-003")
@pytest.mark.tst("TST-01")
@pytest.mark.integration
def test_ca003_resolved_parameter_does_not_create_question(seeded: Connection) -> None:
    result = service(seeded, lt01()).submit(USER_ID, "Rapport 2024 en PDF")
    assert result.questions == ()
    assert result.request is not None
    assert result.request.state == "received"


@pytest.mark.ca("CA-004")
@pytest.mark.tst("TST-01")
@pytest.mark.integration
def test_ca004_unauthorized_submitter_is_refused(seeded: Connection) -> None:
    add_auditor(seeded)
    with pytest.raises(RequestDenied):
        service(seeded, lt01()).submit(AUDITOR_ID, "Rapport 2024 en PDF")
    count = seeded.execute(
        text("SELECT COUNT(*) FROM requests WHERE author_id = :id"), {"id": AUDITOR_ID}
    ).scalar_one()
    assert count == 0


@pytest.mark.ca("CA-005")
@pytest.mark.tst("TST-01")
@pytest.mark.integration
def test_ca005_non_significant_ambiguity_does_not_question(seeded: Connection) -> None:
    output = lt01(ambiguities=[{"parameter": "tone", "reason": "style", "blocking": False}])
    result = service(seeded, output).submit(USER_ID, "Rapport 2024 en PDF")
    assert result.questions == ()
    assert result.request is not None
    assert result.request.state == "received"


@pytest.mark.ca("CA-006")
@pytest.mark.tst("TST-01")
@pytest.mark.integration
def test_ca006_significant_ambiguity_creates_targeted_question(seeded: Connection) -> None:
    output = lt01(ambiguities=[{"parameter": "perimetre", "reason": "portee", "blocking": True}])
    result = service(seeded, output).submit(USER_ID, "Rapport 2024 en PDF")
    assert result.request is not None
    assert result.request.state == "clarifying"
    assert len(result.questions) == 1
    assert result.questions[0].why_needed
    assert "perimetre" in result.questions[0].question_text


@pytest.mark.ca("CA-007")
@pytest.mark.tst("TST-01")
@pytest.mark.integration
def test_ca007_blocking_questions_come_first(seeded: Connection) -> None:
    output = lt01(
        ambiguities=[
            {"parameter": "perimetre", "reason": "portee", "blocking": True},
            {"parameter": "periode", "reason": "annee", "blocking": True},
            {"parameter": "ton", "reason": "style", "blocking": False},
        ]
    )
    result = service(seeded, output).submit(USER_ID, "Rapport 2024 en PDF")
    assert len(result.questions) <= 5
    assert all(question.blocking for question in result.questions)


@pytest.mark.ca("CA-008")
@pytest.mark.tst("TST-01")
@pytest.mark.integration
def test_ca008_unanswered_choice_stays_pending(seeded: Connection) -> None:
    output = lt01(ambiguities=[{"parameter": "perimetre", "reason": "portee", "blocking": True}])
    result = service(seeded, output).submit(USER_ID, "Rapport 2024 en PDF")
    assert result.request is not None
    status = service(seeded, output).status(result.request.id, USER_ID)
    assert status.expected
    assert status.request_state == "clarifying"


@pytest.mark.ca("CA-009")
@pytest.mark.tst("TST-01")
@pytest.mark.integration
def test_ca009_punctual_instruction_does_not_change_rules(seeded: Connection) -> None:
    seed_governance(seeded)
    before = seeded.execute(text("SELECT COUNT(*) FROM governance_artifact_versions")).scalar_one()
    output = lt01(constraints=["utiliser le ton neutre pour cette demande"])
    service(seeded, output).submit(USER_ID, "Rapport 2024 en PDF, ton neutre")
    after = seeded.execute(text("SELECT COUNT(*) FROM governance_artifact_versions")).scalar_one()
    assert before == after


@pytest.mark.ca("CA-010")
@pytest.mark.tst("TST-01")
@pytest.mark.integration
def test_ca010_multiple_deliverables_are_detected_not_split(seeded: Connection) -> None:
    output = lt01(multiple_deliverables_detected=True)
    result = service(seeded, output).submit(USER_ID, "Deux rapports 2024 en PDF")
    assert result.request is None
    assert result.split is not None
    count = seeded.execute(
        text("SELECT COUNT(*) FROM requests WHERE author_id = :author"), {"author": USER_ID}
    ).scalar_one()
    assert count == 0


@pytest.mark.ca("CA-011")
@pytest.mark.tst("TST-02")
@pytest.mark.integration
def test_ca011_missing_model_blocks(seeded: Connection) -> None:
    svc = service(seeded, lt01())
    result = svc.submit(USER_ID, "Rapport 2024 en PDF")
    assert result.request is not None
    report = svc.assess_feasibility(result.request.id, USER_ID)
    assert report.outcome == "blocked"
    assert any(part.dimension == "model" and part.verdict == "blocked" for part in report.parts)


@pytest.mark.ca("CA-012")
@pytest.mark.tst("TST-02")
@pytest.mark.integration
def test_ca012_diagnostic_covers_all_dimensions(seeded: Connection) -> None:
    seed_governance(seeded)
    svc = service(seeded, lt01())
    result = svc.submit(USER_ID, "Rapport 2024 en PDF")
    assert result.request is not None
    report = svc.assess_feasibility(result.request.id, USER_ID)
    assert report.outcome == "realizable"
    assert {part.dimension for part in report.parts} == {
        "model",
        "rules",
        "information",
        "authorizations",
        "requirements",
        "contradictions",
        "preconditions",
    }


@pytest.mark.ca("CA-013")
@pytest.mark.tst("TST-02")
@pytest.mark.integration
def test_ca013_missing_condition_blocks_with_reason(seeded: Connection) -> None:
    svc = service(seeded, lt01())
    result = svc.submit(USER_ID, "Rapport 2024 en PDF")
    assert result.request is not None
    report = svc.assess_feasibility(result.request.id, USER_ID)
    assert report.outcome == "blocked"
    assert report.reason_for(False)


@pytest.mark.ca("CA-014")
@pytest.mark.tst("TST-02")
@pytest.mark.integration
def test_ca014_diagnostic_remains_available_after_block(seeded: Connection) -> None:
    svc = service(seeded, lt01())
    result = svc.submit(USER_ID, "Rapport 2024 en PDF")
    assert result.request is not None
    report = svc.assess_feasibility(result.request.id, USER_ID)
    status = svc.status(result.request.id, USER_ID)
    assert report.outcome == "blocked"
    assert status.request_state == "blocked"
    assert status.reasons


@pytest.mark.ca("CA-015")
@pytest.mark.tst("TST-02")
@pytest.mark.integration
def test_ca015_diagnostic_distinguishes_outcomes(seeded: Connection) -> None:
    seed_governance(seeded)
    svc = service(seeded, lt01())
    result = svc.submit(USER_ID, "Rapport 2024 en PDF")
    assert result.request is not None
    report = svc.assess_feasibility(result.request.id, USER_ID)
    assert report.outcome == "realizable"
    assert all(part.verdict for part in report.parts)


@pytest.mark.ca("CA-016")
@pytest.mark.tst("TST-02")
@pytest.mark.integration
def test_ca016_versions_are_pinned_at_feasibility(seeded: Connection) -> None:
    seed_governance(seeded)
    svc = service(seeded, lt01())
    result = svc.submit(USER_ID, "Rapport 2024 en PDF")
    assert result.request is not None
    report = svc.assess_feasibility(result.request.id, USER_ID)
    pins = svc.governance.pins_for_request(result.request.id)
    assert len(report.pinned_version_ids) >= 3
    assert len(pins) >= 3


@pytest.mark.ca("CA-017")
@pytest.mark.tst("TST-02")
@pytest.mark.integration
def test_ca017_uncertain_rights_suspend_operation(seeded: Connection) -> None:
    seed_governance(seeded, uncertain=True)
    svc = service(seeded, lt01())
    result = svc.submit(USER_ID, "Rapport 2024 en PDF")
    assert result.request is not None
    report = svc.assess_feasibility(result.request.id, USER_ID)
    assert report.outcome == "suspended"
    assert svc.status(result.request.id, USER_ID).request_state == "awaiting_decision"


@pytest.mark.ca("CA-018")
@pytest.mark.tst("TST-02")
@pytest.mark.integration
def test_ca018_rule_change_does_not_change_pins(seeded: Connection) -> None:
    seed_governance(seeded)
    svc = service(seeded, lt01())
    result = svc.submit(USER_ID, "Rapport 2024 en PDF")
    assert result.request is not None
    svc.assess_feasibility(result.request.id, USER_ID)
    before = [pin.version_id for pin in svc.governance.pins_for_request(result.request.id)]
    gov = svc.governance
    responsible = gov.actor(RESPONSIBLE_ID)
    new_rule = gov.create_draft(
        responsible,
        "rule_pack",
        "rules",
        {
            "meta": {"key": "rules", "version": 2, "language": "fr", "title": "Regles"},
            "deliverable_types": [
                {
                    "key": "note",
                    "template": {"key": "note", "version": 1},
                    "allowed_formats": ["pdf"],
                    "mandatory_controls": ["CT-01"],
                }
            ],
            "quality": {},
            "priority_rules": [{"id": "p", "order": ["inis"]}],
            "transformations": [],
            "calculations": [],
            "rules": [],
        },
        "nouvelle regle",
    )
    gov.approve(responsible, new_rule.id, EFFECTIVE + timedelta(days=1), "nouvelle regle")
    after = [pin.version_id for pin in svc.governance.pins_for_request(result.request.id)]
    assert after == before


@pytest.mark.ca("CA-019")
@pytest.mark.tst("TST-02")
@pytest.mark.integration
def test_ca019_diagnostic_only_does_not_produce_or_pin(seeded: Connection) -> None:
    seed_governance(seeded)
    svc = service(seeded, lt01())
    result = svc.submit(USER_ID, "Rapport 2024 en PDF", diagnostic_only=True)
    assert result.request is not None
    report = svc.assess_feasibility(result.request.id, USER_ID, diagnostic_only=True)
    assert report.outcome == "realizable"
    assert svc.governance.pins_for_request(result.request.id) == ()


@pytest.mark.ca("CA-020")
@pytest.mark.tst("TST-02")
@pytest.mark.integration
def test_ca020_protected_reason_is_general_for_unauthorized_actor(seeded: Connection) -> None:
    seed_governance(seeded, source_access=False)
    svc = service(seeded, lt01())
    result = svc.submit(USER_ID, "Rapport 2024 en PDF")
    assert result.request is not None
    report = svc.assess_feasibility(result.request.id, USER_ID)
    public = svc.reason_for(report, USER_ID)
    detail = svc.reason_for(report, RESPONSIBLE_ID)
    assert public
    assert "inis" not in public
    assert "inis" in detail


@pytest.mark.ca("CA-135")
@pytest.mark.tst("TST-14")
@pytest.mark.integration
def test_ca135_status_contains_tracking_fields(seeded: Connection) -> None:
    svc = service(seeded, lt01())
    result = svc.submit(USER_ID, "Rapport 2024 en PDF")
    assert result.request is not None
    status = svc.status(result.request.id, USER_ID)
    assert status.steps_done
    assert status.current_step
    assert status.next_action
    assert status.statuses.keys() == {"C", "A", "D", "V"}
    assert status.provisional is True


@pytest.mark.ca("CA-136")
@pytest.mark.tst("TST-14")
@pytest.mark.integration
def test_ca136_items_distinguish_states(seeded: Connection) -> None:
    svc = service(seeded, lt01())
    result = svc.submit(USER_ID, "Rapport 2024 en PDF")
    assert result.request is not None
    for key, state in (
        ("a", "done"),
        ("b", "suspended"),
        ("c", "blocked"),
        ("d", "awaiting_decision"),
        ("e", "finalized"),
    ):
        svc.add_tracking_item(result.request.id, key, key, state)
    status = svc.status(result.request.id, USER_ID)
    assert {item.state for item in status.items} == {
        "done",
        "suspended",
        "blocked",
        "awaiting_decision",
        "finalized",
    }


@pytest.mark.ca("CA-137")
@pytest.mark.tst("TST-14")
@pytest.mark.integration
def test_ca137_protected_information_is_not_exposed(seeded: Connection) -> None:
    seed_governance(seeded, source_access=False)
    svc = service(seeded, lt01())
    result = svc.submit(USER_ID, "Rapport 2024 en PDF")
    assert result.request is not None
    svc.assess_feasibility(result.request.id, USER_ID)
    status = svc.status(result.request.id, USER_ID)
    assert all("inis" not in reason for reason in status.reasons)


@pytest.mark.ca("CA-138")
@pytest.mark.tst("TST-14")
@pytest.mark.integration
def test_ca138_reason_depends_on_rights(seeded: Connection) -> None:
    seed_governance(seeded, source_access=False)
    svc = service(seeded, lt01())
    result = svc.submit(USER_ID, "Rapport 2024 en PDF")
    assert result.request is not None
    report = svc.assess_feasibility(result.request.id, USER_ID)
    assert svc.reason_for(report, USER_ID) != svc.reason_for(report, RESPONSIBLE_ID)


@pytest.mark.ca("CA-139")
@pytest.mark.tst("TST-14")
@pytest.mark.integration
def test_ca139_status_does_not_announce_success(seeded: Connection) -> None:
    seed_governance(seeded)
    svc = service(seeded, lt01())
    result = svc.submit(USER_ID, "Rapport 2024 en PDF")
    assert result.request is not None
    svc.assess_feasibility(result.request.id, USER_ID)
    status = svc.status(result.request.id, USER_ID)
    assert "termine" not in status.message.lower()
    assert "finalise" not in status.message.lower()


@pytest.mark.ca("CA-140")
@pytest.mark.tst("TST-14")
@pytest.mark.integration
def test_ca140_status_uses_functional_states(seeded: Connection) -> None:
    seed_governance(seeded)
    svc = service(seeded, lt01())
    result = svc.submit(USER_ID, "Rapport 2024 en PDF")
    assert result.request is not None
    svc.assess_feasibility(result.request.id, USER_ID)
    status = svc.status(result.request.id, USER_ID)
    assert "En production" in status.current_step
    assert "mobilisation" not in status.message.lower()


@pytest.mark.ca("CA-142")
@pytest.mark.tst("TST-01")
@pytest.mark.integration
def test_ca142_natural_language_request_needs_no_internal_knowledge(seeded: Connection) -> None:
    result = service(seeded, lt01()).submit(
        USER_ID, "Je voudrais un rapport de suivi-evaluation 2024 en PDF, simplement."
    )
    assert result.request is not None
    assert result.request.state == "received"


@pytest.mark.ca("CA-143")
@pytest.mark.tst("TST-14")
@pytest.mark.integration
def test_ca143_history_is_returned(seeded: Connection) -> None:
    svc = service(seeded, lt01())
    result = svc.submit(USER_ID, "Rapport 2024 en PDF")
    assert result.request is not None
    history = svc.history(result.request.id, USER_ID)
    assert history
    assert any(message["template_key"] == "request_received" for message in history)


@pytest.mark.ca("CA-144")
@pytest.mark.tst("TST-14")
@pytest.mark.integration
def test_ca144_public_reason_has_no_technical_jargon(seeded: Connection) -> None:
    seed_governance(seeded, source_access=False)
    svc = service(seeded, lt01())
    result = svc.submit(USER_ID, "Rapport 2024 en PDF")
    assert result.request is not None
    report = svc.assess_feasibility(result.request.id, USER_ID)
    assert "MB-" not in svc.reason_for(report, USER_ID)


@pytest.mark.ca("CA-189")
@pytest.mark.tst("TST-01")
@pytest.mark.integration
def test_ca189_confirmed_split_creates_two_independent_requests(seeded: Connection) -> None:
    result = service(seeded, lt01(multiple_deliverables_detected=True)).submit(
        USER_ID, "Deux rapports 2024 en PDF"
    )
    assert result.split is not None
    created = service(seeded, lt01()).confirm_split(result.split.id, USER_ID)
    assert len(created) == 2
    assert created[0].id != created[1].id
    assert all(item.state == "received" for item in created)


@pytest.mark.ca("CA-190")
@pytest.mark.tst("TST-01")
@pytest.mark.integration
def test_ca190_user_answer_is_candidate_qi02(seeded: Connection) -> None:
    output = lt01(ambiguities=[{"parameter": "scope", "reason": "portee", "blocking": True}])
    svc = service(seeded, output)
    result = svc.submit(USER_ID, "Rapport 2024 en PDF")
    assert result.request is not None
    svc.clarify(result.request.id, USER_ID, {"scope": "national"})
    row = seeded.execute(
        text(
            "SELECT quality_status FROM request_parameters "
            "WHERE request_id = :id AND name = 'scope'"
        ),
        {"id": result.request.id},
    ).one()
    assert row[0] == "candidate"
