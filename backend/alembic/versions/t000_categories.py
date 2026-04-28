"""Create categories table (Phase 0 Foundation)

Revision ID: t000_categories
Revises:
Create Date: 2026-04-04

"""

from alembic import op
import sqlalchemy as sa

revision = "t000_categories"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create categories table
    op.create_table(
        "categories",
        sa.Column(
            "id",
            sa.String(length=36),
            primary_key=True,
        ),
        sa.Column("name", sa.String(100), nullable=False, unique=True),
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
        sa.Column("user_id", sa.String(length=36), nullable=True),
        sa.Column("branch_id", sa.String(length=36), nullable=True),
    )

    # Create index
    op.create_index("idx_categories_name", "categories", ["name"])


def downgrade() -> None:
    op.drop_index("idx_categories_name", "categories")
    op.drop_table("categories")
