"""ET-022, PR-05 : canonisation RFC 8785 et verification de chaine (pur)."""

from __future__ import annotations

from uuid import UUID

import pytest

from agent.ledger.api import (
    GENESIS_HASH,
    LedgerRecord,
    canonicalize,
    compute_self_hash,
    verify_events,
)
from agent.ledger.core.canonical import CanonicalizationError

WORKSPACE = UUID("11111111-1111-7111-8111-111111111111")
REQUEST = UUID("44444444-4444-7444-8444-444444444444")
ACTOR = UUID("22222222-2222-7222-8222-222222222222")
INSTANT = "2026-10-23T12:00:00.000000Z"


def _record(seq: int, previous: str, payload: dict[str, object] | None = None) -> LedgerRecord:
    draft = LedgerRecord(
        seq=seq,
        workspace_id=WORKSPACE,
        request_id=REQUEST,
        request_seq=seq,
        event_type="TestEvent",
        payload=payload or {"seq": seq},
        actor_type="human",
        actor_id=ACTOR,
        at=INSTANT,
        prev_hash=previous,
        self_hash="",
    )
    return LedgerRecord(
        seq=draft.seq,
        workspace_id=draft.workspace_id,
        request_id=draft.request_id,
        request_seq=draft.request_seq,
        event_type=draft.event_type,
        payload=draft.payload,
        actor_type=draft.actor_type,
        actor_id=draft.actor_id,
        at=draft.at,
        prev_hash=draft.prev_hash,
        self_hash=compute_self_hash(draft, previous),
    )


@pytest.mark.spec("ET-022")
def test_canonical_json_sorts_keys_and_preserves_unicode() -> None:
    assert canonicalize({"b": 2, "a": "é"}) == '{"a":"é","b":2}'.encode()
    assert canonicalize([True, None, 3]) == b"[true,null,3]"


@pytest.mark.spec("ET-022")
def test_canonical_json_rejects_floats() -> None:
    with pytest.raises(CanonicalizationError):
        canonicalize({"value": 1.5})


@pytest.mark.spec("ET-022")
def test_chain_verifies_and_detects_tampering() -> None:
    first = _record(1, GENESIS_HASH)
    second = _record(2, first.self_hash, {"seq": 2, "text": "b"})
    third = _record(3, second.self_hash)
    result = verify_events((first, second, third))
    assert result.ok, result.errors

    tampered = LedgerRecord(
        seq=second.seq,
        workspace_id=second.workspace_id,
        request_id=second.request_id,
        request_seq=second.request_seq,
        event_type=second.event_type,
        payload={"seq": 2, "text": "modifie"},
        actor_type=second.actor_type,
        actor_id=second.actor_id,
        at=second.at,
        prev_hash=second.prev_hash,
        self_hash=second.self_hash,
    )
    assert not verify_events((first, tampered, third)).ok


@pytest.mark.spec("ET-022")
def test_chain_detects_deletion_and_reordering() -> None:
    first = _record(1, GENESIS_HASH)
    second = _record(2, first.self_hash)
    third = _record(3, second.self_hash)
    assert not verify_events((first, third)).ok
    assert not verify_events((second, first, third)).ok


@pytest.mark.spec("ET-022")
def test_first_event_must_start_at_one_with_genesis() -> None:
    wrong = LedgerRecord(
        seq=1,
        workspace_id=WORKSPACE,
        request_id=REQUEST,
        request_seq=2,
        event_type="TestEvent",
        payload={},
        actor_type="human",
        actor_id=ACTOR,
        at=INSTANT,
        prev_hash=GENESIS_HASH,
        self_hash="0" * 64,
    )
    assert not verify_events((wrong,)).ok
