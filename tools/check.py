#!/usr/bin/env python3
"""Orchestrateur des commandes de qualite (make check).

Sans dependance externe : peut etre lance avec le Python systeme.
Sur Windows, make est optionnel : python tools/check.py check.
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
IS_WINDOWS = os.name == "nt"
VENV = ROOT / ".venv"
VENV_PYTHON = VENV / ("Scripts/python.exe" if IS_WINDOWS else "bin/python")


def _run(command: list[str], *, check: bool = True) -> int:
    print("+", " ".join(command), flush=True)
    completed = subprocess.run(command, cwd=ROOT, check=False)
    if check and completed.returncode != 0:
        raise SystemExit(completed.returncode)
    return completed.returncode


def _uv() -> list[str]:
    uv = shutil.which("uv")
    if uv:
        return [uv]
    return [sys.executable, "-m", "uv"]


def sync() -> None:
    """Installe l'environnement verrouille (ET-004)."""
    if not (ROOT / "uv.lock").exists():
        raise SystemExit("uv.lock absent : lancer 'uv lock' puis relancer make check")
    _run([*_uv(), "sync", "--locked", "--all-groups"])


def _venv_python() -> str:
    if VENV_PYTHON.exists():
        return str(VENV_PYTHON)
    return sys.executable


def _tool(name: str, *args: str) -> int:
    return _run([_venv_python(), "-m", name, *args], check=False)


def fmt() -> None:
    _tool("ruff", "format", "backend/src", "backend/tests", "tools")
    _tool("ruff", "check", "--fix", "backend/src", "backend/tests", "tools")


def format_check() -> None:
    _run(
        [_venv_python(), "-m", "ruff", "format", "--check", "backend/src", "backend/tests", "tools"]
    )
    _run([_venv_python(), "-m", "ruff", "check", "backend/src", "backend/tests", "tools"])


def type_check() -> None:
    _run([_venv_python(), "-m", "mypy"])


def dependency_check() -> None:
    _run([_venv_python(), "tools/check_imports.py"])


def generated_check() -> None:
    _run([_venv_python(), "tools/gen_enums.py", "--check"])
    _run([_venv_python(), "tools/gen_transitions.py", "--check"])
    _run([_venv_python(), "tools/gen_openapi.py", "--check"])


def pytest(*args: str) -> None:
    build = ROOT / "build"
    build.mkdir(exist_ok=True)
    _run(
        [
            _venv_python(),
            "-m",
            "pytest",
            "-q",
            "--junitxml=build/junit.xml",
            *args,
        ]
    )


def tests() -> None:
    pytest("-m", "not integration")


def integration_tests() -> None:
    pytest("-m", "integration")


def acceptance_tests() -> None:
    pytest("backend/tests/acceptance", "-m", "not integration")


def traceability() -> None:
    _run(
        [
            _venv_python(),
            "tools/spec_trace.py",
            "--junit",
            "build/junit.xml",
            "--strict",
            "--write",
        ]
    )


def check() -> None:
    sync()
    format_check()
    type_check()
    dependency_check()
    tests()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "target",
        nargs="?",
        default="check",
        choices=[
            "check",
            "sync",
            "fmt",
            "test",
            "test-acceptance",
            "integration",
            "spec-trace",
            "gen-transitions",
            "gen-enums",
            "verify-chain",
            "db-up",
            "db-down",
        ],
    )
    args = parser.parse_args(argv)

    if args.target == "sync":
        sync()
    elif args.target == "fmt":
        sync()
        fmt()
    elif args.target == "test":
        sync()
        tests()
    elif args.target == "test-acceptance":
        sync()
        acceptance_tests()
    elif args.target == "integration":
        sync()
        integration_tests()
    elif args.target == "spec-trace":
        sync()
        traceability()
    elif args.target == "gen-transitions":
        sync()
        _run([_venv_python(), "tools/gen_transitions.py"])
    elif args.target == "gen-enums":
        sync()
        _run([_venv_python(), "tools/gen_enums.py"])
    elif args.target == "verify-chain":
        sync()
        _run([_venv_python(), "tools/verify_chain.py"])
    elif args.target == "db-up":
        _run(["docker", "compose", "-f", "ops/compose.yaml", "up", "-d", "--wait", "db"])
    elif args.target == "db-down":
        _run(["docker", "compose", "-f", "ops/compose.yaml", "down", "-v"])
    else:
        check()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
