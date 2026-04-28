from alembic import op
import sqlalchemy as sa

revision = 'b7c8b4e1ddfa'
down_revision = '74d2e1f1c3a5'
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    is_postgres = bind.dialect.name == 'postgresql'

    # inventory_log index - fine
    op.create_index(op.f('ix_inventory_log_created_at'), 'inventory_log', ['created_at'], unique=False)

    # partner_wallet_transactions - all alter_column ops need batch
    with op.batch_alter_table('partner_wallet_transactions') as batch_op:
        batch_op.alter_column('partner_id', existing_type=sa.String(length=36), comment='Partner whose wallet changed', existing_nullable=False)
        batch_op.alter_column('amount', existing_type=sa.Numeric(precision=12, scale=2), comment='Credit (positive) or debit (negative)', existing_nullable=False)
        batch_op.alter_column('transaction_type', existing_type=sa.String(length=50), comment='sale_profit or manual_adjustment', existing_nullable=False)
        batch_op.alter_column('reference_id', existing_type=sa.String(length=36), comment='FK to sale_id or NULL for manual', existing_nullable=True)
        batch_op.alter_column('reference_type', existing_type=sa.String(length=50), comment='sale or manual', existing_nullable=True)
        batch_op.alter_column('description', existing_type=sa.Text(), comment='Human-readable description', existing_nullable=True)
        batch_op.alter_column('balance_after', existing_type=sa.Numeric(precision=12, scale=2), comment='Wallet balance after this transaction', existing_nullable=False)
        batch_op.alter_column('created_at', existing_type=sa.DateTime(timezone=True), comment='Transaction timestamp', existing_nullable=False, existing_server_default=sa.text('CURRENT_TIMESTAMP'))
        batch_op.alter_column('created_by', existing_type=sa.String(length=36), comment='User who initiated transaction', existing_nullable=True)

    # Index ops on partner_wallet_transactions - fine
    op.drop_index('idx_partner_transactions', table_name='partner_wallet_transactions', if_exists=True)
    op.create_index('idx_partner_transactions', 'partner_wallet_transactions', ['partner_id', 'created_at'], unique=False)
    op.create_index(op.f('ix_partner_wallet_transactions_partner_id'), 'partner_wallet_transactions', ['partner_id'], unique=False)

    # product_assignments - all alter_column ops need batch
    with op.batch_alter_table('product_assignments') as batch_op:
        batch_op.alter_column('partner_id', existing_type=sa.String(length=36), comment='Partner receiving profit share', existing_nullable=False)
        batch_op.alter_column('product_id', existing_type=sa.String(length=36), comment='Product assigned to partner', existing_nullable=False)
        batch_op.alter_column('assigned_quantity', existing_type=sa.Integer(), comment='Original quantity assigned', existing_nullable=False)
        batch_op.alter_column('remaining_quantity', existing_type=sa.Integer(), comment='Quantity remaining unsold', existing_nullable=False, existing_server_default='0')
        batch_op.alter_column('share_percentage', existing_type=sa.Numeric(precision=5, scale=2), comment='Profit share (overrides partner default)', existing_nullable=False)
        if is_postgres:
            batch_op.alter_column('status', existing_type=sa.String(length=20), comment='active or fulfilled', existing_nullable=False, existing_server_default=sa.text('active::character varying'))
        else:
            batch_op.alter_column('status', existing_type=sa.String(length=20), comment='active or fulfilled', existing_nullable=False, existing_server_default='active')
        batch_op.alter_column('created_at', existing_type=sa.DateTime(timezone=True), comment='Creation timestamp', existing_nullable=False, existing_server_default=sa.text('CURRENT_TIMESTAMP'))
        batch_op.alter_column('updated_at', existing_type=sa.DateTime(timezone=True), comment='Last update timestamp', existing_nullable=False, existing_server_default=sa.text('CURRENT_TIMESTAMP'))
        batch_op.alter_column('fulfilled_at', existing_type=sa.DateTime(timezone=True), comment='When remaining_quantity hit 0', existing_nullable=True)
        batch_op.alter_column('created_by', existing_type=sa.String(length=36), comment='User who created assignment', existing_nullable=True)
        batch_op.alter_column('branch_id', existing_type=sa.String(length=36), comment='Branch for multi-branch support', existing_nullable=True)

    # Index ops on product_assignments - fine
    op.create_index(op.f('ix_product_assignments_partner_id'), 'product_assignments', ['partner_id'], unique=False)
    op.create_index(op.f('ix_product_assignments_product_id'), 'product_assignments', ['product_id'], unique=False)

    # products - add partner_id column, FK, and drop base_cost
    with op.batch_alter_table('products') as batch_op:
        batch_op.add_column(sa.Column('partner_id', sa.String(length=36), nullable=True))
    op.create_index(op.f('ix_products_partner_id'), 'products', ['partner_id'], unique=False)
    # Note: SQLite does not support ADD FOREIGN KEY via ALTER TABLE, so we skip the FK for SQLite
    if is_postgres:
        with op.batch_alter_table('products') as batch_op:
            batch_op.create_foreign_key(None, 'partners', ['partner_id'], ['id'], ondelete='SET NULL')
            batch_op.drop_column('base_cost')
    else:
        with op.batch_alter_table('products') as batch_op:
            batch_op.drop_column('base_cost')

    # sales index - fine
    op.create_index(op.f('ix_sales_created_at'), 'sales', ['created_at'], unique=False)


def downgrade() -> None:
    bind = op.get_bind()
    is_postgres = bind.dialect.name == 'postgresql'

    # sales index - fine
    op.drop_index(op.f('ix_sales_created_at'), table_name='sales')

    # products - add back base_cost, drop FK
    with op.batch_alter_table('products') as batch_op:
        batch_op.add_column(sa.Column('base_cost', sa.Numeric(precision=12, scale=2), server_default='0', nullable=False))
        batch_op.drop_constraint(None, type_='foreignkey')
    op.drop_index(op.f('ix_products_partner_id'), table_name='products')
    with op.batch_alter_table('products') as batch_op:
        batch_op.drop_column('partner_id')

    # product_assignments indexes - fine
    op.drop_index(op.f('ix_product_assignments_product_id'), table_name='product_assignments')
    op.drop_index(op.f('ix_product_assignments_partner_id'), table_name='product_assignments')

    # product_assignments - restore columns
    with op.batch_alter_table('product_assignments') as batch_op:
        batch_op.alter_column('branch_id', existing_type=sa.String(length=36), comment=None, existing_comment='Branch for multi-branch support', existing_nullable=True)
        batch_op.alter_column('created_by', existing_type=sa.String(length=36), comment=None, existing_comment='User who created assignment', existing_nullable=True)
        batch_op.alter_column('fulfilled_at', existing_type=sa.DateTime(timezone=True), comment=None, existing_comment='When remaining_quantity hit 0', existing_nullable=True)
        batch_op.alter_column('updated_at', existing_type=sa.DateTime(timezone=True), comment=None, existing_comment='Last update timestamp', existing_nullable=False, existing_server_default=sa.text('CURRENT_TIMESTAMP'))
        batch_op.alter_column('created_at', existing_type=sa.DateTime(timezone=True), comment=None, existing_comment='Creation timestamp', existing_nullable=False, existing_server_default=sa.text('CURRENT_TIMESTAMP'))
        if is_postgres:
            batch_op.alter_column('status', existing_type=sa.String(length=20), comment=None, existing_comment='active or fulfilled', existing_nullable=False, existing_server_default=sa.text('active::character varying'))
        else:
            batch_op.alter_column('status', existing_type=sa.String(length=20), comment=None, existing_comment='active or fulfilled', existing_nullable=False, existing_server_default='active')
        batch_op.alter_column('share_percentage', existing_type=sa.Numeric(precision=5, scale=2), comment=None, existing_comment='Profit share (overrides partner default)', existing_nullable=False)
        batch_op.alter_column('remaining_quantity', existing_type=sa.Integer(), comment=None, existing_comment='Quantity remaining unsold', existing_nullable=False, existing_server_default='0')
        batch_op.alter_column('assigned_quantity', existing_type=sa.Integer(), comment=None, existing_comment='Original quantity assigned', existing_nullable=False)
        batch_op.alter_column('product_id', existing_type=sa.String(length=36), comment=None, existing_comment='Product assigned to partner', existing_nullable=False)
        batch_op.alter_column('partner_id', existing_type=sa.String(length=36), comment=None, existing_comment='Partner receiving profit share', existing_nullable=False)

    # partner_wallet_transactions indexes - fine
    op.drop_index(op.f('ix_partner_wallet_transactions_partner_id'), table_name='partner_wallet_transactions')
    op.drop_index('idx_partner_transactions', table_name='partner_wallet_transactions')
    op.create_index('idx_partner_transactions', 'partner_wallet_transactions', ['partner_id', sa.text('created_at DESC')], unique=False)

    # partner_wallet_transactions - restore columns
    with op.batch_alter_table('partner_wallet_transactions') as batch_op:
        batch_op.alter_column('created_by', existing_type=sa.String(length=36), comment=None, existing_comment='User who initiated transaction', existing_nullable=True)
        batch_op.alter_column('created_at', existing_type=sa.DateTime(timezone=True), comment=None, existing_comment='Transaction timestamp', existing_nullable=False, existing_server_default=sa.text('CURRENT_TIMESTAMP'))
        batch_op.alter_column('balance_after', existing_type=sa.Numeric(precision=12, scale=2), comment=None, existing_comment='Wallet balance after this transaction', existing_nullable=False)
        batch_op.alter_column('description', existing_type=sa.Text(), comment=None, existing_comment='Human-readable description', existing_nullable=True)
        batch_op.alter_column('reference_type', existing_type=sa.String(length=50), comment=None, existing_comment='sale or manual', existing_nullable=True)
        batch_op.alter_column('reference_id', existing_type=sa.String(length=36), comment=None, existing_comment='FK to sale_id or NULL for manual', existing_nullable=True)
        batch_op.alter_column('transaction_type', existing_type=sa.String(length=50), comment=None, existing_comment='sale_profit or manual_adjustment', existing_nullable=False)
        batch_op.alter_column('amount', existing_type=sa.Numeric(precision=12, scale=2), comment=None, existing_comment='Credit (positive) or debit (negative)', existing_nullable=False)
        batch_op.alter_column('partner_id', existing_type=sa.String(length=36), comment=None, existing_comment='Partner whose wallet changed', existing_nullable=False)

    # inventory_log index - fine
    op.drop_index(op.f('ix_inventory_log_created_at'), table_name='inventory_log')
