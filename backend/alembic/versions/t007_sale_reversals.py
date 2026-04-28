"""Create sale_reversals table

Revision ID: t007_sale_reversals
Revises: t006_sale_fees
Create Date: 2026-04-04

"""

from alembic import op
import sqlalchemy as sa

revision = "t007_sale_reversals"
down_revision = "t006_sale_fees"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "sale_reversals",
        sa.Column(
            "id",
            sa.String(length=36),
            primary_key=True,
        ),
        sa.Column(
            "original_sale_id",
            sa.String(length=36),
            sa.ForeignKey("sales.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column(
            "reversal_sale_id",
            sa.String(length=36),
            sa.ForeignKey("sales.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("reason", sa.Text, nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column("user_id", sa.String(length=36), nullable=True),
        sa.Column("branch_id", sa.String(length=36), nullable=True),
    )

    # Create index
    op.create_index(
        "idx_sale_reversals_original", "sale_reversals", ["original_sale_id"]
    )


def downgrade() -> None:
    op.drop_index("idx_sale_reversals_original", "sale_reversals")
    op.drop_table("sale_reversals")
