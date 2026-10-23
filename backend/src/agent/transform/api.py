"""Facade applicative du module MOD-10 (transform).

Les autres modules n'utilisent que cette facade ou les evenements publies
(DR-02). Aucune logique metier n'est implementee en MS-0.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

from agent.transform.core.cel import (
    CalculationResult,
    CelError,
    calculate,
    compile_expression,
    evaluate,
)
from agent.transform.core.decimal_math import DecimalPolicy, UnitTable

MODULE_ID: Final[str] = "MOD-10"
MODULE_NAME: Final[str] = "transform"


@dataclass(frozen=True, slots=True)
class ModuleInfo:
    """Description stable de la facade, utile aux tests de frontieres."""

    module_id: str
    name: str


def module_info() -> ModuleInfo:
    return ModuleInfo(module_id=MODULE_ID, name=MODULE_NAME)


__all__ = [
    "CalculationResult",
    "CelError",
    "DecimalPolicy",
    "ModuleInfo",
    "UnitTable",
    "calculate",
    "compile_expression",
    "evaluate",
    "module_info",
]
