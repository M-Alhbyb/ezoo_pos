from alembic import op
import sqlalchemy as sa

revision = '8e1f63b297a9'
down_revision = 'ff61dc814413'
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    is_postgres = bind.dialect.name == 'postgresql'

    # categories - drop unique constraint
    if is_postgres:
        with op.batch_alter_table('categories') as batch_op:
            batch_op.drop_constraint('categories_name_key', type_='unique')
    op.drop_index('idx_categories_name', table_name='categories')
    op.create_index(op.f('ix_categories_name'), 'categories', ['name'], unique=True)

    # inventory_log - indexes only, fine
    op.drop_index('idx_inventory_log_product', table_name='inventory_log')
    op.drop_index('idx_inventory_log_reference', table_name='inventory_log', postgresql_where='(reference_id IS NOT NULL)')
    op.create_index(op.f('ix_inventory_log_product_id'), 'inventory_log', ['product_id'], unique=False)

    # payment_methods - drop unique constraint
    if is_postgres:
        with op.batch_alter_table('payment_methods') as batch_op:
            batch_op.drop_constraint('payment_methods_name_key', type_='unique')
    op.create_index(op.f('ix_payment_methods_is_active'), 'payment_methods', ['is_active'], unique=False)
    op.create_index(op.f('ix_payment_methods_name'), 'payment_methods', ['name'], unique=True)

    # products - drop unique constraint
    op.drop_index('idx_products_active', table_name='products')
    op.drop_index('idx_products_category', table_name='products')
    op.drop_index('idx_products_name', table_name='products', postgresql_using='gin')
    op.drop_index('idx_products_sku', table_name='products', postgresql_where='(sku IS NOT NULL)')
    if is_postgres:
        with op.batch_alter_table('products') as batch_op:
            batch_op.drop_constraint('products_sku_key', type_='unique')
    op.create_index(op.f('ix_products_category_id'), 'products', ['category_id'], unique=False)
    op.create_index(op.f('ix_products_is_active'), 'products', ['is_active'], unique=False)
    op.create_index(op.f('ix_products_name'), 'products', ['name'], unique=False)
    op.create_index(op.f('ix_products_sku'), 'products', ['sku'], unique=True)

    # sale_fees - recreate FK (drop and recreate for postgres, skip for sqlite - constraints already exist)
    op.drop_index('idx_sale_fees_sale', table_name='sale_fees')
    op.create_index(op.f('ix_sale_fees_sale_id'), 'sale_fees', ['sale_id'], unique=False)
    if is_postgres:
        with op.batch_alter_table('sale_fees') as batch_op:
            batch_op.drop_constraint('sale_fees_sale_id_fkey', type_='foreignkey')
            batch_op.create_foreign_key(None, 'sales', ['sale_id'], ['id'])

    # sale_items - add columns and modify FKs
    with op.batch_alter_table('sale_items') as batch_op:
        batch_op.add_column(sa.Column('base_cost', sa.Numeric(precision=12, scale=2), nullable=True))
        batch_op.add_column(sa.Column('vat_rate', sa.Numeric(precision=5, scale=2), nullable=True))
    op.drop_index('idx_sale_items_sale', table_name='sale_items')
    op.create_index(op.f('ix_sale_items_product_id'), 'sale_items', ['product_id'], unique=False)
    op.create_index(op.f('ix_sale_items_sale_id'), 'sale_items', ['sale_id'], unique=False)
    if is_postgres:
        with op.batch_alter_table('sale_items') as batch_op:
            batch_op.drop_constraint('sale_items_product_id_fkey', type_='foreignkey')
            batch_op.drop_constraint('sale_items_sale_id_fkey', type_='foreignkey')
            batch_op.create_foreign_key(None, 'sales', ['sale_id'], ['id'])
            batch_op.create_foreign_key(None, 'products', ['product_id'], ['id'])

    # sale_reversals - modify FKs
    op.drop_index('idx_sale_reversals_original', table_name='sale_reversals')
    op.create_index(op.f('ix_sale_reversals_original_sale_id'), 'sale_reversals', ['original_sale_id'], unique=False)
    if is_postgres:
        with op.batch_alter_table('sale_reversals') as batch_op:
            batch_op.drop_constraint('sale_reversals_reversal_sale_id_fkey', type_='foreignkey')
            batch_op.drop_constraint('sale_reversals_original_sale_id_fkey', type_='foreignkey')
            batch_op.create_foreign_key(None, 'sales', ['original_sale_id'], ['id'])
            batch_op.create_foreign_key(None, 'sales', ['reversal_sale_id'], ['id'])

    # sales - add columns
    with op.batch_alter_table('sales') as batch_op:
        batch_op.add_column(sa.Column('vat_total', sa.Numeric(precision=12, scale=2), nullable=False, server_default='0'))
        batch_op.add_column(sa.Column('grand_total', sa.Numeric(precision=12, scale=2), nullable=False, server_default='0'))
        batch_op.add_column(sa.Column('total_cost', sa.Numeric(precision=12, scale=2), nullable=False, server_default='0'))
        batch_op.add_column(sa.Column('profit', sa.Numeric(precision=12, scale=2), nullable=False, server_default='0'))

    op.execute('UPDATE sales SET vat_total = vat_amount, grand_total = total, total_cost = 0, profit = total')

    op.drop_index('idx_sales_created_at', table_name='sales')
    op.drop_index('idx_sales_payment_method', table_name='sales')
    op.create_index(op.f('ix_sales_payment_method_id'), 'sales', ['payment_method_id'], unique=False)

    # For dropping columns, SQLite needs table recreation due to ALTER TABLE DROP COLUMN bug with CHECK constraints
    if is_postgres:
        with op.batch_alter_table('sales') as batch_op:
            batch_op.drop_column('total')
            batch_op.drop_column('vat_amount')
    else:
        op.execute('''
        CREATE TABLE sales_tmp (
            id VARCHAR(36) NOT NULL,
            payment_method_id VARCHAR(36) NOT NULL,
            subtotal NUMERIC(12, 2) NOT NULL,
            fees_total NUMERIC(12, 2) DEFAULT '0' NOT NULL,
            vat_rate NUMERIC(5, 2),
            note TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
            user_id VARCHAR(36),
            branch_id VARCHAR(36),
            idempotency_key VARCHAR(255),
            vat_total NUMERIC(12, 2) DEFAULT '0' NOT NULL,
            grand_total NUMERIC(12, 2) DEFAULT '0' NOT NULL,
            total_cost NUMERIC(12, 2) DEFAULT '0' NOT NULL,
            profit NUMERIC(12, 2) DEFAULT '0' NOT NULL,
            PRIMARY KEY (id),
            CONSTRAINT chk_subtotal_positive CHECK (subtotal >= 0),
            CONSTRAINT chk_fees_positive CHECK (fees_total >= 0),
            FOREIGN KEY(payment_method_id) REFERENCES payment_methods (id)
        )
        ''')
        op.execute('INSERT INTO sales_tmp SELECT id, payment_method_id, subtotal, fees_total, vat_rate, note, created_at, updated_at, user_id, branch_id, idempotency_key, vat_total, grand_total, total_cost, profit FROM sales')
        op.execute('DROP TABLE sales')
        op.execute('ALTER TABLE sales_tmp RENAME TO sales')

    # settings - drop unique constraint
    if is_postgres:
        with op.batch_alter_table('settings') as batch_op:
            batch_op.drop_constraint('settings_key_key', type_='unique')
    op.create_index(op.f('ix_settings_key'), 'settings', ['key'], unique=True)


def downgrade() -> None:
    bind = op.get_bind()
    is_postgres = bind.dialect.name == 'postgresql'

    op.drop_index(op.f('ix_settings_key'), table_name='settings')
    with op.batch_alter_table('settings') as batch_op:
        batch_op.create_unique_constraint('settings_key_key', ['key'])

    # sales - restore original schema (add back total and vat_amount, remove new columns)
    if is_postgres:
        with op.batch_alter_table('sales') as batch_op:
            batch_op.add_column(sa.Column('vat_amount', sa.NUMERIC(precision=12, scale=2), autoincrement=False, nullable=True))
            batch_op.add_column(sa.Column('total', sa.NUMERIC(precision=12, scale=2), autoincrement=False, nullable=False))
        with op.batch_alter_table('sales') as batch_op:
            batch_op.drop_column('profit')
            batch_op.drop_column('total_cost')
            batch_op.drop_column('grand_total')
            batch_op.drop_column('vat_total')
    else:
        # SQLite: recreate table with original schema
        op.execute('''
        CREATE TABLE sales_tmp (
            id VARCHAR(36) NOT NULL,
            payment_method_id VARCHAR(36) NOT NULL,
            subtotal NUMERIC(12, 2) NOT NULL,
            fees_total NUMERIC(12, 2) DEFAULT '0' NOT NULL,
            vat_rate NUMERIC(5, 2),
            vat_amount NUMERIC(12, 2),
            total NUMERIC(12, 2) NOT NULL,
            note TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
            user_id VARCHAR(36),
            branch_id VARCHAR(36),
            idempotency_key VARCHAR(255),
            PRIMARY KEY (id),
            CONSTRAINT chk_subtotal_positive CHECK (subtotal >= 0),
            CONSTRAINT chk_fees_positive CHECK (fees_total >= 0),
            CONSTRAINT chk_total_positive CHECK (total >= 0),
            FOREIGN KEY(payment_method_id) REFERENCES payment_methods (id)
        )
        ''')
        op.execute('INSERT INTO sales_tmp SELECT id, payment_method_id, subtotal, fees_total, vat_rate, vat_amount, total, note, created_at, updated_at, user_id, branch_id, idempotency_key FROM sales')
        op.execute('DROP TABLE sales')
        op.execute('ALTER TABLE sales_tmp RENAME TO sales')

    op.drop_index(op.f('ix_sales_payment_method_id'), table_name='sales')
    op.create_index('idx_sales_payment_method', 'sales', ['payment_method_id'], unique=False)
    op.create_index('idx_sales_created_at', 'sales', [sa.text('created_at DESC')], unique=False)

    if is_postgres:
        with op.batch_alter_table('sale_reversals') as batch_op:
            batch_op.drop_constraint(None, type_='foreignkey')
            batch_op.drop_constraint(None, type_='foreignkey')
            batch_op.create_foreign_key('sale_reversals_original_sale_id_fkey', 'sales', ['original_sale_id'], ['id'], ondelete='RESTRICT')
            batch_op.create_foreign_key('sale_reversals_reversal_sale_id_fkey', 'sales', ['reversal_sale_id'], ['id'], ondelete='SET NULL')
    op.drop_index(op.f('ix_sale_reversals_original_sale_id'), table_name='sale_reversals')
    op.create_index('idx_sale_reversals_original', 'sale_reversals', ['original_sale_id'], unique=False)

    if is_postgres:
        with op.batch_alter_table('sale_items') as batch_op:
            batch_op.drop_constraint(None, type_='foreignkey')
            batch_op.drop_constraint(None, type_='foreignkey')
            batch_op.create_foreign_key('sale_items_sale_id_fkey', 'sales', ['sale_id'], ['id'], ondelete='CASCADE')
            batch_op.create_foreign_key('sale_items_product_id_fkey', 'products', ['product_id'], ['id'], ondelete='RESTRICT')
    op.drop_index(op.f('ix_sale_items_sale_id'), table_name='sale_items')
    op.drop_index(op.f('ix_sale_items_product_id'), table_name='sale_items')
    op.create_index('idx_sale_items_sale', 'sale_items', ['sale_id'], unique=False)
    with op.batch_alter_table('sale_items') as batch_op:
        batch_op.drop_column('vat_rate')
        batch_op.drop_column('base_cost')

    if is_postgres:
        with op.batch_alter_table('sale_fees') as batch_op:
            batch_op.drop_constraint(None, type_='foreignkey')
            batch_op.create_foreign_key('sale_fees_sale_id_fkey', 'sales', ['sale_id'], ['id'], ondelete='CASCADE')
    op.drop_index(op.f('ix_sale_fees_sale_id'), table_name='sale_fees')
    op.create_index('idx_sale_fees_sale', 'sale_fees', ['sale_id'], unique=False)

    op.drop_index(op.f('ix_products_sku'), table_name='products')
    op.drop_index(op.f('ix_products_name'), table_name='products')
    op.drop_index(op.f('ix_products_is_active'), table_name='products')
    op.drop_index(op.f('ix_products_category_id'), table_name='products')
    with op.batch_alter_table('products') as batch_op:
        batch_op.create_unique_constraint('products_sku_key', ['sku'])
    op.create_index('idx_products_sku', 'products', ['sku'], unique=False, postgresql_where='(sku IS NOT NULL)')
    op.create_index('idx_products_name', 'products', ['name'], unique=False, postgresql_using='gin')
    op.create_index('idx_products_category', 'products', ['category_id'], unique=False)
    op.create_index('idx_products_active', 'products', ['is_active'], unique=False)

    op.drop_index(op.f('ix_payment_methods_name'), table_name='payment_methods')
    op.drop_index(op.f('ix_payment_methods_is_active'), table_name='payment_methods')
    with op.batch_alter_table('payment_methods') as batch_op:
        batch_op.create_unique_constraint('payment_methods_name_key', ['name'])

    op.drop_index(op.f('ix_inventory_log_product_id'), table_name='inventory_log')
    op.create_index('idx_inventory_log_reference', 'inventory_log', ['reference_id'], unique=False, postgresql_where='(reference_id IS NOT NULL)')
    op.create_index('idx_inventory_log_product', 'inventory_log', ['product_id', sa.text('created_at DESC')], unique=False)

    op.drop_index(op.f('ix_categories_name'), table_name='categories')
    op.create_index('idx_categories_name', 'categories', ['name'], unique=False)
    with op.batch_alter_table('categories') as batch_op:
        batch_op.create_unique_constraint('categories_name_key', ['name'])
