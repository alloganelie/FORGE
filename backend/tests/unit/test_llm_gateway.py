"""ET-247 a ET-256 : passerelle LLM, rejeu strict, validation et journal."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

import pytest
from sqlalchemy import Connection, text

from agent.llm_gateway.api import (
    PROMPTS,
    LlmError,
    LlmFailure,
    LlmResponse,
    ReplayAdapter,
    run_task,
)
from agent.llm_gateway.core.schemas import Lt01Output
from agent.platform.clock import FixedClock

WORKSPACE_ID = UUID("11111111-1111-7111-8111-111111111111")
REQUEST_ID = UUID("44444444-4444-7444-8444-444444444444")
NOW = datetime(2026, 10, 23, 12, 0, tzinfo=UTC)


def valid_output() -> dict[str, object]:
    return {
        "candidate_type": "note",
        "objective": "Produire une note",
        "context": "contexte",
        "purpose": "but",
        "constraints": [],
        "parameters": [],
        "ambiguities": [],
        "multiple_deliverables_detected": False,
        "requested_format": "pdf",
    }


@pytest.mark.spec("ET-247")
@pytest.mark.spec("ET-250")
@pytest.mark.integration
def test_valid_replay_is_validated_and_logged(seeded: Connection) -> None:
    result = run_task(
        seeded,
        task_id="LT-01",
        request_id=REQUEST_ID,
        workspace_id=WORKSPACE_ID,
        inputs={"text": "Rapport 2024"},
        adapter=ReplayAdapter({"LT-01": LlmResponse(output=valid_output())}),
        output_model=Lt01Output,
        clock=FixedClock(NOW),
    )
    assert result.candidate_type == "note"
    row = seeded.execute(
        text("SELECT task_id, prompt_version, validation_outcome, stop_reason FROM llm_calls")
    ).one()
    assert row[0] == "LT-01"
    assert row[1] == "v1"
    assert row[2] == "valid"
    assert row[3] == "stop"


@pytest.mark.spec("ET-252")
@pytest.mark.integration
def test_invalid_output_is_a_typed_failure_and_is_logged(seeded: Connection) -> None:
    with pytest.raises(LlmError) as raised:
        run_task(
            seeded,
            task_id="LT-01",
            request_id=REQUEST_ID,
            workspace_id=WORKSPACE_ID,
            inputs={"text": "Rapport 2024"},
            adapter=ReplayAdapter({"LT-01": LlmResponse(output={"candidate_type": "note"})}),
            output_model=Lt01Output,
            clock=FixedClock(NOW),
        )
    assert raised.value.failure is LlmFailure.INVALID_OUTPUT
    outcome = seeded.execute(text("SELECT validation_outcome FROM llm_calls")).scalar_one()
    assert outcome == "invalid"


@pytest.mark.spec("ET-252")
@pytest.mark.integration
def test_refusal_is_a_typed_failure(seeded: Connection) -> None:
    with pytest.raises(LlmError) as raised:
        run_task(
            seeded,
            task_id="LT-01",
            request_id=REQUEST_ID,
            workspace_id=WORKSPACE_ID,
            inputs={"text": "Rapport 2024"},
            adapter=ReplayAdapter({"LT-01": LlmResponse(output={}, stop_reason="refusal")}),
            output_model=Lt01Output,
            clock=FixedClock(NOW),
        )
    assert raised.value.failure is LlmFailure.REFUSAL


@pytest.mark.spec("ET-247")
def test_missing_fixture_is_a_typed_failure() -> None:
    adapter = ReplayAdapter({})
    with pytest.raises(LlmError) as raised:
        adapter.complete("LT-01", {})
    assert raised.value.failure is LlmFailure.FIXTURE_MISSING


@pytest.mark.spec("ET-258")
def test_prompts_are_versioned_and_fingerprinted() -> None:
    for task in ("LT-01", "LT-02", "LT-10"):
        assert PROMPTS[task].version == "v1"
        assert len(PROMPTS[task].fingerprint) == 64
        assert "outil" in PROMPTS[task].anti_injection.lower()
