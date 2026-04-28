"""Create sale_items table

Revision ID: t005_sale_items
Revises: t004_sales
Create Date: 2026-04-04

"""

from alembic import op
import sqlalchemy as sa

revision = "t005_sale_items"
down_revision = "t004_sales"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "sale_items",
        sa.Column(
            "id",
            sa.String(length=36),
            primary_key=True,
        ),
        sa.Column(
            "sale_id",
            sa.String(length=36),
            sa.ForeignKey("sales.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "product_id",
            sa.String(length=36),
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
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column("user_id", sa.String(length=36), nullable=True),
        sa.Column("branch_id", sa.String(length=36), nullable=True),
        sa.CheckConstraint("quantity > 0", name="chk_quantity_positive"),
        sa.CheckConstraint("unit_price >= 0", name="chk_unit_price_positive"),
        sa.CheckConstraint("line_total >= 0", name="chk_line_total_positive"),
    )

    # Create index
    op.create_index("idx_sale_items_sale", "sale_items", ["sale_id"])


def downgrade() -> None:
    op.drop_index("idx_sale_items_sale", "sale_items")
    op.drop_table("sale_items")
