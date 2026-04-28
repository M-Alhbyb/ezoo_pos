"""Create inventory_log table

Revision ID: t003_inventory_log
Revises: t002_products
Create Date: 2026-04-04

"""

from alembic import op
import sqlalchemy as sa

revision = "t003_inventory_log"
down_revision = "t002_products"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "inventory_log",
        sa.Column(
            "id",
            sa.String(length=36),
            primary_key=True,
        ),
        sa.Column(
            "product_id",
            sa.String(length=36),
            sa.ForeignKey("products.id"),
            nullable=False,
        ),
        sa.Column("delta", sa.Integer, nullable=False),
        sa.Column("reason", sa.String(20), nullable=False),
        sa.Column("reference_id", sa.String(length=36), nullable=True),
        sa.Column("balance_after", sa.Integer, nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column("user_id", sa.String(length=36), nullable=True),
        sa.Column("branch_id", sa.String(length=36), nullable=True),
        sa.CheckConstraint("balance_after >= 0", name="chk_balance_non_negative"),
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
