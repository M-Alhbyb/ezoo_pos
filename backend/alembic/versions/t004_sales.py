"""Create sales table

Revision ID: t004_sales
Revises: t003_inventory_log
Create Date: 2026-04-04

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "t004_sales"
down_revision = "t003_inventory_log"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "sales",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "payment_method_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("payment_methods.id"),
            nullable=False,
        ),
        sa.Column("subtotal", sa.Numeric(12, 2), nullable=False),
        sa.Column("fees_total", sa.Numeric(12, 2), nullable=False, server_default="0"),
        sa.Column("vat_rate", sa.Numeric(5, 2), nullable=True),
        sa.Column("vat_amount", sa.Numeric(12, 2), nullable=True),
        sa.Column("total", sa.Numeric(12, 2), nullable=False),
        sa.Column("note", sa.Text, nullable=True),
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
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("branch_id", postgresql.UUID(as_uuid=True), nullable=True),
    )

    # Add CHECK constraints
    op.create_check_constraint("chk_subtotal_positive", "sales", "subtotal >= 0")
    op.create_check_constraint("chk_fees_positive", "sales", "fees_total >= 0")
    op.create_check_constraint("chk_total_positive", "sales", "total >= 0")

    # Create indexes
    op.create_index("idx_sales_created_at", "sales", [sa.text("created_at DESC")])
    op.create_index("idx_sales_payment_method", "sales", ["payment_method_id"])


def downgrade() -> None:
    op.drop_index("idx_sales_payment_method", "sales")
    op.drop_index("idx_sales_created_at", "sales")
    op.drop_table("sales")
