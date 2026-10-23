"""Criteres de sortie MS-0 observables par le Product Owner.

Aucun CA metier n'appartient a MS-0 ; ces tests verifient les livrables
transverses (tableau de bord, image, transitions) sans base de donnees.
"""

from __future__ import annotations

from pathlib import Path

import pytest


@pytest.mark.spec("ET-372")
def test_spec_trace_dashboard_exists_and_is_readable() -> None:
    path = Path("docs/reports/spec-trace.html")
    assert path.is_file()
    content = path.read_text(encoding="utf-8")
    assert "Tableau de bord specification" in content
    assert "Criteres du jalon" in content
    assert "hors perimetre" in content


@pytest.mark.spec("ET-353")
def test_spec_trace_json_contains_all_transitions() -> None:
    import json

    data = json.loads(Path("docs/reports/spec-trace.json").read_text(encoding="utf-8"))
    transitions = data["transitions"]
    assert len(transitions) == 54
    assert all(entry["covered_by"] for entry in transitions.values())


@pytest.mark.spec("ET-009")
def test_image_is_multi_stage_and_non_root() -> None:
    dockerfile = Path("ops/Dockerfile").read_text(encoding="utf-8")
    assert " AS builder" in dockerfile
    assert " AS runtime" in dockerfile
    assert "USER 10001:10001" in dockerfile
    assert "ENTRYPOINT" in dockerfile


@pytest.mark.spec("ET-035")
def test_transition_yaml_is_versioned() -> None:
    files = sorted(Path("rulepacks/state_machines").glob("*.yaml"))
    assert len(files) == 6
    assert all("generated_from" in path.read_text(encoding="utf-8") for path in files)
