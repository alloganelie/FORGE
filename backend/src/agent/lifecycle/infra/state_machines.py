"""Chargement des machines a etats versionnees (ET-035).

Les YAML sont la source unique des transitions ; le code ne contient aucune
transition en dur. Le chargeur valide la coherence avant tout usage.
"""

from __future__ import annotations

import os
from typing import Any, Final

import yaml

from agent.documents_io.api import read_utf8
from agent.lifecycle.core.engine import Machine, MachineSet, Transition
from agent.lifecycle.core.guards import GUARDS

DEFAULT_RULEPACK_DIR: Final[str] = os.path.normpath(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        "..",
        "..",
        "..",
        "..",
        "rulepacks",
        "state_machines",
    )
)
AXES: Final[tuple[str, ...]] = ("R", "C", "A", "D", "V", "E")
AXIS_FILES: Final[dict[str, str]] = {
    "R": "request.yaml",
    "C": "version_conformity.yaml",
    "A": "version_approval.yaml",
    "D": "version_diffusion.yaml",
    "V": "version_state.yaml",
    "E": "element.yaml",
}


class MachineDefinitionError(RuntimeError):
    """Definition de machine invalide : le demarrage doit echouer."""


def _name(path: str) -> str:
    return os.path.basename(path)


def _as_tuple(value: Any, field: str, path: str) -> tuple[str, ...]:
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise MachineDefinitionError(f"{_name(path)} : {field} doit etre une liste de chaines")
    return tuple(value)


def _as_effects(value: Any, path: str, transition_id: str) -> tuple[str, ...]:
    if not isinstance(value, list):
        raise MachineDefinitionError(f"{_name(path)} : effets invalides pour {transition_id}")
    effects: list[str] = []
    for item in value:
        if isinstance(item, str):
            effects.append(item)
        elif isinstance(item, dict) and len(item) == 1:
            key, raw = next(iter(item.items()))
            effects.append(f"{key}: {raw}")
        else:
            raise MachineDefinitionError(f"{_name(path)} : effet invalide pour {transition_id}")
    return tuple(effects)


def load_machine(path: str) -> Machine:
    raw = yaml.safe_load(read_utf8(path))
    name = _name(path)
    if not isinstance(raw, dict):
        raise MachineDefinitionError(f"{name} : document YAML invalide")
    if not isinstance(raw.get("states"), list):
        raise MachineDefinitionError(f"{name} : states doit etre une liste")
    try:
        axis = str(raw["axis"])
        entity = str(raw["entity"])
    except KeyError as exc:
        raise MachineDefinitionError(f"{name} : cle manquante {exc}") from exc

    state_values: list[str] = []
    for state in raw["states"]:
        if not isinstance(state, dict) or "value" not in state:
            raise MachineDefinitionError(f"{name} : etat invalide")
        state_values.append(str(state["value"]))
    if len(state_values) != len(set(state_values)):
        raise MachineDefinitionError(f"{name} : etats dupliques")

    final_states = frozenset(_as_tuple(raw.get("final_states", []), "final_states", path))
    unknown_final = final_states - set(state_values)
    if unknown_final:
        raise MachineDefinitionError(f"{name} : etats finaux inconnus {sorted(unknown_final)}")

    transitions: list[Transition] = []
    for item in raw.get("transitions", []):
        if not isinstance(item, dict):
            raise MachineDefinitionError(f"{name} : transition invalide")
        transition_id = str(item["id"])
        target = item.get("to")
        source = item.get("from")
        guards = _as_tuple(item.get("guards", []), "guards", path)
        unknown_guards = set(guards) - set(GUARDS)
        if unknown_guards:
            raise MachineDefinitionError(
                f"{name} : gardes inconnues pour {transition_id} : {sorted(unknown_guards)}"
            )
        transitions.append(
            Transition(
                id=transition_id,
                source=None if source is None else str(source),
                target=None if target is None else str(target),
                actors=_as_tuple(item.get("actor", []), "actor", path),
                guards=guards,
                condition=str(item.get("condition", "")),
                effects=_as_effects(item.get("effects", []), path, transition_id),
            )
        )
    ids = [transition.id for transition in transitions]
    if len(ids) != len(set(ids)):
        raise MachineDefinitionError(f"{name} : identifiants de transition dupliques")
    return Machine(
        axis=axis,
        entity=entity,
        states=tuple(state_values),
        final_states=final_states,
        transitions=tuple(transitions),
    )


def load_machines(directory: str | None = None) -> MachineSet:
    root = directory if directory is not None else DEFAULT_RULEPACK_DIR
    machines: dict[str, Machine] = {}
    for axis in AXES:
        path = os.path.join(root, AXIS_FILES[axis])
        machine = load_machine(path)
        if machine.axis != axis:
            raise MachineDefinitionError(
                f"{os.path.basename(path)} : axe {machine.axis} au lieu de {axis}"
            )
        machines[axis] = machine
    return MachineSet(by_axis=machines)
