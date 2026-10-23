"""Facade applicative du module MOD-23 (platform).

Configuration, horloge, identifiants et services transverses. Les autres
modules n'utilisent que cette facade (DR-02).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

from agent.platform.clock import Clock, FixedClock, SystemClock
from agent.platform.ids import new_uuid7, uuid7, uuid7_timestamp_ms

MODULE_ID: Final[str] = "MOD-23"
MODULE_NAME: Final[str] = "platform"


@dataclass(frozen=True, slots=True)
class ModuleInfo:
    """Description stable de la facade, utile aux tests de frontieres."""

    module_id: str
    name: str


def module_info() -> ModuleInfo:
    return ModuleInfo(module_id=MODULE_ID, name=MODULE_NAME)


__all__ = [
    "Clock",
    "FixedClock",
    "ModuleInfo",
    "SystemClock",
    "module_info",
    "new_uuid7",
    "uuid7",
    "uuid7_timestamp_ms",
]
