#!/usr/bin/env python3
"""Detecte toute construction float dans le chemin de calcul (ET-062).

Le controle est volontairement syntaxique : il refuse les appels float(...)
et les annotations float, tout en laissant la garde isinstance(..., float)
qui sert a rejeter une entree flottante.
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CALC_ROOT = ROOT / "backend" / "src" / "agent" / "transform" / "core"


def find_float_usage(source: str | None = None, relpath: str = "") -> list[str]:
    violations: list[str] = []
    paths = sorted(CALC_ROOT.glob("*.py")) if source is None else [Path(relpath)]
    for path in paths:
        text = path.read_text(encoding="utf-8") if source is None else source
        try:
            tree = ast.parse(text, filename=str(path))
        except SyntaxError:
            continue
        parents: dict[ast.AST, ast.AST] = {}
        for node in ast.walk(tree):
            for child in ast.iter_child_nodes(node):
                parents[child] = node
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Name)
                and node.func.id == "float"
            ):
                violations.append(f"{path}: appel float() interdit")
            elif isinstance(node, ast.Attribute) and node.attr == "float":
                violations.append(f"{path}: attribut float interdit")
            elif isinstance(node, ast.Name) and node.id == "float":
                parent = parents.get(node)
                if not (
                    isinstance(parent, ast.Call)
                    and isinstance(parent.func, ast.Name)
                    and parent.func.id == "isinstance"
                ):
                    violations.append(f"{path}: reference float interdite")
    return violations


def main() -> int:
    violations = find_float_usage()
    if violations:
        print("Float interdit dans le chemin de calcul :", file=sys.stderr)
        for violation in violations:
            print(f"  - {violation}", file=sys.stderr)
        return 1
    print("ET-062 : aucun float dans transform/core")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
