"""Facade applicative du module MOD-04 (lifecycle).

Les autres modules n'utilisent que cette facade ou les evenements publies
(DR-02). Aucune logique metier n'est implementee en MS-0.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

from agent.lifecycle.core.engine import (
    InvalidTransition,
    Machine,
    MachineSet,
    ResumeTargetError,
    Transition,
    TransitionError,
    UnknownTransition,
    apply_transition,
    resume_target,
)
from agent.lifecycle.core.guards import GuardContext, GuardResult
from agent.lifecycle.infra.state_machines import (
    MachineDefinitionError,
    load_machines,
)
from agent.lifecycle.infra.transitions import (
    AppliedTransition,
    ConcurrencyConflict,
    TransitionRejected,
    apply_element_transition,
    apply_request_transition,
    apply_version_transition,
)

MODULE_ID: Final[str] = "MOD-04"
MODULE_NAME: Final[str] = "lifecycle"


@dataclass(frozen=True, slots=True)
class ModuleInfo:
    """Description stable de la facade, utile aux tests de frontieres."""

    module_id: str
    name: str


def module_info() -> ModuleInfo:
    return ModuleInfo(module_id=MODULE_ID, name=MODULE_NAME)


__all__ = [
    "AppliedTransition",
    "ConcurrencyConflict",
    "GuardContext",
    "GuardResult",
    "InvalidTransition",
    "Machine",
    "MachineDefinitionError",
    "MachineSet",
    "ModuleInfo",
    "ResumeTargetError",
    "Transition",
    "TransitionError",
    "TransitionRejected",
    "UnknownTransition",
    "apply_element_transition",
    "apply_request_transition",
    "apply_transition",
    "apply_version_transition",
    "load_machines",
    "module_info",
    "resume_target",
]
