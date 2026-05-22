"""add title and updated_at to agent_traces

Revision ID: 6c2e8f1a9d4b
Revises: 4a2fb1c77a65
Create Date: 2026-05-22 17:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "6c2e8f1a9d4b"
down_revision: Union[str, None] = "4a2fb1c77a65"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "agent_traces",
        sa.Column("title", sa.String(length=200), nullable=True),
    )
    op.add_column(
        "agent_traces",
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_column("agent_traces", "updated_at")
    op.drop_column("agent_traces", "title")
