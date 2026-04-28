from alembic import op
import sqlalchemy as sa

revision = '374b96547931'
down_revision = '8e1f63b297a9'
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    is_postgres = bind.dialect.name == 'postgresql'

    # Drop sale_reversals table (fine - it's a drop table)
    op.drop_index('ix_sale_reversals_original_sale_id', table_name='sale_reversals')
    op.drop_table('sale_reversals')

    # Add columns to sales - use batch
    with op.batch_alter_table('sales') as batch_op:
        batch_op.add_column(sa.Column('original_sale_id', sa.String(length=36), nullable=True))
        batch_op.add_column(sa.Column('is_reversal', sa.Boolean(), server_default='false', nullable=False))

    # Create index and FK
    op.create_index(op.f('ix_sales_original_sale_id'), 'sales', ['original_sale_id'], unique=False)
    # Note: SQLite does not support ADD FOREIGN KEY via ALTER TABLE, so we skip it for SQLite
    if is_postgres:
        with op.batch_alter_table('sales') as batch_op:
            batch_op.create_foreign_key(None, 'sales', ['original_sale_id'], ['id'])

    # Drop check constraints - use batch for SQLite
    if is_postgres:
        op.drop_constraint('chk_subtotal_positive', 'sales', type_='check')
        op.drop_constraint('chk_fees_positive', 'sales', type_='check')
        op.execute('ALTER TABLE sales DROP CONSTRAINT IF EXISTS check_total_nonnegative')
        op.execute('ALTER TABLE sales DROP CONSTRAINT IF EXISTS check_total_cost_nonnegative')
        op.drop_constraint('chk_quantity_positive', 'sale_items', type_='check')
        op.drop_constraint('chk_line_total_positive', 'sale_items', type_='check')
    else:
        # SQLite - use batch mode
        with op.batch_alter_table('sales') as batch_op:
            batch_op.drop_constraint('chk_subtotal_positive', type_='check')
            batch_op.drop_constraint('chk_fees_positive', type_='check')
        with op.batch_alter_table('sale_items') as batch_op:
            batch_op.drop_constraint('chk_quantity_positive', type_='check')
            batch_op.drop_constraint('chk_line_total_positive', type_='check')


def downgrade() -> None:
    bind = op.get_bind()
    is_postgres = bind.dialect.name == 'postgresql'

    # Drop FK and columns from sales
    # Note: For SQLite, we skip FK drop since we skipped FK add (SQLite doesn't support ADD FOREIGN KEY)
    if is_postgres:
        with op.batch_alter_table('sales') as batch_op:
            batch_op.drop_constraint(None, type_='foreignkey')
    op.drop_index(op.f('ix_sales_original_sale_id'), table_name='sales')
    with op.batch_alter_table('sales') as batch_op:
        batch_op.drop_column('is_reversal')
        batch_op.drop_column('original_sale_id')

    # Recreate check constraints
    with op.batch_alter_table('sales') as batch_op:
        batch_op.create_check_constraint('chk_subtotal_positive', 'subtotal >= 0')
        batch_op.create_check_constraint('chk_fees_positive', 'fees_total >= 0')
    with op.batch_alter_table('sale_items') as batch_op:
        batch_op.create_check_constraint('chk_quantity_positive', 'quantity > 0')
        batch_op.create_check_constraint('chk_line_total_positive', 'line_total >= 0')

    # Recreate sale_reversals table
    op.create_table('sale_reversals',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('original_sale_id', sa.String(length=36), nullable=False),
    sa.Column('reversal_sale_id', sa.String(length=36), nullable=True),
    sa.Column('reason', sa.Text(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.Column('user_id', sa.String(length=36), nullable=True),
    sa.Column('branch_id', sa.String(length=36), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.ForeignKeyConstraint(['original_sale_id'], ['sales.id']),
    sa.ForeignKeyConstraint(['reversal_sale_id'], ['sales.id']),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_sale_reversals_original_sale_id', 'sale_reversals', ['original_sale_id'], unique=False)
