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


def decimal_check() -> None:
    _run([_venv_python(), "tools/check_decimal.py"])


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


def all_tests() -> None:
    pytest()


def integration_tests() -> None:
    pytest("-m", "integration")


def acceptance_tests() -> None:
    pytest("backend/tests/acceptance")


def ensure_database() -> None:
    """Demarre PostgreSQL local si la base de test n'est pas joignable."""
    url = os.environ.get(
        "FORGE_TEST_DATABASE_URL",
        os.environ.get(
            "AGENT_TEST_DATABASE_URL",
            "postgresql+psycopg://agent:agent@localhost:55432/agent_test",
        ),
    ).replace("+psycopg", "")
    admin_url = url.rsplit("/", 1)[0] + "/postgres"
    probe = (
        "import os, psycopg; "
        "psycopg.connect(os.environ['CHECK_DB_URL'], connect_timeout=3); "
        "print('PostgreSQL joignable')"
    )
    env_probe = dict(os.environ, CHECK_DB_URL=admin_url)
    completed = subprocess.run([_venv_python(), "-c", probe], cwd=ROOT, env=env_probe, check=False)
    if completed.returncode != 0:
        print("PostgreSQL local indisponible : demarrage du conteneur...")
        _run(["docker", "compose", "-f", "ops/compose.yaml", "up", "-d", "--wait", "db"])


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
    ensure_database()
    format_check()
    type_check()
    dependency_check()
    decimal_check()
    generated_check()
    all_tests()
    traceability()


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
            "tst18",
            "integration",
            "spec-trace",
            "gen-transitions",
            "gen-enums",
            "verify-chain",
            "demo-ledger",
            "demo-governance",
            "demo-requests",
            "seed-governance",
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
        ensure_database()
        acceptance_tests()
    elif args.target == "tst18":
        sync()
        pytest("backend/tests/property/test_tst18.py")
    elif args.target == "integration":
        sync()
        integration_tests()
    elif args.target == "spec-trace":
        sync()
        all_tests()
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
    elif args.target == "demo-ledger":
        sync()
        _run([_venv_python(), "tools/demo_ledger.py"])
    elif args.target == "demo-governance":
        sync()
        _run([_venv_python(), "tools/demo_governance.py"])
    elif args.target == "demo-requests":
        sync()
        _run([_venv_python(), "tools/demo_requests.py"])
    elif args.target == "seed-governance":
        sync()
        _run([_venv_python(), "tools/seed_governance_demo.py"])
    elif args.target == "db-up":
        _run(["docker", "compose", "-f", "ops/compose.yaml", "up", "-d", "--wait", "db"])
    elif args.target == "db-down":
        _run(["docker", "compose", "-f", "ops/compose.yaml", "down", "-v"])
    else:
        check()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
