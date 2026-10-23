"""ET-353, ET-354, ET-355, ET-356, ET-372 : outil de tracabilite."""

from __future__ import annotations

from pathlib import Path

import pytest
from tools.spec_trace import (
    build_report,
    gate_errors,
    load_ids,
    load_transitions,
    milestone_criteria,
)


@pytest.mark.spec("ET-353")
@pytest.mark.spec("ET-372")
def test_all_spec_transitions_are_known_to_the_tool() -> None:
    ids = load_ids()
    transitions = load_transitions()
    assert set(transitions) == {key for key in ids if key.startswith("TR-")}
    assert len(transitions) == 54


@pytest.mark.spec("ET-354")
def test_milestone_scope_is_cumulative() -> None:
    assert milestone_criteria("MS-0") == []
    assert "CA-150" in milestone_criteria("MS-1")
    assert set(milestone_criteria("MS-1")) <= set(milestone_criteria("MS-2"))


@pytest.mark.spec("ET-353")
@pytest.mark.spec("ET-355")
@pytest.mark.spec("ET-356")
def test_ms0_report_passes_its_own_gates() -> None:
    report = build_report("MS-0", Path("build/junit.xml"))
    assert report.unknown_ids == []
    assert report.orphan_tests == []
    assert gate_errors(report, strict_requirements=False) == []
    assert report.summary()["transitions_covered"] == 54


@pytest.mark.spec("ET-372")
def test_dashboards_are_published_for_the_product_owner() -> None:
    for name in ("spec-trace.html", "spec-trace.md", "spec-trace.json"):
        path = Path("docs/reports") / name
        assert path.is_file(), name
    html = Path("docs/reports/spec-trace.html").read_text(encoding="utf-8")
    assert "Tableau de bord specification" in html
    assert "hors perimetre" in html
