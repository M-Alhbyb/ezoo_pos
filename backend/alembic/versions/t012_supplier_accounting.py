"""add supplier accounting tables

Revision ID: t012_supplier_accounting
Revises: 66f9164d52fd
Create Date: 2026-04-20

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

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
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            primary_key=True,
        ),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("phone", sa.String(50), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )

    # Create purchases table
    op.create_table(
        "purchases",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            primary_key=True,
        ),
        sa.Column(
            "supplier_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("suppliers.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("total_amount", sa.Numeric(12, 2), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )

    # Create purchase_items table
    op.create_table(
        "purchase_items",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            primary_key=True,
        ),
        sa.Column(
            "purchase_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("purchases.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "product_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("products.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("unit_cost", sa.Numeric(12, 2), nullable=False),
        sa.Column("total_cost", sa.Numeric(12, 2), nullable=False),
    )

    # Create supplier_ledger table
    op.create_table(
        "supplier_ledger",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            primary_key=True,
        ),
        sa.Column(
            "supplier_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("suppliers.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("type", sa.String(20), nullable=False),
        sa.Column("amount", sa.Numeric(12, 2), nullable=False),
        sa.Column(
            "reference_id",
            postgresql.UUID(as_uuid=True),
            nullable=True,
        ),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
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

    # Add CHECK constraints
    op.create_check_constraint(
        "check_supplier_ledger_type",
        "supplier_ledger",
        "type IN ('PURCHASE', 'PAYMENT', 'RETURN')",
    )
    op.create_check_constraint(
        "check_supplier_ledger_amount_positive",
        "supplier_ledger",
        "amount > 0",
    )
    op.create_check_constraint(
        "check_purchase_total_amount_positive",
        "purchases",
        "total_amount >= 0",
    )
    op.create_check_constraint(
        "check_purchase_item_quantity_positive",
        "purchase_items",
        "quantity > 0",
    )
    op.create_check_constraint(
        "check_purchase_item_costs_positive",
        "purchase_items",
        "unit_cost >= 0 AND total_cost >= 0",
    )


def downgrade():
    op.drop_table("supplier_ledger")
    op.drop_table("purchase_items")
    op.drop_table("purchases")
    op.drop_table("suppliers")
