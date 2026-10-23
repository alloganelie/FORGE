"""RB-097, RB-104, GV-02, ET-057 : roles, dates, epinglage, impact."""

from __future__ import annotations

from uuid import UUID

import pytest

from agent.anomalies.api import UnknownAutofix, apply_autofix
from agent.governance.core.approval import require_draft, require_future_effective_date
from agent.governance.core.impact import ImpactReport
from agent.governance.core.pinning import PinError, require_approved, resolve_artifact
from agent.governance.core.roles import require_responsible
from agent.governance.core.types import (
    Actor,
    ArtifactStatus,
    ArtifactType,
    ArtifactVersion,
    GovernanceDenied,
    InvalidEffectiveDate,
    InvalidTransition,
)

ACTOR_ID = UUID("22222222-2222-7222-8222-222222222222")
WORKSPACE_ID = UUID("11111111-1111-7111-8111-111111111111")


def version(
    identifier: int, status: ArtifactStatus, artifact_type: ArtifactType = ArtifactType.RULE_PACK
) -> ArtifactVersion:
    return ArtifactVersion(
        id=UUID(f"00000000-0000-7000-8000-{identifier:012d}"),
        workspace_id=WORKSPACE_ID,
        artifact_type=artifact_type,
        artifact_key="rules",
        version=identifier,
        content={},
        content_hash="0" * 64,
        status=status,
        effective_from=None,
        created_by=ACTOR_ID,
        created_at="2026-10-23T12:00:00+00:00",
    )


@pytest.mark.spec("RB-097")
def test_only_responsible_can_write() -> None:
    with pytest.raises(GovernanceDenied):
        require_responsible(Actor(ACTOR_ID, "user"))
    require_responsible(Actor(ACTOR_ID, "responsible"))


@pytest.mark.spec("RB-104")
def test_effective_date_must_be_future() -> None:
    with pytest.raises(InvalidEffectiveDate):
        require_future_effective_date("2026-10-23T11:00:00+00:00", "2026-10-23T12:00:00+00:00")
    require_future_effective_date("2026-10-24T12:00:00+00:00", "2026-10-23T12:00:00+00:00")


@pytest.mark.spec("GV-02")
def test_only_draft_can_be_approved() -> None:
    with pytest.raises(InvalidTransition):
        require_draft(ArtifactStatus.APPROVED)
    require_draft(ArtifactStatus.DRAFT)


@pytest.mark.spec("ET-059")
def test_only_approved_version_can_be_pinned() -> None:
    with pytest.raises(PinError):
        require_approved(version(1, ArtifactStatus.DRAFT))
    require_approved(version(1, ArtifactStatus.APPROVED))


@pytest.mark.spec("ET-060")
def test_resolution_uses_pin_not_latest() -> None:
    first = version(1, ArtifactStatus.RETIRED)
    second = version(2, ArtifactStatus.APPROVED)
    resolved = resolve_artifact("rule_pack", (first,), (first, second))
    assert resolved.id == first.id


@pytest.mark.spec("ET-057")
def test_impact_is_serialisable() -> None:
    report = ImpactReport(replaced_version_id=ACTOR_ID, pinned_requests=(WORKSPACE_ID,))
    payload = report.as_dict()
    assert payload["pinned_requests"] == [str(WORKSPACE_ID)]
    assert report.ready is True


@pytest.mark.spec("ET-064")
def test_named_autofix_is_allowlisted_and_unknown_is_refused() -> None:
    assert apply_autofix("fix_typographic_quotes", "\u201ctexte\u201d") == '"texte"'
    assert apply_autofix("normalize_date", "23/10/2026") == "2026-10-23"
    with pytest.raises(UnknownAutofix):
        apply_autofix("exec_shell", "rm -rf /")
