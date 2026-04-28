from alembic import op
import sqlalchemy as sa

revision = 'ff61dc814413'
down_revision = 't010_add_updated_at'
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table('sales') as batch_op:
        batch_op.add_column(sa.Column('idempotency_key', sa.String(length=255), nullable=True))
    op.create_index(op.f('ix_sales_idempotency_key'), 'sales', ['idempotency_key'], unique=True)


def downgrade() -> None:
    op.drop_index(op.f('ix_sales_idempotency_key'), table_name='sales')
    with op.batch_alter_table('sales') as batch_op:
        batch_op.drop_column('idempotency_key')
