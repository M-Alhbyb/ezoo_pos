"""add missing updated_at columns

Revision ID: t010_add_updated_at
Revises: t009_seed_fee_presets
Create Date: 2026-04-05 15:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 't010_add_updated_at'
down_revision = 't009_seed_fee_presets'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add updated_at to inventory_log
    op.add_column('inventory_log', sa.Column(
        'updated_at', 
        sa.DateTime(timezone=True), 
        nullable=False, 
        server_default=sa.func.now(),
        onupdate=sa.func.now()
    ))
    
    # Add updated_at to sale_items
    op.add_column('sale_items', sa.Column(
        'updated_at', 
        sa.DateTime(timezone=True), 
        nullable=False, 
        server_default=sa.func.now(),
        onupdate=sa.func.now()
    ))
    
    # Add updated_at to sale_fees
    op.add_column('sale_fees', sa.Column(
        'updated_at', 
        sa.DateTime(timezone=True), 
        nullable=False, 
        server_default=sa.func.now(),
        onupdate=sa.func.now()
    ))
    
    # Add updated_at to sale_reversals
    op.add_column('sale_reversals', sa.Column(
        'updated_at', 
        sa.DateTime(timezone=True), 
        nullable=False, 
        server_default=sa.func.now(),
        onupdate=sa.func.now()
    ))


def downgrade() -> None:
    op.drop_column('sale_reversals', 'updated_at')
    op.drop_column('sale_fees', 'updated_at')
    op.drop_column('sale_items', 'updated_at')
    op.drop_column('inventory_log', 'updated_at')
