"""ET-054 a ET-058 : pipeline de validation en 9 etapes."""

from __future__ import annotations

from uuid import UUID

import pytest

from agent.governance.core.impact import ImpactReport
from agent.governance.core.types import ArtifactType
from agent.governance.core.validation import (
    ValidationContext,
    run_pipeline,
    step_cycles,
    step_forbidden,
    step_schema,
)
from agent.governance.infra.formulas import CelFormulaEngine
from agent.governance.infra.schemas import JsonSchemaStore

VERSION_ID = UUID("77777777-7777-7777-8777-777777777777")


def context(**overrides: object) -> ValidationContext:
    values: dict[str, object] = {
        "schema_validator": JsonSchemaStore(),
        "formula_engine": CelFormulaEngine(),
        "templates": {"note": {}},
        "controls": {"CT-01": {}},
        "transformations": frozenset({"tf_date_iso"}),
        "units": frozenset({"percent", "person"}),
    }
    values.update(overrides)
    return ValidationContext(**values)  # type: ignore[arg-type]


def source_registry(missing: str | None = None) -> dict[str, object]:
    authorizations: dict[str, object] = {
        "access": {"allowed": True},
        "use": {"allowed": True},
        "integration": {"allowed": True},
        "diffusion": {"allowed": True},
    }
    if missing:
        del authorizations[missing]
    return {
        "sources": [
            {
                "key": "inis",
                "kind": "inis",
                "priority": 1,
                "authorizations": authorizations,
                "classification": "internal",
                "validity": {},
                "restrictions": [],
            }
        ]
    }


@pytest.mark.spec("ET-054")
def test_schema_requires_all_four_authorizations() -> None:
    report = step_schema(ArtifactType.SOURCE_REGISTRY, source_registry("diffusion"), context())
    assert report.status == "failed"
    assert any("diffusion" in finding.message for finding in report.findings)


@pytest.mark.spec("ET-055")
def test_cycle_in_template_is_rejected() -> None:
    content = {
        "template": {"key": "note", "version": 1},
        "elements": [
            {"key": "a", "mandatory": True, "on_missing": "block", "depends_on": ["b"]},
            {"key": "b", "mandatory": True, "on_missing": "block", "depends_on": ["a"]},
        ],
    }
    report = step_cycles(ArtifactType.TEMPLATE, content, context())
    assert report.status == "failed"
    assert any(finding.code == "cycle" for finding in report.findings)


@pytest.mark.spec("ET-055")
def test_default_value_is_forbidden() -> None:
    content = {
        "template": {"key": "note", "version": 1},
        "elements": [
            {
                "key": "a",
                "mandatory": True,
                "on_missing": "block",
                "needed_information": [{"field_key": "x", "default_value": "1"}],
            }
        ],
    }
    report = step_forbidden(ArtifactType.TEMPLATE, content, context())
    assert report.status == "failed"
    assert any(finding.code == "valeur_par_defaut" for finding in report.findings)


@pytest.mark.spec("ET-056")
def test_rule_test_is_executed_and_failure_rejects() -> None:
    content = {
        "meta": {"key": "rules", "version": 1, "language": "fr", "title": "Regles"},
        "deliverable_types": [],
        "quality": {},
        "priority_rules": [],
        "transformations": [],
        "calculations": [],
        "rules": [],
        "rule_tests": [
            {
                "id": "rt-1",
                "formula": 'dec(inputs.amount) >= dec("100")',
                "inputs": {"amount": "50"},
                "expected": True,
            }
        ],
    }
    report = run_pipeline(ArtifactType.RULE_PACK, content, context(), steps=(7,))
    assert not report.ok
    assert report.steps[0].findings[0].code == "test_echoue"


@pytest.mark.spec("ET-056")
@pytest.mark.spec("RF-256")
def test_contradicting_example_becomes_an_observation_not_a_failure() -> None:
    content = {
        "meta": {"key": "rules", "version": 1, "language": "fr", "title": "Regles"},
        "deliverable_types": [],
        "quality": {},
        "priority_rules": [],
        "transformations": [],
        "calculations": [],
        "rules": [{"id": "min_amount", "formula": 'dec(inputs.amount) >= dec("100")'}],
        "examples": [
            {
                "id": "ex-1",
                "rule_id": "min_amount",
                "inputs": {"amount": "50"},
                "claimed_outcome": True,
            }
        ],
    }
    report = run_pipeline(ArtifactType.RULE_PACK, content, context(), steps=(7,))
    assert report.ok
    assert report.observations[0].code == "example_contradicts_rule"


@pytest.mark.spec("ET-057")
def test_impact_step_publishes_pinned_requests() -> None:
    impact = ImpactReport(replaced_version_id=VERSION_ID, pinned_requests=(VERSION_ID,))
    report = run_pipeline(
        ArtifactType.RULE_PACK,
        {"rules": []},
        context(impact=impact),
        steps=(9,),
    )
    assert report.ok
    assert report.steps[0].details["pinned_requests"] == [str(VERSION_ID)]


@pytest.mark.spec("ET-055")
def test_reference_to_unknown_template_fails() -> None:
    content = {
        "meta": {"key": "rules", "version": 1, "language": "fr", "title": "Regles"},
        "deliverable_types": [
            {
                "key": "note",
                "template": {"key": "missing", "version": 1},
                "allowed_formats": ["md"],
                "mandatory_controls": [],
            }
        ],
        "quality": {},
        "priority_rules": [],
        "transformations": [],
        "calculations": [],
        "rules": [],
    }
    report = run_pipeline(ArtifactType.RULE_PACK, content, context(), steps=(2,))
    assert not report.ok
    assert report.steps[0].findings[0].code == "reference_inconnue"


@pytest.mark.spec("ET-064")
def test_autofix_function_must_be_registered() -> None:
    content = {
        "meta": {"key": "rules", "version": 1, "language": "fr", "title": "Regles"},
        "deliverable_types": [],
        "quality": {},
        "priority_rules": [],
        "transformations": [],
        "calculations": [],
        "rules": [],
        "autofix": [{"id": "af-1", "function": "exec_shell", "params": {}}],
    }
    report = run_pipeline(
        ArtifactType.RULE_PACK,
        content,
        context(autofix_functions=frozenset({"normalize_date"})),
        steps=(5,),
    )
    assert not report.ok
    assert report.steps[0].findings[0].code == "autofix_inconnue"
