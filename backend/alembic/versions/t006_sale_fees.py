"""Create sale_fees table

Revision ID: t006_sale_fees
Revises: t005_sale_items
Create Date: 2026-04-04

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "t006_sale_fees"
down_revision = "t005_sale_items"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "sale_fees",
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
        sa.Column("fee_type", sa.String(20), nullable=False),
        sa.Column("fee_label", sa.String(100), nullable=False),
        sa.Column("fee_value_type", sa.String(10), nullable=False),
        sa.Column("fee_value", sa.Numeric(12, 2), nullable=False),
        sa.Column("calculated_amount", sa.Numeric(12, 2), nullable=False),
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
    op.create_check_constraint("chk_fee_value_positive", "sale_fees", "fee_value >= 0")
    op.create_check_constraint(
        "chk_calculated_amount_positive", "sale_fees", "calculated_amount >= 0"
    )

    # Create index
    op.create_index("idx_sale_fees_sale", "sale_fees", ["sale_id"])


def downgrade() -> None:
    op.drop_index("idx_sale_fees_sale", "sale_fees")
    op.drop_table("sale_fees")
