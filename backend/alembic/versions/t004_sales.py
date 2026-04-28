"""Create sales table

Revision ID: t004_sales
Revises: t003_inventory_log
Create Date: 2026-04-04

"""

from alembic import op
import sqlalchemy as sa

revision = "t004_sales"
down_revision = "t003_inventory_log"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "sales",
        sa.Column(
            "id",
            sa.String(length=36),
            primary_key=True,
        ),
        sa.Column(
            "payment_method_id",
            sa.String(length=36),
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
        sa.CheckConstraint("subtotal >= 0", name="chk_subtotal_positive"),
        sa.CheckConstraint("fees_total >= 0", name="chk_fees_positive"),
        sa.CheckConstraint("total >= 0", name="chk_total_positive"),
    )

    # Create indexes
    op.create_index("idx_sales_created_at", "sales", [sa.text("created_at DESC")])
    op.create_index("idx_sales_payment_method", "sales", ["payment_method_id"])


def downgrade() -> None:
    op.drop_index("idx_sales_payment_method", "sales")
    op.drop_index("idx_sales_created_at", "sales")
    op.drop_table("sales")
