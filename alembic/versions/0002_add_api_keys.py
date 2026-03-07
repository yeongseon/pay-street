# pyright: reportMissingImports=false
"""Add api_keys table."""

from collections.abc import Sequence
from typing import Optional, Union

import alembic.op as op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0002_add_api_keys"
down_revision: Optional[str] = "0001_initial_schema"
branch_labels: Optional[Union[str, Sequence[str]]] = None
depends_on: Optional[Union[str, Sequence[str]]] = None


def upgrade() -> None:
    op.create_table(
        "api_keys",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("provider", sa.String(length=50), nullable=False),
        sa.Column("key_value", sa.Text(), nullable=False),
        sa.Column("label", sa.String(length=200), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("provider"),
    )
    op.create_index("ix_api_keys_provider", "api_keys", ["provider"])


def downgrade() -> None:
    op.drop_index("ix_api_keys_provider", table_name="api_keys")
    op.drop_table("api_keys")
