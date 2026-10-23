#!/usr/bin/env python3
"""Genere les machines a etats YAML depuis la specification (ET-035, ET-044).

Sources :
  - specification fonctionnelle 8.2 a 8.7 : etats ST-xx et transitions TR-xx ;
  - specification technique 7.2 : acteurs, gardes et effets declaratifs ;
  - specification technique 6.3 : valeurs des types enumeres.

Sorties : rulepacks/state_machines/*.yaml. Aucune transition n'existe
uniquement dans le code (ET-035). L'outil est idempotent : --check echoue si
les fichiers divergent de la specification.
"""

from __future__ import annotations

import argparse
import hashlib
import re
import sys
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

try:  # execution en script ou en module de test
    from tools.gen_enums import build_enums
    from tools.spec import Doc, cells, load
except ModuleNotFoundError:  # pragma: no cover - fallback script
    from gen_enums import build_enums  # type: ignore[no-redef]
    from spec import Doc, cells, load  # type: ignore[no-redef]

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "rulepacks" / "state_machines"

AXES = (
    ("R", "8.2", "request.yaml", "request", "st_request", ["finalized", "cancelled"]),
    ("C", "8.3", "version_conformity.yaml", "deliverable_version", "st_conformity", ["conforming"]),
    (
        "A",
        "8.4",
        "version_approval.yaml",
        "deliverable_version",
        "st_approval",
        ["approved", "refused"],
    ),
    ("D", "8.5", "version_diffusion.yaml", "deliverable_version", "st_diffusion", []),
    (
        "V",
        "8.6",
        "version_state.yaml",
        "deliverable_version",
        "st_version",
        ["superseded", "abandoned"],
    ),
    ("E", "8.7", "element.yaml", "element", "st_element", []),
)

LABEL_ALIASES = {
    "recue": "received",
    "en clarification": "clarifying",
    "en verification de faisabilite": "feasibility",
    "en production": "producing",
    "en controle qualite": "quality_control",
    "bloquee": "blocked",
    "bloque": "blocked",
    "en attente d'une decision humaine": "awaiting_decision",
    "suspendue": "suspended",
    "finalisee": "finalized",
    "annulee definitivement": "cancelled",
    "non evalue": "not_evaluated",
    "en controle": "in_control",
    "non conforme": "non_conforming",
    "conforme": "conforming",
    "conforme (version non encore finalisee)": "conforming",
    "non soumise": "not_submitted",
    "non requise": "not_required",
    "en attente d'approbation": "pending",
    "approuvee": "approved",
    "refusee": "refused",
    "non autorisee": "not_authorized",
    "autorisee": "authorized",
    "revoquee": "revoked",
    "provisoire": "provisional",
    "remplacee": "superseded",
    "abandonnee": "abandoned",
    "a produire": "to_produce",
    "produit (provisoire)": "produced",
    "produit": "produced",
    "en attente de clarification ou de decision": "awaiting",
    "controle conforme": "controlled_ok",
    "non applicable": "not_applicable",
}

ACTORS = {
    "utilisateur": "user",
    "agent": "agent",
    "personne responsable": "responsible",
    "auteur de la demande": "author",
}

# Gardes non listees explicitement en T 7.2 pour les axes C, A, V et E.
# Le texte de condition reste conserve dans le YAML pour la suite du projet.
EXTRA_GUARDS = {
    "TR-C-02": ["all_mandatory_controls_passed"],
    "TR-C-03": ["mandatory_control_failed"],
    "TR-A-01": ["version_finalized"],
    "TR-A-02": ["version_finalized"],
    "TR-A-03": ["approver_authorized"],
    "TR-A-04": ["approver_authorized"],
    "TR-V-01": [
        "all_mandatory_controls_passed",
        "version_conforming",
        "mandatory_elements_ok",
        "reports_produced",
    ],
}

NON_TRANSITIONS = {
    "TR-R-22": "Revision : cree une nouvelle demande liee via TR-R-01 ; aucun etat ne change",
}

# Les tableaux F 8.3 a 8.7 ne portent pas de colonne Acteur : la specification
# technique 7.3 et IV-09 fixent les acteurs par axe.
DEFAULT_ACTORS = {
    "C": ["agent"],
    "A": ["responsible"],
    "V": ["agent", "system"],
    "E": ["agent"],
}


@dataclass
class ParsedAxis:
    axis: str
    section: str
    filename: str
    entity: str
    sql_enum: str
    final_states: list[str]
    states: list[dict[str, str]] = field(default_factory=list)
    transitions: list[dict[str, Any]] = field(default_factory=list)
    non_transitions: list[dict[str, str]] = field(default_factory=list)


def normalise(text: str) -> str:
    stripped = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"\s+", " ", stripped).strip().lower()


def section(doc: Doc, prefix: str) -> str:
    for idx, (start, _level, text, _sec, _idref) in enumerate(doc.headings):
        if text.startswith(prefix):
            return "\n".join(doc.lines[start : doc.block_end(idx)])
    raise SystemExit(f"Section introuvable : {prefix}")


def parse_states(block: str) -> list[dict[str, str]]:
    pattern = re.compile(r"^\|\s*(ST-([A-Z])-(\d{2}))\s*\|\s*\*\*(.+?)\*\*")
    states: list[dict[str, str]] = []
    for line in block.split("\n"):
        match = pattern.match(line)
        if match:
            states.append({"id": match.group(1), "label": match.group(4).strip()})
    return states


def parse_transitions(block: str) -> list[list[str]]:
    rows: list[list[str]] = []
    for line in block.split("\n"):
        if not line.startswith("| TR-"):
            continue
        row = cells(line)
        if len(row) in (5, 6):
            rows.append(row)
    return rows


def parse_t72(technical: Doc) -> dict[str, dict[str, dict[str, Any]]]:
    block = section(technical, "7.2")
    blocks: list[str] = []
    current: list[str] | None = None
    for line in block.split("\n"):
        if line.strip() == "```yaml":
            current = []
            continue
        if current is not None and line.strip() == "```":
            blocks.append("\n".join(current))
            current = None
            continue
        if current is not None:
            current.append(line)
    parsed: dict[str, dict[str, dict[str, Any]]] = {}
    for raw in blocks:
        data = yaml.safe_load(raw)
        if not isinstance(data, dict) or "axis" not in data:
            continue
        axis = str(data["axis"])
        parsed[axis] = {}
        for transition in data.get("transitions", []):
            parsed[axis][str(transition["id"])] = transition
    return parsed


def resolve_label(raw: str, labels: dict[str, str], allowed: set[str]) -> str:
    cleaned = raw.strip().strip("*").strip()
    if cleaned in allowed:
        return cleaned
    key = normalise(cleaned)
    if key in LABEL_ALIASES:
        return LABEL_ALIASES[key]
    if key in labels:
        return labels[key]
    for label, value in labels.items():
        if key and (key in label or label in key):
            return value
    raise SystemExit(f"Libelle d'etat non resolu : {raw!r}")


def parse_actors(raw: str) -> list[str]:
    parts = [part.strip() for part in re.split(r"\s+(?:puis|ou|et)\s+", raw.strip())]
    actors: list[str] = []
    for part in parts:
        key = normalise(part)
        if key not in ACTORS:
            raise SystemExit(f"Acteur non resolu : {part!r}")
        actors.append(ACTORS[key])
    return actors


def build_axis(
    functional: Doc,
    technical: Doc,
    definition: tuple[str, str, str, str, str, list[str]],
    enum_values: dict[str, tuple[str, ...]],
    t72: dict[str, dict[str, dict[str, Any]]],
) -> ParsedAxis:
    axis, prefix, filename, entity, sql_enum, final_states = definition
    block = section(functional, prefix)
    states = parse_states(block)
    values = enum_values[sql_enum]
    if len(states) != len(values):
        raise SystemExit(f"Axe {axis} : {len(states)} etats F pour {len(values)} valeurs SQL")
    labels: dict[str, str] = {}
    for state, value in zip(states, values, strict=True):
        state["value"] = value
        labels[normalise(state["label"])] = value
    allowed = set(values)

    parsed = ParsedAxis(
        axis=axis,
        section=prefix,
        filename=filename,
        entity=entity,
        sql_enum=sql_enum,
        final_states=list(final_states),
        states=states,
    )

    for row in parse_transitions(block):
        if len(row) == 6:
            transition_id, from_raw, to_raw, condition, actors_raw, _status = row
        else:
            transition_id, from_raw, to_raw, condition, _status = row
            actors_raw = ""
        if transition_id in NON_TRANSITIONS:
            parsed.non_transitions.append(
                {"id": transition_id, "reason": NON_TRANSITIONS[transition_id]}
            )
            continue
        override = t72.get(axis, {}).get(transition_id, {})
        if override:
            source = override.get("from")
            target = override.get("to")
            actors = list(override.get("actor", []))
            guards = list(override.get("guards", []))
            effects = list(override.get("effects", []))
        else:
            source = resolve_special_source(from_raw, labels, allowed)
            target = resolve_special_target(to_raw, labels, allowed)
            actors = parse_actors(actors_raw) if actors_raw else list(DEFAULT_ACTORS[axis])
            guards = list(EXTRA_GUARDS.get(transition_id, []))
            effects = []
        if target is None:
            raise SystemExit(f"{transition_id} : cible non resolue")
        parsed.transitions.append(
            {
                "id": transition_id,
                "from": source,
                "to": target,
                "actor": actors,
                "guards": guards,
                "condition": condition.strip(),
                "effects": effects,
            }
        )
    return parsed


def resolve_special_source(raw: str, labels: dict[str, str], allowed: set[str]) -> str | None:
    cleaned = raw.strip()
    if cleaned == "—":
        return None
    key = normalise(cleaned)
    if key.startswith("tout etat non final, sauf"):
        return "ANY_NON_FINAL_EXCEPT_SUSPENDED"
    if key.startswith("tout etat non final"):
        return "ANY_NON_FINAL"
    return resolve_label(cleaned, labels, allowed)


def resolve_special_target(raw: str, labels: dict[str, str], allowed: set[str]) -> str | None:
    cleaned = raw.strip()
    key = normalise(cleaned)
    if key.startswith("etat reevalue"):
        return "DYNAMIC"
    if "inchangee" in key:
        return None
    return resolve_label(cleaned, labels, allowed)


def dump_axis(parsed: ParsedAxis, functional_hash: str, technical_hash: str) -> str:
    payload = {
        "axis": parsed.axis,
        "entity": parsed.entity,
        "spec_section": parsed.section,
        "generated_from": {
            "functional_sha256": functional_hash,
            "technical_sha256": technical_hash,
        },
        "states": parsed.states,
        "final_states": parsed.final_states,
        "transitions": parsed.transitions,
        "non_transitions": parsed.non_transitions,
    }
    header = (
        "# Genere par tools/gen_transitions.py depuis F 8 et T 7.2.\n"
        "# NE PAS MODIFIER A LA MAIN. Regenerer : python tools/gen_transitions.py\n"
    )
    body = yaml.safe_dump(
        payload,
        sort_keys=False,
        allow_unicode=True,
        default_flow_style=False,
        width=120,
    )
    return header + body


def build_axes() -> list[ParsedAxis]:
    functional = load("F")
    technical = load("T")
    enums = build_enums()
    enum_values = {definition.sql_name: definition.values for definition in enums}
    t72 = parse_t72(technical)
    return [build_axis(functional, technical, definition, enum_values, t72) for definition in AXES]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="verifie sans ecrire")
    args = parser.parse_args(argv)

    functional = load("F")
    technical = load("T")
    functional_hash = hashlib.sha256("\n".join(functional.lines).encode("utf-8")).hexdigest()
    technical_hash = hashlib.sha256("\n".join(technical.lines).encode("utf-8")).hexdigest()

    ok = True
    for parsed in build_axes():
        content = dump_axis(parsed, functional_hash, technical_hash)
        path = OUT_DIR / parsed.filename
        current = path.read_text(encoding="utf-8") if path.exists() else None
        if args.check:
            if current != content:
                print(
                    f"Desynchronise : {path.relative_to(ROOT)} "
                    "(lancer python tools/gen_transitions.py)"
                )
                ok = False
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8", newline="\n")
            print(f"Ecrit : {path.relative_to(ROOT)} ({len(parsed.transitions)} transitions)")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
