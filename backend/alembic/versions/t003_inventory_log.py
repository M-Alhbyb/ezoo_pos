"""Create inventory_log table

Revision ID: t003_inventory_log
Revises: t002_products
Create Date: 2026-04-04

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "t003_inventory_log"
down_revision = "t002_products"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "inventory_log",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "product_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("products.id"),
            nullable=False,
        ),
        sa.Column("delta", sa.Integer, nullable=False),
        sa.Column("reason", sa.String(20), nullable=False),
        sa.Column("reference_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("balance_after", sa.Integer, nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("branch_id", postgresql.UUID(as_uuid=True), nullable=True),
    )

    # Add CHECK constraint
    op.create_check_constraint(
        "chk_balance_non_negative", "inventory_log", "balance_after >= 0"
    )

    # Create indexes
    op.create_index(
        "idx_inventory_log_product",
        "inventory_log",
        ["product_id", sa.text("created_at DESC")],
    )
    op.create_index(
        "idx_inventory_log_reference",
        "inventory_log",
        ["reference_id"],
        postgresql_where=sa.text("reference_id IS NOT NULL"),
    )


def downgrade() -> None:
    op.drop_index("idx_inventory_log_reference", "inventory_log")
    op.drop_index("idx_inventory_log_product", "inventory_log")
    op.drop_table("inventory_log")
