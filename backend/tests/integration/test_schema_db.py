"""ET-013, ET-018, ET-019, ET-021, ET-027, ET-029, ET-036 : invariants en base."""

from __future__ import annotations

import os
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from uuid import UUID

import psycopg
import pytest
from sqlalchemy import Connection, text
from sqlalchemy.engine import make_url
from sqlalchemy.exc import DBAPIError
from tools.gen_enums import build_enums

ROOT = Path(__file__).resolve().parents[3]
DB_URL = os.environ.get(
    "AGENT_TEST_DATABASE_URL", "postgresql+psycopg://agent:agent@localhost:55432/agent_test"
)
WORKSPACE_ID = UUID("11111111-1111-7111-8111-111111111111")
REQUEST_ID = UUID("44444444-4444-7444-8444-444444444444")
DELIVERABLE_ID = UUID("66666666-6666-7666-8666-666666666666")
VERSION_ID = UUID("77777777-7777-7777-8777-777777777777")
ELEMENT_ID = UUID("88888888-8888-7888-8888-888888888888")
AT = datetime(2026, 10, 23, 12, 0, tzinfo=UTC)


def _add_deliverable(connection: Connection) -> None:
    connection.execute(
        text(
            """
            INSERT INTO deliverables (id, workspace_id, request_id, type_key, target_format)
            VALUES (:id, :workspace_id, :request_id, 'note', 'md')
            """
        ),
        {"id": DELIVERABLE_ID, "workspace_id": WORKSPACE_ID, "request_id": REQUEST_ID},
    )


def _add_version(connection: Connection, **overrides: object) -> None:
    values: dict[str, object] = {
        "id": VERSION_ID,
        "workspace_id": WORKSPACE_ID,
        "deliverable_id": DELIVERABLE_ID,
        "number": 1,
        "st_v": "provisional",
        "st_c": "not_evaluated",
        "st_a": "not_submitted",
        "st_d": "not_authorized",
        "finalized_at": None,
    }
    values.update(overrides)
    connection.execute(
        text(
            """
            INSERT INTO deliverable_versions
              (id, workspace_id, deliverable_id, number, st_v, st_c, st_a, st_d, finalized_at)
            VALUES
              (:id, :workspace_id, :deliverable_id, :number, :st_v, :st_c, :st_a, :st_d,
               :finalized_at)
            """
        ),
        values,
    )


def _set_transition(connection: Connection, value: str = "TEST-TRANSITION") -> None:
    connection.execute(
        text("SELECT set_config('app.transition_id', :value, true)"), {"value": value}
    )


@pytest.mark.integration
@pytest.mark.spec("ET-017")
@pytest.mark.spec("DC-05")
def test_database_enums_match_generated_enums(seeded: Connection) -> None:
    rows = seeded.execute(
        text(
            """
            SELECT t.typname, e.enumlabel
              FROM pg_type t
              JOIN pg_enum e ON e.enumtypid = t.oid
             ORDER BY t.typname, e.enumsortorder
            """
        )
    ).all()
    found: dict[str, list[str]] = {}
    for type_name, label in rows:
        found.setdefault(str(type_name), []).append(str(label))
    for definition in build_enums():
        assert found[definition.sql_name] == list(definition.values), definition.sql_name


@pytest.mark.integration
@pytest.mark.spec("ET-015")
def test_every_business_table_has_workspace_id(seeded: Connection) -> None:
    tables = seeded.execute(
        text(
            """
            SELECT table_name
              FROM information_schema.tables
             WHERE table_schema = 'public'
               AND table_name NOT IN ('workspaces', 'alembic_version')
            """
        )
    ).scalars()
    for table in tables:
        exists = seeded.execute(
            text(
                """
                SELECT 1 FROM information_schema.columns
                 WHERE table_schema = 'public' AND table_name = :table
                   AND column_name = 'workspace_id'
                """
            ),
            {"table": table},
        ).first()
        assert exists is not None, table


@pytest.mark.integration
@pytest.mark.spec("ET-029")
def test_rls_is_enabled_and_forced(seeded: Connection) -> None:
    names = (
        "requests",
        "deliverables",
        "deliverable_versions",
        "elements",
        "state_changes",
        "ledger_events",
        "control_results",
        "documents",
        "content_atoms",
        "step_runs",
    )
    rows = seeded.execute(
        text(
            """
            SELECT relname, relrowsecurity, relforcerowsecurity
              FROM pg_class
             WHERE relname = ANY(:names)
            """
        ),
        {"names": list(names)},
    ).all()
    assert len(rows) == len(names)
    for name, enabled, forced in rows:
        assert enabled is True, name
        assert forced is True, name


@pytest.mark.integration
@pytest.mark.spec("ET-021")
def test_expected_triggers_exist(seeded: Connection) -> None:
    rows = seeded.execute(text("SELECT tgname FROM pg_trigger WHERE NOT tgisinternal")).scalars()
    found = set(rows)
    expected = {
        "ledger_append_only",
        "ledger_chain",
        "ledger_no_truncate",
        "control_results_append_only",
        "documents_immutable",
        "state_changes_append_only",
        "finalized_protect",
        "atoms_protect",
        "elements_protect",
        "requests_state_guard",
        "versions_state_guard",
        "elements_state_guard",
        "request_final_protect",
        "request_finalization_check",
        "version_finalization_check",
    }
    assert expected <= found


@pytest.mark.integration
@pytest.mark.spec("ET-018")
def test_version_constraints_enforce_three_independent_axes(seeded: Connection) -> None:
    _add_deliverable(seeded)
    with pytest.raises(DBAPIError, match="finalized_requires_conforming"):
        with seeded.begin_nested():
            _add_version(seeded, st_v="finalized", st_c="not_evaluated", finalized_at=AT)
    with pytest.raises(DBAPIError, match="approval_requires_finalized"), seeded.begin_nested():
        _add_version(seeded, st_v="provisional", st_c="conforming", st_a="approved")
    savepoint = seeded.begin_nested()
    _add_version(seeded, st_v="provisional", st_c="conforming", st_a="not_submitted")
    _set_transition(seeded)
    with pytest.raises(DBAPIError, match="diffusion_requires_finalized_and_approved"):
        seeded.execute(
            text("UPDATE deliverable_versions SET st_d = 'authorized' WHERE id = :id"),
            {"id": VERSION_ID},
        )
    savepoint.rollback()


@pytest.mark.integration
@pytest.mark.spec("ET-036")
def test_state_change_is_refused_outside_the_engine(seeded: Connection) -> None:
    with pytest.raises(DBAPIError, match="hors moteur"), seeded.begin_nested():
        seeded.execute(
            text("UPDATE requests SET state = 'producing' WHERE id = :id"), {"id": REQUEST_ID}
        )
    _set_transition(seeded)
    seeded.execute(
        text("UPDATE requests SET state = 'producing' WHERE id = :id"), {"id": REQUEST_ID}
    )
    state = seeded.execute(
        text("SELECT state FROM requests WHERE id = :id"), {"id": REQUEST_ID}
    ).scalar_one()
    assert state == "producing"


@pytest.mark.integration
@pytest.mark.spec("ET-004")
def test_finalized_request_state_is_frozen(seeded: Connection) -> None:
    _add_deliverable(seeded)
    _add_version(
        seeded,
        st_v="finalized",
        st_c="conforming",
        st_a="approved",
        st_d="not_authorized",
        finalized_at=AT,
    )
    _set_transition(seeded)
    seeded.execute(
        text("UPDATE requests SET state = 'finalized' WHERE id = :id"), {"id": REQUEST_ID}
    )
    with pytest.raises(DBAPIError, match="etat fige"), seeded.begin_nested():
        seeded.execute(
            text("UPDATE requests SET state = 'cancelled' WHERE id = :id"), {"id": REQUEST_ID}
        )


@pytest.mark.integration
@pytest.mark.spec("ET-018")
def test_version_finalization_requires_mandatory_elements(seeded: Connection) -> None:
    _add_deliverable(seeded)
    _add_version(seeded, st_v="provisional", st_c="conforming")
    seeded.execute(
        text(
            """
            INSERT INTO elements (id, workspace_id, version_id, element_key, mandatory, st_e)
            VALUES (:id, :workspace_id, :version_id, 'E1', true, 'to_produce')
            """
        ),
        {"id": ELEMENT_ID, "workspace_id": WORKSPACE_ID, "version_id": VERSION_ID},
    )
    _set_transition(seeded)
    with pytest.raises(DBAPIError, match="elements obligatoires"):
        with seeded.begin_nested():
            seeded.execute(
                text(
                    "UPDATE deliverable_versions SET st_v = 'finalized', "
                    "finalized_at = :at WHERE id = :id"
                ),
                {"id": VERSION_ID, "at": AT},
            )
    seeded.execute(
        text("UPDATE elements SET st_e = 'controlled_ok' WHERE id = :id"), {"id": ELEMENT_ID}
    )
    seeded.execute(
        text(
            "UPDATE deliverable_versions SET st_v = 'finalized', finalized_at = :at WHERE id = :id"
        ),
        {"id": VERSION_ID, "at": AT},
    )
    assert (
        seeded.execute(
            text("SELECT st_v FROM deliverable_versions WHERE id = :id"), {"id": VERSION_ID}
        ).scalar_one()
        == "finalized"
    )


@pytest.mark.integration
@pytest.mark.spec("ET-028")
def test_atoms_of_a_finalized_version_are_immutable(seeded: Connection) -> None:
    _add_deliverable(seeded)
    _add_version(seeded, st_v="provisional", st_c="conforming")
    atom_id = UUID("99999999-9999-7999-8999-999999999999")
    seeded.execute(
        text(
            """
            INSERT INTO content_atoms
              (id, workspace_id, version_id, element_key, origin, text, created_at)
            VALUES (:id, :workspace_id, :version_id, 'E1', 'quotation', 'texte', :at)
            """
        ),
        {"id": atom_id, "workspace_id": WORKSPACE_ID, "version_id": VERSION_ID, "at": AT},
    )
    _set_transition(seeded)
    seeded.execute(
        text(
            "UPDATE deliverable_versions SET st_v = 'finalized', finalized_at = :at WHERE id = :id"
        ),
        {"id": VERSION_ID, "at": AT},
    )
    with pytest.raises(DBAPIError, match="immuable"), seeded.begin_nested():
        seeded.execute(
            text("UPDATE content_atoms SET text = 'modifie' WHERE id = :id"), {"id": atom_id}
        )


@pytest.mark.integration
@pytest.mark.spec("ET-029")
def test_row_level_security_isolates_authors(seeded: Connection) -> None:
    other_request = UUID("aaaaaaaa-aaaa-7aaa-8aaa-aaaaaaaaaaaa")
    seeded.execute(
        text(
            """
            INSERT INTO requests (id, workspace_id, author_id, original_text, state, created_at)
            VALUES (:id, :workspace_id, :author_id, 'Autre demande', 'received', :at)
            """
        ),
        {
            "id": other_request,
            "workspace_id": WORKSPACE_ID,
            "author_id": UUID("33333333-3333-7333-8333-333333333333"),
            "at": AT,
        },
    )
    seeded.execute(
        text("SELECT set_config('app.user_id', :value, true)"),
        {"value": "33333333-3333-7333-8333-333333333333"},
    )
    seeded.execute(text("SELECT set_config('app.role', 'user', true)"))
    seeded.execute(text("SET LOCAL ROLE agent_app"))
    visible = seeded.execute(text("SELECT id FROM requests")).scalars().all()
    assert visible == [other_request]
    seeded.execute(text("SELECT set_config('app.role', 'responsible', true)"))
    assert len(seeded.execute(text("SELECT id FROM requests")).scalars().all()) == 2


@pytest.mark.integration
@pytest.mark.spec("ET-019")
def test_application_role_has_no_delete_privilege(seeded: Connection) -> None:
    with pytest.raises(DBAPIError, match="permission denied"), seeded.begin_nested():
        seeded.execute(text("SET LOCAL ROLE agent_app"))
        seeded.execute(text("DELETE FROM requests"))


@pytest.mark.integration
@pytest.mark.spec("ET-020")
def test_migration_upgrade_downgrade_upgrade_on_a_copy() -> None:
    admin_url = (
        make_url(DB_URL)
        .set(drivername="postgresql", database="postgres")
        .render_as_string(hide_password=False)
    )
    test_url = (
        make_url(DB_URL)
        .set(drivername="postgresql", database="agent_migration_test")
        .render_as_string(hide_password=False)
    )
    with psycopg.connect(admin_url, autocommit=True) as admin:
        admin.execute("DROP DATABASE IF EXISTS agent_migration_test WITH (FORCE)")
        admin.execute("CREATE DATABASE agent_migration_test")

    env = os.environ.copy()
    env["AGENT_DATABASE_URL"] = test_url.replace("postgresql://", "postgresql+psycopg://", 1)
    commands = [
        ["upgrade", "head"],
        ["downgrade", "base"],
        ["upgrade", "head"],
    ]
    for command in commands:
        completed = subprocess.run(
            [sys.executable, "-m", "alembic", "-c", "backend/alembic.ini", *command],
            cwd=ROOT,
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )
        assert completed.returncode == 0, completed.stderr

    with psycopg.connect(test_url) as connection:
        assert connection.execute("SELECT to_regclass('public.requests')").fetchone()[0] is not None
        assert (
            connection.execute("SELECT to_regtype('public.st_request')").fetchone()[0] is not None
        )
    with psycopg.connect(admin_url, autocommit=True) as admin:
        admin.execute("DROP DATABASE agent_migration_test WITH (FORCE)")
