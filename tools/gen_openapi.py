#!/usr/bin/env python3
"""Genere le contrat OpenAPI versionne (ET-002).

Le contrat est commite pour etre relu et compare ; --check echoue s'il diverge
du code FastAPI.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from agent.interfaces.rest.app import create_app
from agent.platform.config import Settings

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "backend" / "openapi.json"


def render() -> str:
    schema = create_app(Settings()).openapi()
    return json.dumps(schema, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="verifie sans ecrire")
    args = parser.parse_args(argv)
    content = render()
    current = OUT.read_text(encoding="utf-8") if OUT.exists() else None
    if args.check:
        if current != content:
            print(f"Desynchronise : {OUT.relative_to(ROOT)} (lancer python tools/gen_openapi.py)")
            return 1
        print("Contrat OpenAPI a jour")
        return 0
    OUT.write_text(content, encoding="utf-8", newline="\n")
    print(f"Ecrit : {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
