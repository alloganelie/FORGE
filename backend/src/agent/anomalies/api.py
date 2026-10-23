"""Facade applicative du module MOD-13 (anomalies).

Les autres modules n'utilisent que cette facade ou les evenements publies
(DR-02). Aucune logique metier n'est implementee en MS-0.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

MODULE_ID: Final[str] = "MOD-13"
MODULE_NAME: Final[str] = "anomalies"


@dataclass(frozen=True, slots=True)
class ModuleInfo:
    """Description stable de la facade, utile aux tests de frontieres."""

    module_id: str
    name: str


def module_info() -> ModuleInfo:
    return ModuleInfo(module_id=MODULE_ID, name=MODULE_NAME)
