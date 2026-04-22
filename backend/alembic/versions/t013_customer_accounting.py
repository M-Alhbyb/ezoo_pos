"""add customer accounting tables

Revision ID: t013_customer_accounting
Revises: t012_supplier_accounting
Create Date: 2026-04-21

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "t013_customer_accounting"
down_revision = "t012_supplier_accounting"
branch_labels = None
depends_on = None


def upgrade():
    # Create customers table
    op.create_table(
        "customers",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            primary_key=True,
        ),
        sa.Column("name", sa.String(255), nullable=False, unique=True),
        sa.Column("phone", sa.String(50), nullable=False),
        sa.Column("address", sa.Text(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("credit_limit", sa.Numeric(12, 2), server_default="0.00", nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )

    # Create customer_ledger table
    op.create_table(
        "customer_ledger",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            primary_key=True,
        ),
        sa.Column(
            "customer_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("customers.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("type", sa.String(20), nullable=False),
        sa.Column("amount", sa.Numeric(12, 2), nullable=False),
        sa.Column(
            "reference_id",
            postgresql.UUID(as_uuid=True),
            nullable=True,
        ),
        sa.Column("payment_method", sa.String(100), nullable=True),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )

    # Add customer_id to sales table
    op.add_column(
        "sales",
        sa.Column(
            "customer_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("customers.id", ondelete="RESTRICT"),
            nullable=True,
        ),
    )

    # Add indexes
    op.create_index("idx_customer_ledger_customer", "customer_ledger", ["customer_id", "created_at"])
    op.create_index("idx_customer_ledger_type", "customer_ledger", ["customer_id", "type"])
    op.create_index("idx_sales_customer", "sales", ["customer_id"])

    # Add CHECK constraints
    op.create_check_constraint(
        "check_customer_ledger_type",
        "customer_ledger",
        "type IN ('SALE', 'PAYMENT', 'RETURN')",
    )
    op.create_check_constraint(
        "check_customer_credit_limit_non_negative",
        "customers",
        "credit_limit >= 0",
    )


def downgrade():
    op.drop_index("idx_sales_customer", table_name="sales")
    op.drop_column("sales", "customer_id")
    op.drop_table("customer_ledger")
    op.drop_table("customers")
