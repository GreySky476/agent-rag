"""add created_at to file_index

Revision ID: 7d3f3e2b1c6a
Revises: 6c2e8f1a9d4b
Create Date: 2026-05-22 17:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "7d3f3e2b1c6a"
down_revision: Union[str, None] = "6c2e8f1a9d4b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "file_index",
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_column("file_index", "created_at")
