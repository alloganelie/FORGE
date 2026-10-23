"""Chaine de hachage du journal (ET-022, ET-026, PR-05).

Chaque evenement porte le hachage du precedent de sa demande. Le hachage est
calcule sur une serialisation canonique RFC 8785 ; la base verifie la
continuite, l'application re-verifie le contenu.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Any
from uuid import UUID

from agent.ledger.core.canonical import canonicalize

GENESIS_HASH = "0" * 64


@dataclass(frozen=True, slots=True)
class LedgerRecord:
    """Vue immuable d'un evenement, pour le calcul et la verification."""

    seq: int | None
    workspace_id: UUID
    request_id: UUID | None
    request_seq: int | None
    event_type: str
    payload: dict[str, Any]
    actor_type: str
    actor_id: UUID | None
    at: str
    prev_hash: str
    self_hash: str


@dataclass(frozen=True, slots=True)
class ChainVerification:
    ok: bool
    checked: int
    errors: tuple[str, ...]

    def raise_if_invalid(self) -> None:
        if not self.ok:
            raise ChainIntegrityError("; ".join(self.errors))


class ChainIntegrityError(RuntimeError):
    """La chaine du journal ne se verifie pas : alerte de securite."""


def hashed_material(record: LedgerRecord, prev_hash: str) -> dict[str, Any]:
    return {
        "workspace_id": str(record.workspace_id),
        "request_id": str(record.request_id) if record.request_id is not None else None,
        "request_seq": record.request_seq,
        "event_type": record.event_type,
        "payload": record.payload,
        "actor_type": record.actor_type,
        "actor_id": str(record.actor_id) if record.actor_id is not None else None,
        "at": record.at,
        "prev_hash": prev_hash,
    }


def compute_self_hash(record: LedgerRecord, prev_hash: str) -> str:
    material = hashed_material(record, prev_hash)
    return hashlib.sha256(canonicalize(material)).hexdigest()


def verify_events(records: tuple[LedgerRecord, ...]) -> ChainVerification:
    """Verifie hachages, continuite et absence de reordonnancement."""
    errors: list[str] = []
    last_seq: int | None = None
    expected: dict[UUID, tuple[int, str]] = {}
    for record in records:
        label = f"seq={record.seq}" if record.seq is not None else "seq=?"
        if record.seq is not None:
            if last_seq is not None and record.seq <= last_seq:
                errors.append(f"{label} : ordre global non croissant")
            last_seq = record.seq
        if record.request_id is None:
            if record.request_seq is not None:
                errors.append(f"{label} : request_seq interdit sans request_id")
                continue
            if record.prev_hash != GENESIS_HASH:
                errors.append(f"{label} : prev_hash non initial pour un evenement global")
            recomputed = compute_self_hash(record, record.prev_hash)
            if recomputed != record.self_hash:
                errors.append(f"{label} : self_hash invalide")
            continue
        previous = expected.get(record.request_id)
        wanted_seq, wanted_prev = (
            (1, GENESIS_HASH) if previous is None else (previous[0] + 1, previous[1])
        )
        if record.request_seq != wanted_seq:
            errors.append(
                f"{label} : request_seq {record.request_seq} au lieu de {wanted_seq} "
                "(trou ou doublon)"
            )
        if record.prev_hash != wanted_prev:
            errors.append(f"{label} : prev_hash ne suit pas l'evenement precedent")
        recomputed = compute_self_hash(record, record.prev_hash)
        if recomputed != record.self_hash:
            errors.append(f"{label} : self_hash invalide")
        expected[record.request_id] = (record.request_seq or 0, record.self_hash)
    return ChainVerification(ok=not errors, checked=len(records), errors=tuple(errors))
