"""Facade applicative du module MOD-19 (ledger).

Toute ecriture du journal passe par append_event ; les autres modules ne
manipulent jamais ledger_events (DR-04).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

from agent.ledger.core.canonical import CanonicalizationError, canonicalize
from agent.ledger.core.hashchain import (
    GENESIS_HASH,
    ChainIntegrityError,
    ChainVerification,
    LedgerRecord,
    compute_self_hash,
    verify_events,
)
from agent.ledger.infra.repository import (
    AppendedEvent,
    append_event,
    verify_chain,
    write_checkpoint,
)

MODULE_ID: Final[str] = "MOD-19"
MODULE_NAME: Final[str] = "ledger"


@dataclass(frozen=True, slots=True)
class ModuleInfo:
    """Description stable de la facade, utile aux tests de frontieres."""

    module_id: str
    name: str


def module_info() -> ModuleInfo:
    return ModuleInfo(module_id=MODULE_ID, name=MODULE_NAME)


__all__ = [
    "GENESIS_HASH",
    "AppendedEvent",
    "CanonicalizationError",
    "ChainIntegrityError",
    "ChainVerification",
    "LedgerRecord",
    "ModuleInfo",
    "append_event",
    "canonicalize",
    "compute_self_hash",
    "module_info",
    "verify_chain",
    "verify_events",
    "write_checkpoint",
]
