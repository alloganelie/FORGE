#!/usr/bin/env python3
"""Demonstration lisible par le Product Owner : journal et refus d'ecriture.

Cree des donnees de demonstration dans une transaction, verifie la chaine,
tente des contournements, puis annule tout. Aucune donnee n'est conservee.
"""

from __future__ import annotations

import os
from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy import create_engine, text
from sqlalchemy.exc import DBAPIError

from agent.ledger.api import append_event, verify_chain

DEFAULT_URL = "postgresql+psycopg://agent:agent@localhost:55432/agent"


def main() -> int:
    url = os.environ.get("AGENT_DATABASE_URL", DEFAULT_URL)
    workspace, user, request = uuid4(), uuid4(), uuid4()
    at = datetime.now(UTC)
    engine = create_engine(url)
    with engine.connect() as connection:
        transaction = connection.begin()
        try:
            connection.execute(
                text("SELECT set_config('app.workspace_id', :value, true)"),
                {"value": str(workspace)},
            )
            connection.execute(
                text("SELECT set_config('app.user_id', :value, true)"),
                {"value": str(user)},
            )
            connection.execute(text("SELECT set_config('app.role', 'responsible', true)"))
            connection.execute(
                text("INSERT INTO workspaces (id, name, created_at) VALUES (:id, :name, :at)"),
                {"id": workspace, "name": "Demonstration", "at": at},
            )
            connection.execute(
                text(
                    """
                    INSERT INTO users (id, workspace_id, display_name, role, created_at)
                    VALUES (:id, :workspace_id, 'Demonstration', 'responsible', :at)
                    """
                ),
                {"id": user, "workspace_id": workspace, "at": at},
            )
            connection.execute(
                text(
                    """
                    INSERT INTO requests
                      (id, workspace_id, author_id, original_text, state, created_at)
                    VALUES (:id, :workspace_id, :author_id, 'Demonstration', 'received', :at)
                    """
                ),
                {"id": request, "workspace_id": workspace, "author_id": user, "at": at},
            )

            print("1. Ajout de trois evenements dans le journal")
            for number in (1, 2, 3):
                event = append_event(
                    connection,
                    workspace_id=workspace,
                    request_id=request,
                    event_type="DemoEvent",
                    payload={"numero": number},
                    actor_type="human",
                    actor_id=user,
                    at=at,
                )
                print(f"   - evenement {number} : request_seq={event.request_seq}")

            print("2. Verification de la chaine")
            result = verify_chain(connection, workspace)
            print(f"   - {result.checked} evenements, resultat : {'OK' if result.ok else 'ECHEC'}")

            print("3. Tentative de modification d'un evenement")
            try:
                with connection.begin_nested():
                    connection.execute(text("UPDATE ledger_events SET payload = '{}'"))
                print("   - ECHEC DE LA DEMONSTRATION : la modification a ete acceptee")
            except DBAPIError as exc:
                print(f"   - refusee : {str(exc.orig).splitlines()[0]}")

            print("4. Tentative de suppression d'un evenement")
            try:
                with connection.begin_nested():
                    connection.execute(text("DELETE FROM ledger_events"))
                print("   - ECHEC DE LA DEMONSTRATION : la suppression a ete acceptee")
            except DBAPIError as exc:
                print(f"   - refusee : {str(exc.orig).splitlines()[0]}")

            print("5. Tentative de changement d'etat hors moteur de transitions")
            try:
                with connection.begin_nested():
                    connection.execute(
                        text("UPDATE requests SET state = 'producing' WHERE id = :id"),
                        {"id": request},
                    )
                print("   - ECHEC DE LA DEMONSTRATION : le changement a ete accepte")
            except DBAPIError as exc:
                print(f"   - refuse : {str(exc.orig).splitlines()[0]}")

            print("6. Fin : transaction annulee, aucune donnee de demonstration conservee.")
            return 0
        finally:
            transaction.rollback()
            engine.dispose()


if __name__ == "__main__":
    raise SystemExit(main())
