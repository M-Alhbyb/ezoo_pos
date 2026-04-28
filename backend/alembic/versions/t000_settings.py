"""Create settings table (Phase 0 Foundation)

Revision ID: t000_settings
Revises: t000_payment_methods
Create Date: 2026-04-04

"""

from alembic import op
import sqlalchemy as sa

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
            sa.String(length=36),
            primary_key=True,
        ),
        sa.Column("key", sa.String(50), nullable=False, unique=True),
        sa.Column("value", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
    )


def downgrade() -> None:
    op.drop_table("settings")
