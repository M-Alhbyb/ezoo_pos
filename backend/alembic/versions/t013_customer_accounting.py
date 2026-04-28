from alembic import op
import sqlalchemy as sa

revision = 't013_customer_accounting'
down_revision = 't012_supplier_accounting'
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    is_postgres = bind.dialect.name == 'postgresql'

    # Create customers table
    op.create_table(
        'customers',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('name', sa.String(255), nullable=False, unique=True),
        sa.Column('phone', sa.String(50), nullable=False),
        sa.Column('address', sa.Text(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('credit_limit', sa.Numeric(12, 2), server_default='0.00', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.CheckConstraint('credit_limit >= 0', name='check_customer_credit_limit_non_negative'),
    )

    # Create customer_ledger table
    op.create_table(
        'customer_ledger',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('customer_id', sa.String(length=36), sa.ForeignKey('customers.id', ondelete='RESTRICT'), nullable=False),
        sa.Column('type', sa.String(20), nullable=False),
        sa.Column('amount', sa.Numeric(12, 2), nullable=False),
        sa.Column('reference_id', sa.String(length=36), nullable=True),
        sa.Column('payment_method', sa.String(100), nullable=True),
        sa.Column('note', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.CheckConstraint('type IN (\"SALE\", \"PAYMENT\", \"RETURN\")', name='check_customer_ledger_type'),
    )

    # Add customer_id to sales table (FK skipped for SQLite since ADD FOREIGN KEY not supported via ALTER TABLE)
    if is_postgres:
        with op.batch_alter_table('sales') as batch_op:
            batch_op.add_column(sa.Column('customer_id', sa.String(length=36), sa.ForeignKey('customers.id', ondelete='RESTRICT'), nullable=True))
    else:
        with op.batch_alter_table('sales') as batch_op:
            batch_op.add_column(sa.Column('customer_id', sa.String(length=36), nullable=True))

    # Add indexes
    op.create_index('idx_customer_ledger_customer', 'customer_ledger', ['customer_id', 'created_at'])
    op.create_index('idx_customer_ledger_type', 'customer_ledger', ['customer_id', 'type'])
    op.create_index('idx_sales_customer', 'sales', ['customer_id'])


def downgrade():
    op.drop_index('idx_sales_customer', table_name='sales')
    with op.batch_alter_table('sales') as batch_op:
        batch_op.drop_column('customer_id')
    op.drop_table('customer_ledger')
    op.drop_table('customers')
