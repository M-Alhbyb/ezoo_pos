"""Create products table

Revision ID: t002_products
Revises: t000_settings
Create Date: 2026-04-04

"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "t002_products"
down_revision = "t000_settings"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create products table
    op.create_table(
        "products",
        sa.Column(
            "id",
            sa.String(length=36),
            primary_key=True,
        ),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("sku", sa.String(50), unique=True, nullable=True),
        sa.Column(
            "category_id",
            sa.String(length=36),
            sa.ForeignKey("categories.id"),
            nullable=False,
        ),
        sa.Column("base_price", sa.Numeric(12, 2), nullable=False),
        sa.Column("selling_price", sa.Numeric(12, 2), nullable=False),
        sa.Column("stock_quantity", sa.Integer, nullable=False, server_default="0"),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
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
        sa.CheckConstraint("base_price >= 0", name="chk_base_price_positive"),
        sa.CheckConstraint("selling_price >= base_price", name="chk_selling_price_gte_base"),
        sa.CheckConstraint("stock_quantity >= 0", name="chk_stock_non_negative"),
    )

    # Create indexes
    op.create_index(
        "idx_products_name",
        "products",
        ["name"],
        postgresql_using="gin",
        postgresql_ops={"name": "gin_trgm_ops"},
    )
    op.create_index(
        "idx_products_sku",
        "products",
        ["sku"],
        postgresql_where=sa.text("sku IS NOT NULL"),
    )
    op.create_index("idx_products_category", "products", ["category_id"])
    op.create_index("idx_products_active", "products", ["is_active"])


def downgrade() -> None:
    op.drop_index("idx_products_active", "products")
    op.drop_index("idx_products_category", "products")
    op.drop_index("idx_products_sku", "products")
    op.drop_index("idx_products_name", "products")
    op.drop_table("products")
