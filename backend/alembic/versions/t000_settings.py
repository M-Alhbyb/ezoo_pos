"""Create settings table (Phase 0 Foundation)

Revision ID: t000_settings
Revises: t000_payment_methods
Create Date: 2026-04-04

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "t000_settings"
down_revision = "t000_payment_methods"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create settings table
    op.create_table(
        "settings",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("key", sa.String(50), nullable=False, unique=True),
        sa.Column("value", postgresql.JSONB, nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )


def downgrade() -> None:
    op.drop_table("settings")
