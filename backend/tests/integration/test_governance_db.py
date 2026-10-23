"""ET-053, ET-058, ET-059 : immuabilite, non-retroactivite et epinglage en base."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

import pytest
from sqlalchemy import Connection, text
from sqlalchemy.exc import DBAPIError, IntegrityError

from agent.governance.api import GovernanceService
from agent.governance.core.types import InvalidEffectiveDate
from agent.platform.clock import FixedClock

WORKSPACE_ID = UUID("11111111-1111-7111-8111-111111111111")
RESPONSIBLE_ID = UUID("22222222-2222-7222-8222-222222222222")
USER_ID = UUID("33333333-3333-7333-8333-333333333333")
REQUEST_ID = UUID("44444444-4444-7444-8444-444444444444")
NOW = datetime(2026, 10, 23, 12, 0, tzinfo=UTC)


def service(connection: Connection) -> GovernanceService:
    return GovernanceService(connection, WORKSPACE_ID, clock=FixedClock(NOW))


def registry() -> dict[str, object]:
    return {
        "sources": [
            {
                "key": "inis",
                "kind": "inis",
                "priority": 1,
                "authorizations": {
                    "access": {"allowed": True},
                    "use": {"allowed": True},
                    "integration": {"allowed": True},
                    "diffusion": {"allowed": True},
                },
                "classification": "internal",
                "validity": {},
                "restrictions": [],
            }
        ]
    }


def approved_registry(connection: Connection) -> object:
    gov = service(connection)
    actor = gov.actor(RESPONSIBLE_ID)
    version = gov.create_draft(actor, "source_registry", "registry", registry(), "creation")
    return gov.approve(actor, version.id, NOW + timedelta(days=1), "approbation")


@pytest.mark.integration
@pytest.mark.spec("ET-053")
def test_approved_artifact_content_is_immutable(seeded: Connection) -> None:
    version = approved_registry(seeded)
    with pytest.raises(DBAPIError, match="immuable"):
        with seeded.begin_nested():
            seeded.execute(
                text(
                    "UPDATE governance_artifact_versions SET content = '{}'::jsonb WHERE id = :id"
                ),
                {"id": version.id},
            )


@pytest.mark.integration
@pytest.mark.spec("ET-053")
def test_approved_artifact_cannot_be_deleted(seeded: Connection) -> None:
    version = approved_registry(seeded)
    with pytest.raises(DBAPIError, match=r"ajout seul|DELETE"):
        with seeded.begin_nested():
            seeded.execute(
                text("DELETE FROM governance_artifact_versions WHERE id = :id"),
                {"id": version.id},
            )


@pytest.mark.integration
@pytest.mark.spec("ET-058")
def test_approval_with_past_effective_date_is_refused(seeded: Connection) -> None:
    gov = service(seeded)
    actor = gov.actor(RESPONSIBLE_ID)
    version = gov.create_draft(actor, "source_registry", "registry", registry(), "creation")
    with pytest.raises(InvalidEffectiveDate):
        gov.approve(actor, version.id, NOW - timedelta(days=1), "retroactif")


@pytest.mark.integration
@pytest.mark.spec("ET-059")
def test_pins_are_append_only(seeded: Connection) -> None:
    version = approved_registry(seeded)
    gov = service(seeded)
    actor = gov.actor(RESPONSIBLE_ID)
    gov.pin_request(actor, REQUEST_ID, [version.id])
    with pytest.raises(DBAPIError, match="ajout seul"):
        with seeded.begin_nested():
            seeded.execute(
                text("UPDATE request_pins SET pinned_at = :at WHERE request_id = :request_id"),
                {"at": NOW, "request_id": REQUEST_ID},
            )


@pytest.mark.integration
@pytest.mark.spec("ET-070")
def test_only_one_active_responsible_per_workspace(seeded: Connection) -> None:
    with pytest.raises(IntegrityError):
        with seeded.begin_nested():
            seeded.execute(
                text(
                    """
                    INSERT INTO role_assignments
                      (id, workspace_id, user_id, role, valid_from)
                    VALUES (:id, :workspace_id, :user_id, 'responsible', :at)
                    """
                ),
                {
                    "id": uuid4(),
                    "workspace_id": WORKSPACE_ID,
                    "user_id": USER_ID,
                    "at": NOW,
                },
            )
            seeded.execute(
                text(
                    """
                    INSERT INTO role_assignments
                      (id, workspace_id, user_id, role, valid_from)
                    VALUES (:id, :workspace_id, :user_id, 'responsible', :at)
                    """
                ),
                {
                    "id": uuid4(),
                    "workspace_id": WORKSPACE_ID,
                    "user_id": RESPONSIBLE_ID,
                    "at": NOW,
                },
            )
