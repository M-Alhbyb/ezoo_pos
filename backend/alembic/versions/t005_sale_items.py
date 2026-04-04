"""Create sale_items table

Revision ID: t005_sale_items
Revises: t004_sales
Create Date: 2026-04-04

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "t005_sale_items"
down_revision = "t004_sales"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "sale_items",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "sale_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("sales.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "product_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("products.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("product_name", sa.String(200), nullable=False),
        sa.Column("quantity", sa.Integer, nullable=False),
        sa.Column("unit_price", sa.Numeric(12, 2), nullable=False),
        sa.Column("line_total", sa.Numeric(12, 2), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("branch_id", postgresql.UUID(as_uuid=True), nullable=True),
    )

    # Add CHECK constraints
    op.create_check_constraint("chk_quantity_positive", "sale_items", "quantity > 0")
    op.create_check_constraint(
        "chk_unit_price_positive", "sale_items", "unit_price >= 0"
    )
    op.create_check_constraint(
        "chk_line_total_positive", "sale_items", "line_total >= 0"
    )

    # Create index
    op.create_index("idx_sale_items_sale", "sale_items", ["sale_id"])


def downgrade() -> None:
    op.drop_index("idx_sale_items_sale", "sale_items")
    op.drop_table("sale_items")
