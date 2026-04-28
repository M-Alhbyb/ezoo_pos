from alembic import op
import sqlalchemy as sa

revision = 't010_add_updated_at'
down_revision = 't009_seed_fee_presets'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add updated_at to inventory_log
    with op.batch_alter_table('inventory_log') as batch_op:
        batch_op.add_column(sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP'), onupdate=sa.text('CURRENT_TIMESTAMP')))

    # Add updated_at to sale_items
    with op.batch_alter_table('sale_items') as batch_op:
        batch_op.add_column(sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP'), onupdate=sa.text('CURRENT_TIMESTAMP')))

    # Add updated_at to sale_fees
    with op.batch_alter_table('sale_fees') as batch_op:
        batch_op.add_column(sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP'), onupdate=sa.text('CURRENT_TIMESTAMP')))

    # Add updated_at to sale_reversals
    with op.batch_alter_table('sale_reversals') as batch_op:
        batch_op.add_column(sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP'), onupdate=sa.text('CURRENT_TIMESTAMP')))


def downgrade() -> None:
    with op.batch_alter_table('sale_reversals') as batch_op:
        batch_op.drop_column('updated_at')
    with op.batch_alter_table('sale_fees') as batch_op:
        batch_op.drop_column('updated_at')
    with op.batch_alter_table('sale_items') as batch_op:
        batch_op.drop_column('updated_at')
    with op.batch_alter_table('inventory_log') as batch_op:
        batch_op.drop_column('updated_at')
