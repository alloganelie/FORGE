"""MS-0 : fondations PostgreSQL, invariants et journal.

Revision ID: 0001_foundations
Revises:
Create Date: 2026-10-23

Les types enumeres sont generes depuis la specification (0001_enums.sql).
Le schema porte les invariants IV-05, IV-12, IV-13, IV-14, RB-114 et les
declencheurs d'immuabilite (ET-018, ET-021, ET-022, ET-027, ET-029).
"""

from __future__ import annotations

from pathlib import Path

from alembic import op

revision = "0001_foundations"
down_revision = None
branch_labels = None
depends_on = None

SQL_DIR = Path(__file__).resolve().parent.parent / "sql"


def _execute(filename: str) -> None:
    op.execute((SQL_DIR / filename).read_text(encoding="utf-8"))


def upgrade() -> None:
    _execute("0001_enums.sql")
    _execute("0002_schema.sql")


def downgrade() -> None:
    _execute("0003_downgrade.sql")
