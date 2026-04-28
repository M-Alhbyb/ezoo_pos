"""add supplier accounting tables

Revision ID: t012_supplier_accounting
Revises: 66f9164d52fd
Create Date: 2026-04-20

"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "t012_supplier_accounting"
down_revision = "66f9164d52fd"
branch_labels = None
depends_on = None


def upgrade():
    # Create suppliers table
    op.create_table(
        "suppliers",
        sa.Column(
            "id",
            sa.String(length=36),
            primary_key=True,
        ),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("phone", sa.String(50), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
    )

    # Create purchases table
    op.create_table(
        "purchases",
        sa.Column(
            "id",
            sa.String(length=36),
            primary_key=True,
        ),
        sa.Column(
            "supplier_id",
            sa.String(length=36),
            sa.ForeignKey("suppliers.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("total_amount", sa.Numeric(12, 2), nullable=False),
        sa.CheckConstraint("total_amount >= 0", name="check_purchase_total_amount_positive"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
    )

    # Create purchase_items table
    op.create_table(
        "purchase_items",
        sa.Column(
            "id",
            sa.String(length=36),
            primary_key=True,
        ),
        sa.Column(
            "purchase_id",
            sa.String(length=36),
            sa.ForeignKey("purchases.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "product_id",
            sa.String(length=36),
            sa.ForeignKey("products.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("unit_cost", sa.Numeric(12, 2), nullable=False),
        sa.Column("total_cost", sa.Numeric(12, 2), nullable=False),
        sa.CheckConstraint("quantity > 0", name="check_purchase_item_quantity_positive"),
        sa.CheckConstraint("unit_cost >= 0 AND total_cost >= 0", name="check_purchase_item_costs_positive"),
    )

    # Create supplier_ledger table
    op.create_table(
        "supplier_ledger",
        sa.Column(
            "id",
            sa.String(length=36),
            primary_key=True,
        ),
        sa.Column(
            "supplier_id",
            sa.String(length=36),
            sa.ForeignKey("suppliers.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("type", sa.String(20), nullable=False),
        sa.Column("amount", sa.Numeric(12, 2), nullable=False),
        sa.Column(
            "reference_id",
            sa.String(length=36),
            nullable=True,
        ),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.CheckConstraint("type IN ('PURCHASE', 'PAYMENT', 'RETURN')", name="check_supplier_ledger_type"),
        sa.CheckConstraint("amount > 0", name="check_supplier_ledger_amount_positive"),
    )

    # Add indexes
    op.create_index("idx_purchases_supplier", "purchases", ["supplier_id"])
    op.create_index("idx_purchase_items_purchase", "purchase_items", ["purchase_id"])
    op.create_index("idx_purchase_items_product", "purchase_items", ["product_id"])
    op.create_index(
        "idx_supplier_ledger_supplier", "supplier_ledger", ["supplier_id", "created_at"]
    )
    op.create_index(
        "idx_supplier_ledger_type", "supplier_ledger", ["supplier_id", "type"]
    )


def downgrade():
    op.drop_table("supplier_ledger")
    op.drop_table("purchase_items")
    op.drop_table("purchases")
    op.drop_table("suppliers")
