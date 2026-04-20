"""add base_cost column to products

Revision ID: 74d2e1f1c3a5
Revises: 73cb9f780be4
Create Date: 2026-04-11

"""

from alembic import op
import sqlalchemy as sa

revision = "74d2e1f1c3a5"
down_revision = "73cb9f780be4"
branch_labels = None
depends_on = None


def upgrade():
    # Add base_cost column to products table for profit calculation
    op.add_column(
        "products",
        sa.Column(
            "base_cost",
            sa.Numeric(12, 2),
            nullable=False,
            server_default="0",
        ),
    )


def downgrade():
    op.drop_column("products", "base_cost")
