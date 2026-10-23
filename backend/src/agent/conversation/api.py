"""Facade applicative du module MOD-18 (conversation).

Les autres modules n'utilisent que cette facade ou les evenements publies
(DR-02). Aucune logique metier n'est implementee en MS-0.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

from agent.conversation.core.templates import (
    STATE_LABELS,
    TEMPLATE_VERSION,
    filter_free_text,
    render,
    status_message,
)

MODULE_ID: Final[str] = "MOD-18"
MODULE_NAME: Final[str] = "conversation"


@dataclass(frozen=True, slots=True)
class ModuleInfo:
    """Description stable de la facade, utile aux tests de frontieres."""

    module_id: str
    name: str


def module_info() -> ModuleInfo:
    return ModuleInfo(module_id=MODULE_ID, name=MODULE_NAME)


__all__ = [
    "STATE_LABELS",
    "TEMPLATE_VERSION",
    "ModuleInfo",
    "filter_free_text",
    "module_info",
    "render",
    "status_message",
]
