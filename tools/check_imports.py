#!/usr/bin/env python3
"""Controle des regles de dependance DR-01 a DR-07 (ET-005).

Analyse statique par AST, sans dependance externe. Une violation fait echouer
le build. Les regles dynamiques (DR-03 en base, DR-04 par privileges) sont
doublees par des declencheurs et des tests d'integration.
"""

from __future__ import annotations

import ast
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC_ROOT = ROOT / "backend" / "src"
AGENT_ROOT = SRC_ROOT / "agent"

MODULES = {
    "identity_access",
    "governance",
    "requests",
    "lifecycle",
    "feasibility",
    "sourcing",
    "evidence",
    "mapping",
    "gaps_conflicts",
    "transform",
    "assembly",
    "controls",
    "anomalies",
    "reporting",
    "decisions",
    "revisions",
    "scheduling",
    "conversation",
    "ledger",
    "policy_privacy",
    "llm_gateway",
    "documents_io",
    "platform",
}

STATE_ATTRS = {"state", "st_v", "st_c", "st_a", "st_d", "st_e"}
CORE_FORBIDDEN = {
    "alembic",
    "anthropic",
    "boto3",
    "datetime",
    "fastapi",
    "httpx",
    "httpx2",
    "openai",
    "os",
    "pathlib",
    "psycopg",
    "random",
    "requests",
    "shutil",
    "socket",
    "sqlalchemy",
    "subprocess",
    "time",
}
LLM_PROVIDERS = {"anthropic", "boto3", "google", "openai"}
FACADE_SUFFIXES = (".api", ".events")


@dataclass(frozen=True, slots=True)
class Violation:
    rule: str
    path: str
    line: int
    message: str

    def __str__(self) -> str:
        return f"{self.rule} {self.path}:{self.line} - {self.message}"


def _relative_parts(relpath: str) -> tuple[str, ...]:
    return tuple(Path(relpath).with_suffix("").parts)


def _current_module(relpath: str) -> str | None:
    parts = _relative_parts(relpath)
    if len(parts) >= 2 and parts[0] == "agent" and parts[1] in MODULES:
        return parts[1]
    return None


def _resolve_import(relpath: str, node: ast.ImportFrom) -> list[str]:
    if node.level == 0:
        return [node.module] if node.module else []
    parts = list(_relative_parts(relpath))
    package = parts[:-1]
    drop = node.level - 1
    if drop > 0:
        package = package[:-drop]
    if node.module:
        package = [*package, node.module]
    return [".".join(package)]


def _imported_modules(tree: ast.AST, relpath: str) -> list[tuple[int, str]]:
    found: list[tuple[int, str]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                found.append((node.lineno, alias.name))
        elif isinstance(node, ast.ImportFrom):
            for module in _resolve_import(relpath, node):
                found.append((node.lineno, module))
    return found


def _is_facade(module: str, target: str) -> bool:
    return module == f"agent.{target}.api" or module == f"agent.{target}.events"


def _is_infra_or_core(module: str, target: str) -> bool:
    prefix = f"agent.{target}."
    return module.startswith(prefix) and not _is_facade(module, target)


def scan_source(source: str, relpath: str) -> list[Violation]:
    """Analyse une source Python et retourne les violations DR-01 a DR-07."""
    try:
        tree = ast.parse(source, filename=relpath)
    except SyntaxError as exc:
        return [Violation("DR-00", relpath, exc.lineno or 0, f"source illisible : {exc.msg}")]

    violations: list[Violation] = []
    current = _current_module(relpath)
    parts = _relative_parts(relpath)
    in_core = current is not None and len(parts) >= 3 and parts[2] == "core"
    is_interface = len(parts) >= 2 and parts[0] == "agent" and parts[1] == "interfaces"

    for line, module in _imported_modules(tree, relpath):
        root = module.split(".")[0]
        if in_core and root in CORE_FORBIDDEN:
            violations.append(Violation("DR-01", relpath, line, f"le domaine pur importe {root!r}"))
        if current is not None and module.startswith("agent."):
            target = module.split(".")[1] if len(module.split(".")) > 1 else ""
            if target in MODULES and target != current and not _is_facade(module, target):
                violations.append(
                    Violation(
                        "DR-02",
                        relpath,
                        line,
                        f"acces direct a {module!r} : utiliser {target}.api ou {target}.events",
                    )
                )
            if current != "ledger" and target == "ledger":
                violations.append(Violation("DR-04", relpath, line, "seul ledger ecrit le journal"))
        if is_interface and module.startswith("agent."):
            target = module.split(".")[1] if len(module.split(".")) > 1 else ""
            if target in MODULES and target != "platform" and _is_infra_or_core(module, target):
                violations.append(
                    Violation(
                        "DR-07",
                        relpath,
                        line,
                        f"l'interface importe {module!r} : passer par la facade",
                    )
                )
        if root in LLM_PROVIDERS and current != "llm_gateway":
            violations.append(
                Violation("DR-05", relpath, line, f"appel direct au fournisseur {root!r}")
            )
        if root == "pathlib" and current != "documents_io":
            violations.append(
                Violation("DR-06", relpath, line, "seul documents_io manipule des fichiers")
            )

    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if (
                isinstance(node.func, ast.Name)
                and node.func.id == "open"
                and current != "documents_io"
            ):
                violations.append(
                    Violation("DR-06", relpath, node.lineno, "appel open() hors documents_io")
                )
            if (
                isinstance(node.func, ast.Attribute)
                and node.func.attr in {"uuid1", "uuid4"}
                and isinstance(node.func.value, ast.Name)
                and node.func.value.id == "uuid"
            ):
                violations.append(
                    Violation(
                        "DR-01",
                        relpath,
                        node.lineno,
                        "identifiants via le port platform, pas uuid4 dans le domaine",
                    )
                )
        if isinstance(node, (ast.Assign, ast.AnnAssign, ast.AugAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            for target in targets:
                if (
                    isinstance(target, ast.Attribute)
                    and target.attr in STATE_ATTRS
                    and current != "lifecycle"
                ):
                    violations.append(
                        Violation(
                            "DR-03",
                            relpath,
                            node.lineno,
                            f"ecriture de l'etat {target.attr!r} hors lifecycle",
                        )
                    )
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "setattr"
            and len(node.args) >= 2
        ):
            name = node.args[1]
            if (
                isinstance(name, ast.Constant)
                and name.value in STATE_ATTRS
                and current != "lifecycle"
            ):
                violations.append(
                    Violation("DR-03", relpath, node.lineno, "setattr sur une colonne d'etat")
                )
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            if "ledger_events" in node.value and current != "ledger":
                violations.append(
                    Violation(
                        "DR-04", relpath, node.lineno, "reference a ledger_events hors ledger"
                    )
                )
            if node.value.startswith("TR-") and len(node.value) <= 8 and is_interface:
                violations.append(
                    Violation("DR-07", relpath, node.lineno, "transition dans l'interface")
                )

    return violations


def find_violations(root: Path = SRC_ROOT) -> list[Violation]:
    violations: list[Violation] = []
    for path in sorted(root.rglob("*.py")):
        relpath = path.relative_to(root).as_posix()
        violations.extend(scan_source(path.read_text(encoding="utf-8"), relpath))
    return violations


def main() -> int:
    violations = find_violations()
    if violations:
        print("Violations des regles de dependance :", file=sys.stderr)
        for violation in violations:
            print(f"  {violation}", file=sys.stderr)
        return 1
    print("DR-01 a DR-07 : aucune violation")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
