"""Facade applicative du module MOD-15 (decisions).

Les autres modules n'utilisent que cette facade ou les evenements publies
(DR-02). Aucune logique metier n'est implementee en MS-0.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

MODULE_ID: Final[str] = "MOD-15"
MODULE_NAME: Final[str] = "decisions"


@dataclass(frozen=True, slots=True)
class ModuleInfo:
    """Description stable de la facade, utile aux tests de frontieres."""

    module_id: str
    name: str


def module_info() -> ModuleInfo:
    return ModuleInfo(module_id=MODULE_ID, name=MODULE_NAME)
