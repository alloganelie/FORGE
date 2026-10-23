"""CA-150 a CA-153, TST-15 : gouvernance (lots, registre, versions, impact).

Les tests portent sur le service de gouvernance et une base PostgreSQL reelle.
Ils sont ecrits avant l'implementation (demarche rouge -> vert).
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID

import pytest
from sqlalchemy import Connection

from agent.governance.api import GovernanceDenied, GovernanceService
from agent.platform.clock import FixedClock

WORKSPACE_ID = UUID("11111111-1111-7111-8111-111111111111")
RESPONSIBLE_ID = UUID("22222222-2222-7222-8222-222222222222")
USER_ID = UUID("33333333-3333-7333-8333-333333333333")
REQUEST_ID = UUID("44444444-4444-7444-8444-444444444444")
NOW = datetime(2026, 10, 23, 12, 0, tzinfo=UTC)
EFFECTIVE = NOW + timedelta(days=1)


def source_registry(version: int = 1) -> dict[str, Any]:
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
        ],
        "meta": {"key": "registry", "version": version},
    }


def rule_pack(version: int = 1, *, with_contradiction: bool = False) -> dict[str, Any]:
    content: dict[str, Any] = {
        "meta": {"key": "rules", "version": version, "language": "fr", "title": "Regles"},
        "deliverable_types": [
            {
                "key": "note",
                "template": {"key": "note", "version": 1},
                "allowed_formats": ["md"],
                "required_outputs": ["deliverable"],
                "approval": {"required": False, "approver": "responsible"},
                "mandatory_controls": ["CT-01"],
                "significant_elements": {"rule": "facts_figures_references_calculations_decisions"},
            }
        ],
        "quality": {
            "criteria": ["source"],
            "validity_rules": [],
            "allow_unverified_in_deliverable": False,
        },
        "priority_rules": [{"id": "prio-1", "order": ["inis", "documents"]}],
        "transformations": [{"id": "tf_date_iso", "type": "TF-04", "function": "normalize_date"}],
        "calculations": [
            {
                "id": "calc_rate",
                "inputs": [{"name": "n", "unit": "person"}],
                "formula": 'rnd(mul(dec(inputs.n), dec("100")), 1, "half_up")',
                "rounding": {"places": 1, "mode": "half_up"},
                "unit_out": "percent",
            }
        ],
        "controls_config": {"CT-01": {"mandatory": True}},
        "rules": [
            {
                "id": "min_amount",
                "description": "Montant minimal",
                "formula": 'dec(inputs.amount) >= dec("100")',
            }
        ],
        "rule_tests": [
            {
                "id": "rt-1",
                "formula": 'dec(inputs.amount) >= dec("100")',
                "inputs": {"amount": "150"},
                "expected": True,
            }
        ],
        "examples": [],
    }
    if with_contradiction:
        content["examples"] = [
            {
                "id": "ex-1",
                "rule_id": "min_amount",
                "inputs": {"amount": "50"},
                "claimed_outcome": True,
            }
        ]
    return content


def make_service(connection: Connection) -> GovernanceService:
    return GovernanceService(connection, WORKSPACE_ID, clock=FixedClock(NOW))


def seed_dependencies(service: GovernanceService, responsible: object) -> None:
    template = service.create_draft(
        responsible,  # type: ignore[arg-type]
        "template",
        "note",
        {
            "template": {"key": "note", "version": 1},
            "elements": [{"key": "sec_objectives", "mandatory": True, "on_missing": "block"}],
            "files": {},
        },
        "modele minimal",
    )
    assert service.validate(template.id).ok
    service.approve(responsible, template.id, EFFECTIVE, "approbation modele")  # type: ignore[arg-type]
    control = service.create_draft(
        responsible,  # type: ignore[arg-type]
        "control_catalog",
        "catalog",
        {
            "controls": [
                {"id": "CT-01", "definition": "Controle minimal", "mandatory_for": ["note"]}
            ]
        },
        "catalogue minimal",
    )
    assert service.validate(control.id).ok
    service.approve(responsible, control.id, EFFECTIVE, "approbation catalogue")  # type: ignore[arg-type]


@pytest.mark.ca("CA-150")
@pytest.mark.tst("TST-15")
@pytest.mark.integration
@pytest.mark.spec("RF-250")
@pytest.mark.spec("RF-252")
def test_ca150_only_responsible_changes_registry_and_pins_stay_on_old_version(
    seeded: Connection,
) -> None:
    service = make_service(seeded)
    responsible = service.actor(RESPONSIBLE_ID)
    ordinary = service.actor(USER_ID)

    first = service.create_draft(
        responsible, "source_registry", "registry", source_registry(1), "creation"
    )
    assert service.validate(first.id).ok
    approved_first = service.approve(responsible, first.id, EFFECTIVE, "approbation initiale")
    assert approved_first.status == "approved"

    service.pin_request(responsible, REQUEST_ID, [first.id])

    with pytest.raises(GovernanceDenied):
        service.create_draft(
            ordinary, "source_registry", "registry", source_registry(2), "tentative"
        )

    second = service.create_draft(
        responsible, "source_registry", "registry", source_registry(2), "mise a jour"
    )
    assert service.validate(second.id).ok
    service.approve(responsible, second.id, EFFECTIVE + timedelta(days=1), "mise a jour")

    pins = service.pins_for_request(REQUEST_ID)
    assert [pin.version_id for pin in pins] == [first.id]
    assert service.get_artifact(first.id).status == "retired"


@pytest.mark.ca("CA-151")
@pytest.mark.tst("TST-15")
@pytest.mark.integration
@pytest.mark.spec("RF-251")
def test_ca151_source_exposes_four_authorization_levels(seeded: Connection) -> None:
    service = make_service(seeded)
    responsible = service.actor(RESPONSIBLE_ID)
    version = service.create_draft(
        responsible, "source_registry", "registry", source_registry(1), "registre"
    )
    service.approve(responsible, version.id, EFFECTIVE, "approbation")

    authorizations = service.source_authorizations(version.id, "inis")
    assert set(authorizations) == {"access", "use", "integration", "diffusion"}
    assert authorizations["diffusion"] == {"allowed": True, "recipients": ["internal"]}


@pytest.mark.ca("CA-152")
@pytest.mark.tst("TST-15")
@pytest.mark.integration
@pytest.mark.spec("RF-254")
@pytest.mark.spec("RF-258")
@pytest.mark.spec("RF-259")
def test_ca152_rule_and_template_changes_require_responsible_and_leave_pins(
    seeded: Connection,
) -> None:
    service = make_service(seeded)
    responsible = service.actor(RESPONSIBLE_ID)
    ordinary = service.actor(USER_ID)

    seed_dependencies(service, responsible)
    rule_first = service.create_draft(
        responsible, "rule_pack", "rules", rule_pack(1), "regles initiales"
    )
    assert service.validate(rule_first.id).ok
    service.approve(responsible, rule_first.id, EFFECTIVE, "approbation")
    service.pin_request(responsible, REQUEST_ID, [rule_first.id])

    with pytest.raises(GovernanceDenied):
        service.create_draft(ordinary, "rule_pack", "rules", rule_pack(2), "tentative")
    with pytest.raises(GovernanceDenied):
        service.create_draft(
            ordinary,
            "template",
            "note",
            {
                "template": {"key": "note", "version": 2},
                "elements": [{"key": "sec_objectives", "mandatory": True, "on_missing": "block"}],
                "files": {},
            },
            "tentative",
        )

    rule_second = service.create_draft(
        responsible, "rule_pack", "rules", rule_pack(2), "nouvelle version"
    )
    assert service.validate(rule_second.id).ok
    service.approve(responsible, rule_second.id, EFFECTIVE + timedelta(days=1), "approbation")

    assert [pin.version_id for pin in service.pins_for_request(REQUEST_ID)] == [rule_first.id]
    assert service.get_artifact(rule_first.id).content["meta"]["version"] == 1
    assert service.get_artifact(rule_first.id).status == "retired"


@pytest.mark.ca("CA-153")
@pytest.mark.tst("TST-15")
@pytest.mark.integration
@pytest.mark.spec("RF-255")
@pytest.mark.spec("RF-256")
def test_ca153_rule_prevails_over_contradicting_example(seeded: Connection) -> None:
    service = make_service(seeded)
    responsible = service.actor(RESPONSIBLE_ID)
    seed_dependencies(service, responsible)
    version = service.create_draft(
        responsible,
        "rule_pack",
        "rules",
        rule_pack(1, with_contradiction=True),
        "regles avec exemple contradictoire",
    )

    report = service.validate(version.id)
    assert report.ok
    assert any(
        observation.code == "example_contradicts_rule" for observation in report.observations
    )
    assert service.evaluate_rule(version.id, "min_amount", {"amount": "50"}) is False
    assert service.evaluate_rule(version.id, "min_amount", {"amount": "150"}) is True


@pytest.mark.tst("TST-15")
@pytest.mark.integration
@pytest.mark.spec("ET-055")
@pytest.mark.spec("ET-057")
@pytest.mark.spec("ET-058")
@pytest.mark.spec("ET-059")
def test_tst15_rule_pack_end_to_end(seeded: Connection) -> None:
    service = make_service(seeded)
    responsible = service.actor(RESPONSIBLE_ID)
    seed_dependencies(service, responsible)
    version = service.create_draft(
        responsible, "rule_pack", "rules", rule_pack(1), "lot de regles exemple"
    )

    report = service.validate(version.id)
    assert len(report.steps) == 9
    assert all(step.status != "failed" for step in report.steps)
    assert report.step(9) is not None

    approved = service.approve(responsible, version.id, EFFECTIVE, "decision DH-07")
    assert approved.status == "approved"
    assert approved.approved_by_decision is not None

    pins = service.pin_request(responsible, REQUEST_ID, [version.id])
    assert [pin.version_id for pin in pins] == [version.id]
    impact = service.impact(version.id)
    assert REQUEST_ID in impact.pinned_requests
