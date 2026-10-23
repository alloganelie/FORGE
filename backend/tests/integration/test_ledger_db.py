"""ET-021, ET-022, ET-026 : journal chaine contre PostgreSQL reel."""

from __future__ import annotations

import json
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime
from uuid import UUID, uuid4

import pytest
from sqlalchemy import Connection, text
from sqlalchemy.exc import DBAPIError

from agent.ledger.api import append_event, verify_chain, write_checkpoint

REQUEST_ID = UUID("44444444-4444-7444-8444-444444444444")
WORKSPACE_ID = UUID("11111111-1111-7111-8111-111111111111")
USER_ID = UUID("22222222-2222-7222-8222-222222222222")
AT = datetime(2026, 10, 23, 12, 0, tzinfo=UTC)


def _append(connection: Connection, number: int) -> object:
    return append_event(
        connection,
        workspace_id=WORKSPACE_ID,
        request_id=REQUEST_ID,
        event_type="TestEvent",
        payload={"number": number},
        actor_type="human",
        actor_id=USER_ID,
        at=AT,
    )


@pytest.mark.integration
@pytest.mark.spec("ET-022")
def test_append_builds_contiguous_chain(seeded: Connection) -> None:
    first = _append(seeded, 1)
    second = _append(seeded, 2)
    third = _append(seeded, 3)
    assert (first.request_seq, second.request_seq, third.request_seq) == (1, 2, 3)
    assert second.prev_hash == first.self_hash
    assert third.prev_hash == second.self_hash
    result = verify_chain(seeded, WORKSPACE_ID)
    assert result.ok, result.errors
    assert result.checked == 3


@pytest.mark.integration
@pytest.mark.spec("ET-021")
def test_ledger_update_delete_and_truncate_are_refused(seeded: Connection) -> None:
    _append(seeded, 1)
    for statement in (
        "UPDATE ledger_events SET payload = '{}'",
        "DELETE FROM ledger_events",
        "TRUNCATE ledger_events",
    ):
        with pytest.raises(DBAPIError, match="ajout seul"), seeded.begin_nested():
            seeded.execute(text(statement))


@pytest.mark.integration
@pytest.mark.spec("ET-022")
def test_wrong_sequence_or_previous_hash_is_refused(seeded: Connection) -> None:
    first = _append(seeded, 1)
    with pytest.raises(DBAPIError, match="Chaine invalide"), seeded.begin_nested():
        seeded.execute(
            text(
                """
                    INSERT INTO ledger_events
                      (workspace_id, request_id, request_seq, event_type, payload,
                       actor_type, actor_id, at, prev_hash, self_hash)
                    VALUES
                      (:workspace_id, :request_id, 5, 'Bad', '{}'::jsonb,
                       'human', :actor_id, :at, :prev_hash, :self_hash)
                    """
            ),
            {
                "workspace_id": WORKSPACE_ID,
                "request_id": REQUEST_ID,
                "actor_id": USER_ID,
                "at": AT,
                "prev_hash": first.self_hash,
                "self_hash": "0" * 64,
            },
        )


@pytest.mark.integration
@pytest.mark.spec("ET-022")
def test_verify_detects_a_forged_self_hash(seeded: Connection) -> None:
    first = _append(seeded, 1)
    with seeded.begin_nested():
        seeded.execute(
            text(
                """
                INSERT INTO ledger_events
                  (workspace_id, request_id, request_seq, event_type, payload,
                   actor_type, actor_id, at, prev_hash, self_hash)
                VALUES
                  (:workspace_id, :request_id, 2, 'Forged', CAST(:payload AS jsonb),
                   'human', :actor_id, :at, :prev_hash, :self_hash)
                """
            ),
            {
                "workspace_id": WORKSPACE_ID,
                "request_id": REQUEST_ID,
                "payload": json.dumps({"number": 2}),
                "actor_id": USER_ID,
                "at": AT,
                "prev_hash": first.self_hash,
                "self_hash": "f" * 64,
            },
        )
        result = verify_chain(seeded, WORKSPACE_ID)
        assert not result.ok
        assert any("self_hash" in error for error in result.errors)


@pytest.mark.integration
@pytest.mark.spec("ET-025")
def test_checkpoint_records_verification(seeded: Connection) -> None:
    _append(seeded, 1)
    checkpoint_id = UUID("55555555-5555-7555-8555-555555555555")
    result = write_checkpoint(
        seeded,
        workspace_id=WORKSPACE_ID,
        checkpoint_id=checkpoint_id,
        at=AT,
    )
    assert result.ok
    row = seeded.execute(
        text("SELECT ok, first_seq, last_seq FROM chain_checkpoints WHERE id = :id"),
        {"id": checkpoint_id},
    ).one()
    assert row[0] is True
    # seq est global : les transactions annulees laissent des trous de sequence.
    assert row[1] >= 1
    assert row[2] >= row[1]


@pytest.mark.integration
@pytest.mark.spec("ET-026")
def test_concurrent_appends_do_not_create_gaps(database_url: str) -> None:
    from sqlalchemy import create_engine

    workspace = uuid4()
    user = uuid4()
    request = uuid4()
    engine = create_engine(database_url)
    with engine.begin() as connection:
        connection.execute(
            text("SELECT set_config('app.workspace_id', :value, true)"),
            {"value": str(workspace)},
        )
        connection.execute(
            text("INSERT INTO workspaces (id, name, created_at) VALUES (:id, :name, :at)"),
            {"id": workspace, "name": "Concurrence", "at": AT},
        )
        connection.execute(
            text(
                """
                INSERT INTO users (id, workspace_id, display_name, role, created_at)
                VALUES (:id, :workspace_id, 'Test', 'responsible', :at)
                """
            ),
            {"id": user, "workspace_id": workspace, "at": AT},
        )
        connection.execute(
            text(
                """
                INSERT INTO requests (id, workspace_id, author_id, original_text, state, created_at)
                VALUES (:id, :workspace_id, :author_id, 'Concurrence', 'received', :at)
                """
            ),
            {"id": request, "workspace_id": workspace, "author_id": user, "at": AT},
        )

    def append_once(number: int) -> int:
        local_engine = create_engine(database_url)
        try:
            with local_engine.begin() as connection:
                connection.execute(
                    text("SELECT set_config('app.workspace_id', :value, true)"),
                    {"value": str(workspace)},
                )
                connection.execute(text("SELECT set_config('app.role', 'responsible', true)"))
                appended = append_event(
                    connection,
                    workspace_id=workspace,
                    request_id=request,
                    event_type="Concurrent",
                    payload={"number": number},
                    actor_type="human",
                    actor_id=user,
                    at=AT,
                )
                return appended.request_seq or 0
        finally:
            local_engine.dispose()

    with ThreadPoolExecutor(max_workers=2) as pool:
        sequences = sorted(pool.map(append_once, (1, 2)))
    assert sequences == [1, 2]

    with engine.connect() as connection:
        connection.execute(
            text("SELECT set_config('app.workspace_id', :value, true)"),
            {"value": str(workspace)},
        )
        connection.execute(text("SELECT set_config('app.role', 'responsible', true)"))
        result = verify_chain(connection, workspace)
        assert result.ok, result.errors
        assert result.checked == 2
    engine.dispose()
