"""ET-017, DC-05 : les types enumeres sont generes et alignes sur la specification."""

from __future__ import annotations

from pathlib import Path

import pytest
from tools.gen_enums import build_enums
from tools.gen_enums import main as gen_enums_main
from tools.spec import load

from agent.lifecycle.core import states


@pytest.mark.spec("ET-017")
@pytest.mark.spec("DC-05")
def test_each_sql_enum_has_a_python_enum_with_same_values() -> None:
    definitions = build_enums()
    for definition in definitions:
        enum_class = getattr(states, definition.class_name)
        assert [member.value for member in enum_class] == list(definition.values)


@pytest.mark.spec("ET-017")
def test_every_st_identifier_from_spec_is_mapped() -> None:
    functional = load("F")
    expected: set[str] = set()
    for ident in functional.rows:
        if ident.startswith("ST-"):
            expected.add(ident)
    mapped = {spec_id for mapping in states.AXIS_STATE_IDS.values() for spec_id in mapping.values()}
    assert expected == mapped


@pytest.mark.spec("ET-017")
def test_state_counts_match_functional_axes() -> None:
    assert len(states.RequestState) == 10
    assert len(states.ConformityState) == 4
    assert len(states.ApprovalState) == 5
    assert len(states.DiffusionState) == 3
    assert len(states.VersionState) == 4
    assert len(states.ElementState) == 7
    assert len(states.QualityStatus) == 7
    assert len(states.LcStatus) == 5
    assert len(states.ControlOutcome) == 4
    assert len(states.AnomalyClass) == 3
    assert len(states.DecisionType) == 10
    assert len(states.AuthLevel) == 4


@pytest.mark.spec("ET-017")
def test_generated_files_are_up_to_date() -> None:
    assert gen_enums_main(["--check"]) == 0


@pytest.mark.spec("ET-017")
def test_sql_enum_file_matches_generated_values() -> None:
    sql = Path("backend/migrations/sql/0001_enums.sql").read_text(encoding="utf-8")
    for definition in build_enums():
        assert f"CREATE TYPE {definition.sql_name} AS ENUM" in sql
        for value in definition.values:
            assert f"'{value}'" in sql
