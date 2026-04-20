"""add partner profit tracking

Revision ID: 73cb9f780be4
Revises: 940b0a6a564e
Create Date: 2026-04-08

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "73cb9f780be4"
down_revision = "940b0a6a564e"
branch_labels = None
depends_on = None


def upgrade():
    # Create product_assignments table
    op.create_table(
        "product_assignments",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            primary_key=True,
        ),
        sa.Column(
            "partner_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("partners.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column(
            "product_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("products.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("assigned_quantity", sa.Integer(), nullable=False),
        sa.Column(
            "remaining_quantity", sa.Integer(), nullable=False, server_default="0"
        ),
        sa.Column("share_percentage", sa.Numeric(5, 2), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="active"),
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
        sa.Column("fulfilled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_by",
            postgresql.UUID(as_uuid=True),
            nullable=True,
        ),
        sa.Column(
            "branch_id",
            postgresql.UUID(as_uuid=True),
            nullable=True,
        ),
    )

    # Add unique constraint for one partner per product
    op.create_index(
        "idx_product_assignments_product_active",
        "product_assignments",
        ["product_id", "status"],
        unique=False,
        postgresql_where=sa.text("status = 'active'"),
    )

    # Create partner_wallet_transactions table
    op.create_table(
        "partner_wallet_transactions",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            primary_key=True,
        ),
        sa.Column(
            "partner_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("partners.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("amount", sa.Numeric(12, 2), nullable=False),
        sa.Column(
            "transaction_type",
            sa.String(50),
            nullable=False,
        ),
        sa.Column(
            "reference_id",
            postgresql.UUID(as_uuid=True),
            nullable=True,
        ),
        sa.Column(
            "reference_type",
            sa.String(50),
            nullable=True,
        ),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "balance_after",
            sa.Numeric(12, 2),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "created_by",
            postgresql.UUID(as_uuid=True),
            nullable=True,
        ),
    )

    # Add indexes for partner_wallet_transactions
    op.create_index(
        "idx_partner_wallet_transactions_partner",
        "partner_wallet_transactions",
        ["partner_id", "created_at"],
    )

    # Add CHECK constraints
    op.create_check_constraint(
        "check_partner_wallet_amount_nonzero",
        "partner_wallet_transactions",
        "amount != 0",
    )


def downgrade():
    op.drop_table("partner_wallet_transactions")
    op.drop_table("product_assignments")
