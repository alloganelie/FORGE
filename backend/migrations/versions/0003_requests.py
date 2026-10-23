"""MS-2 : demande, clarification, faisabilite, LLM et suivi.

Revision ID: 0003_requests
Revises: 0002_governance
"""

from __future__ import annotations

from pathlib import Path

from alembic import op

revision = "0003_requests"
down_revision = "0002_governance"
branch_labels = None
depends_on = None

SQL_DIR = Path(__file__).resolve().parent.parent / "sql"


def upgrade() -> None:
    op.execute((SQL_DIR / "0006_requests.sql").read_text(encoding="utf-8"))


def downgrade() -> None:
    op.execute((SQL_DIR / "0007_requests_downgrade.sql").read_text(encoding="utf-8"))
