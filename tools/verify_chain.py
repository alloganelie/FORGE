#!/usr/bin/env python3
"""Verifie la chaine du journal de toutes les demandes (ET-025, make verify-chain)."""

from __future__ import annotations

import argparse
import os
import sys
from uuid import UUID

from sqlalchemy import create_engine, text

from agent.ledger.api import verify_chain

DEFAULT_URL = "postgresql+psycopg://agent:agent@localhost:55432/agent"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--database-url", default=os.environ.get("AGENT_DATABASE_URL", DEFAULT_URL))
    parser.add_argument("--workspace", default=None, help="UUID d'un espace de travail")
    args = parser.parse_args(argv)

    engine = create_engine(args.database_url)
    failures = 0
    checked = 0
    with engine.connect() as connection:
        transaction = connection.begin()
        if args.workspace:
            workspaces = [args.workspace]
        else:
            workspaces = [
                str(row[0]) for row in connection.execute(text("SELECT id FROM workspaces")).all()
            ]
        for workspace in workspaces:
            connection.execute(
                text("SELECT set_config('app.workspace_id', :value, true)"),
                {"value": workspace},
            )
            connection.execute(text("SELECT set_config('app.role', 'system', true)"))
            result = verify_chain(connection, UUID(workspace))
            checked += result.checked
            print(f"{workspace} : {result.checked} evenement(s), {'OK' if result.ok else 'ECHEC'}")
            for error in result.errors:
                print(f"  - {error}", file=sys.stderr)
            failures += 0 if result.ok else 1
        transaction.rollback()
    engine.dispose()
    if not workspaces:
        print("Aucun espace de travail : rien a verifier.")
    print(f"Total : {checked} evenement(s), {failures} chaine(s) en echec.")
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
