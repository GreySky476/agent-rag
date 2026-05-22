"""add processing_status to file_index

Revision ID: 8e4f4g3d2e7b
Revises: 7d3f3e2b1c6a
Create Date: 2026-05-22 19:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "8e4f4g3d2e7b"
down_revision: Union[str, None] = "7d3f3e2b1c6a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "file_index",
        sa.Column(
            "processing_status",
            sa.String(length=20),
            server_default="pending",
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_column("file_index", "processing_status")
