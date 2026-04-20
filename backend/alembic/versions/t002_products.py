"""Create products table

Revision ID: t002_products
Revises: t000_settings
Create Date: 2026-04-04

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

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
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("sku", sa.String(50), unique=True, nullable=True),
        sa.Column(
            "category_id",
            postgresql.UUID(as_uuid=True),
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
    op.create_check_constraint("chk_base_price_positive", "products", "base_price >= 0")
    op.create_check_constraint(
        "chk_selling_price_gte_base", "products", "selling_price >= base_price"
    )
    op.create_check_constraint(
        "chk_stock_non_negative", "products", "stock_quantity >= 0"
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
