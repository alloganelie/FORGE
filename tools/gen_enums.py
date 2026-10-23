#!/usr/bin/env python3
"""Genere les types enumeres depuis la specification (ET-017, DC-05).

Sources :
  - specification fonctionnelle, section 8 : identifiants ST-xx et libelles ;
  - specification technique, section 6.3 : valeurs SQL et identifiants QI/LC/AN/RC/DH/AU.

Sorties :
  - backend/src/agent/lifecycle/core/states.py (enums Python) ;
  - backend/migrations/sql/0001_enums.sql (types PostgreSQL).

L'outil est idempotent : --check echoue si les fichiers ne correspondent plus
a la specification.
"""

from __future__ import annotations

import argparse
import re
import sys
import unicodedata
from dataclasses import dataclass
from pathlib import Path

try:  # execution en script ou en module de test
    from tools.spec import Doc, load
except ModuleNotFoundError:  # pragma: no cover - fallback script
    from spec import Doc, load  # type: ignore[no-redef]

ROOT = Path(__file__).resolve().parent.parent
PYTHON_OUT = ROOT / "backend" / "src" / "agent" / "lifecycle" / "core" / "states.py"
SQL_OUT = ROOT / "backend" / "migrations" / "sql" / "0001_enums.sql"

ENUM_CLASS_NAMES = {
    "st_request": "RequestState",
    "st_conformity": "ConformityState",
    "st_approval": "ApprovalState",
    "st_diffusion": "DiffusionState",
    "st_version": "VersionState",
    "st_element": "ElementState",
    "qi_status": "QualityStatus",
    "lc_status": "LcStatus",
    "atom_origin": "AtomOrigin",
    "control_outcome": "ControlOutcome",
    "anomaly_class": "AnomalyClass",
    "decision_type": "DecisionType",
    "auth_level": "AuthLevel",
}

AXIS_BY_ENUM = {
    "st_request": "R",
    "st_conformity": "C",
    "st_approval": "A",
    "st_diffusion": "D",
    "st_version": "V",
    "st_element": "E",
}

# Familles d'identifiants non-ST, d'apres les commentaires de T 6.3.
FAMILY_BY_ENUM = {
    "qi_status": ("QI", 2),
    "lc_status": ("LC", 2),
    "control_outcome": ("RC", 1),
    "anomaly_class": ("AN", 1),
    "decision_type": ("DH", 2),
    "auth_level": ("AU", 1),
}


@dataclass(frozen=True, slots=True)
class EnumDef:
    sql_name: str
    class_name: str
    values: tuple[str, ...]
    spec_ids: tuple[str, ...]


def _normalise(text: str) -> str:
    stripped = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"\s+", " ", stripped).strip().lower()


def _section(doc: Doc, prefix: str) -> str:
    for idx, (start, _level, text, _sec, _idref) in enumerate(doc.headings):
        if text.startswith(prefix):
            end = doc.block_end(idx)
            return "\n".join(doc.lines[start:end])
    raise SystemExit(f"Section introuvable : {prefix}")


def _parse_sql_enums(technical: Doc) -> list[tuple[str, tuple[str, ...], str]]:
    block = _section(technical, "6.3")
    pattern = re.compile(
        r"CREATE TYPE\s+(\w+)\s+AS ENUM\s*\((.*?)\);(?:[ \t]*--[ \t]*([^\n]*))?",
        re.S,
    )
    found: list[tuple[str, tuple[str, ...], str]] = []
    for match in pattern.finditer(block):
        values = tuple(re.findall(r"'([^']*)'", match.group(2)))
        found.append((match.group(1), values, (match.group(3) or "").strip()))
    if len(found) != len(ENUM_CLASS_NAMES):
        raise SystemExit(f"6.3 : {len(found)} types trouves, {len(ENUM_CLASS_NAMES)} attendus")
    return found


def _parse_functional_states(functional: Doc) -> dict[str, tuple[tuple[str, str], ...]]:
    by_axis: dict[str, tuple[tuple[str, str], ...]] = {}
    row = re.compile(r"^\|\s*(ST-([A-Z])-(\d{2}))\s*\|\s*\*\*(.+?)\*\*")
    for prefix, axis in (
        ("8.2", "R"),
        ("8.3", "C"),
        ("8.4", "A"),
        ("8.5", "D"),
        ("8.6", "V"),
        ("8.7", "E"),
    ):
        block = _section(functional, prefix)
        states: list[tuple[str, str]] = []
        for line in block.split("\n"):
            match = row.match(line)
            if match:
                states.append((match.group(1), match.group(4).strip()))
        if not states:
            raise SystemExit(f"Section {prefix} : aucun etat ST-{axis} trouve")
        by_axis[axis] = tuple(states)
    return by_axis


def _family_ids(comment: str, count: int, default_prefix: str) -> tuple[str, ...]:
    match = re.search(r"([A-Z]{2,4})-(\d+)(?:\.\.(\d+))?", comment)
    if not match:
        if not comment:
            return tuple(f"{default_prefix}-{index:02d}" for index in range(1, count + 1))
        prefix = comment.strip()
        return tuple(f"{prefix}-{index:02d}" for index in range(1, count + 1))
    prefix, first, last = match.group(1), int(match.group(2)), match.group(3)
    width = len(match.group(2))
    final = int(last) if last else first + count - 1
    ids = tuple(f"{prefix}-{number:0{width}d}" for number in range(first, final + 1))
    if len(ids) != count:
        raise SystemExit(
            f"Plage {prefix} incoherente : {len(ids)} identifiants pour {count} valeurs"
        )
    return ids


def build_enums() -> list[EnumDef]:
    functional = load("F")
    technical = load("T")
    states_by_axis = _parse_functional_states(functional)
    definitions: list[EnumDef] = []

    for sql_name, values, comment in _parse_sql_enums(technical):
        class_name = ENUM_CLASS_NAMES[sql_name]
        axis = AXIS_BY_ENUM.get(sql_name)
        if axis is not None:
            functional_states = states_by_axis[axis]
            if len(functional_states) != len(values):
                raise SystemExit(
                    f"{sql_name} : {len(values)} valeurs SQL pour "
                    f"{len(functional_states)} etats F 8"
                )
            spec_ids = tuple(identifier for identifier, _label in functional_states)
        elif sql_name in FAMILY_BY_ENUM:
            prefix, width = FAMILY_BY_ENUM[sql_name]
            ids = _family_ids(comment, len(values), prefix)
            spec_ids = tuple(f"{prefix}-{number:0{width}d}" for number in range(1, len(values) + 1))
            if ids != spec_ids:
                spec_ids = ids
        else:
            spec_ids = ()
        definitions.append(
            EnumDef(
                sql_name=sql_name,
                class_name=class_name,
                values=values,
                spec_ids=spec_ids,
            )
        )
    return definitions


def _member_name(value: str) -> str:
    return re.sub(r"[^A-Z0-9]+", "_", value.upper()).strip("_")


def render_python(definitions: list[EnumDef]) -> str:
    lines = [
        '"""Types enumeres generes depuis la specification (ET-017, DC-05).',
        "",
        "NE PAS MODIFIER A LA MAIN. Regenerer : python tools/gen_enums.py",
        "Sources : specification fonctionnelle section 8, specification technique 6.3.",
        '"""',
        "",
        "from __future__ import annotations",
        "",
        "from enum import StrEnum",
        "from typing import Final",
        "",
    ]
    for definition in definitions:
        lines.append("")
        lines.append(f"class {definition.class_name}(StrEnum):")
        lines.append(
            '    """Valeurs alignees sur le type PostgreSQL ' + definition.sql_name + '."""'
        )
        lines.append("")
        for value in definition.values:
            lines.append(f'    {_member_name(value)} = "{value}"')
        lines.append("")

    lines.append("SPEC_IDS: Final[dict[str, dict[str, str]]] = {")
    for definition in definitions:
        if not definition.spec_ids:
            continue
        lines.append(f'    "{definition.class_name}": {{')
        for value, spec_id in zip(definition.values, definition.spec_ids, strict=True):
            lines.append(f'        "{value}": "{spec_id}",')
        lines.append("    },")
    lines.append("}")
    lines.append("")
    lines.append("AXIS_ENUM_NAMES: Final[dict[str, str]] = {")
    for sql_name, axis in AXIS_BY_ENUM.items():
        lines.append(f'    "{axis}": "{ENUM_CLASS_NAMES[sql_name]}",')
    lines.append("}")
    lines.append("")
    lines.append("AXIS_STATE_IDS: Final[dict[str, dict[str, str]]] = {")
    for sql_name, axis in AXIS_BY_ENUM.items():
        definition = next(item for item in definitions if item.sql_name == sql_name)
        lines.append(f'    "{axis}": {{')
        for value, spec_id in zip(definition.values, definition.spec_ids, strict=True):
            lines.append(f'        "{value}": "{spec_id}",')
        lines.append("    },")
    lines.append("}")
    lines.append("")
    return "\n".join(lines)


def render_sql(definitions: list[EnumDef]) -> str:
    lines = [
        "-- Types enumeres generes depuis la specification (ET-017, DC-05).",
        "-- NE PAS MODIFIER A LA MAIN. Regenerer : python tools/gen_enums.py",
        "-- Sources : specification fonctionnelle section 8, specification technique 6.3.",
        "",
    ]
    for definition in definitions:
        joined = ", ".join(f"'{value}'" for value in definition.values)
        lines.append(f"CREATE TYPE {definition.sql_name} AS ENUM ({joined});")
    lines.append("")
    return "\n".join(lines)


def _write_or_check(path: Path, content: str, *, check: bool) -> bool:
    current = path.read_text(encoding="utf-8") if path.exists() else None
    if check:
        if current != content:
            print(f"Desynchronise : {path.relative_to(ROOT)} (lancer python tools/gen_enums.py)")
            return False
        return True
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")
    print(f"Ecrit : {path.relative_to(ROOT)}")
    return True


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="verifie sans ecrire")
    args = parser.parse_args(argv)
    definitions = build_enums()
    ok = _write_or_check(PYTHON_OUT, render_python(definitions), check=args.check)
    ok = _write_or_check(SQL_OUT, render_sql(definitions), check=args.check) and ok
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
