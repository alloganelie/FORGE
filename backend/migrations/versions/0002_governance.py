"""MS-1 : gouvernance versionnee, roles et epinglage.

Revision ID: 0002_governance
Revises: 0001_foundations
"""

from __future__ import annotations

from pathlib import Path

from alembic import op

revision = "0002_governance"
down_revision = "0001_foundations"
branch_labels = None
depends_on = None

SQL_DIR = Path(__file__).resolve().parent.parent / "sql"


def _execute(filename: str) -> None:
    op.execute((SQL_DIR / filename).read_text(encoding="utf-8"))


def upgrade() -> None:
    _execute("0004_governance.sql")


def downgrade() -> None:
    _execute("0005_governance_downgrade.sql")
