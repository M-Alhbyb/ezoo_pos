from alembic import op
import sqlalchemy as sa

revision = '9533b1dbbe0c'
down_revision = 't011_add_category_color'
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    is_postgres = bind.dialect.name == 'postgresql'

    # 1. Drop the defunct product_assignments table
    op.drop_table('product_assignments')

    # 2. Drop Foreign Key constraints
    if is_postgres:
        op.drop_constraint('partner_distributions_partner_id_fkey', 'partner_distributions', type_='foreignkey')
        op.drop_constraint('partner_wallet_transactions_partner_id_fkey', 'partner_wallet_transactions', type_='foreignkey')
        op.drop_constraint('products_partner_id_fkey', 'products', type_='foreignkey')
    # For SQLite, skip explicit constraint drops - the batch alter_column will recreate tables without constraints
    # and we'll re-add them afterward

    # 3. Drop Primary Key on partners(id)
    if is_postgres:
        op.drop_constraint('partners_pkey', 'partners', type_='primary')
    # For SQLite, skip explicit PK drop - batch alter_column will handle table recreation

    # 4. Alter column types to Integer
    if is_postgres:
        op.execute('ALTER TABLE partners ALTER COLUMN id DROP DEFAULT')
        op.execute('ALTER TABLE partners ALTER COLUMN id TYPE INTEGER USING 0')
        op.execute('CREATE SEQUENCE partners_id_seq')
        op.execute('ALTER TABLE partners ALTER COLUMN id SET DEFAULT nextval(\'partners_id_seq\')')
        op.execute('ALTER SEQUENCE partners_id_seq OWNED BY partners.id')
        op.execute('ALTER TABLE partner_distributions ALTER COLUMN partner_id TYPE INTEGER USING 0')
        op.execute('ALTER TABLE partner_wallet_transactions ALTER COLUMN partner_id TYPE INTEGER USING 0')
        op.execute('ALTER TABLE products ALTER COLUMN partner_id TYPE INTEGER USING 0')
    else:
        with op.batch_alter_table('partners') as batch_op:
            batch_op.alter_column('id', type_=sa.Integer(), existing_type=sa.String(length=36), existing_nullable=False)
        with op.batch_alter_table('partner_distributions') as batch_op:
            batch_op.alter_column('partner_id', type_=sa.Integer(), existing_type=sa.String(length=36), existing_nullable=False)
        with op.batch_alter_table('partner_wallet_transactions') as batch_op:
            batch_op.alter_column('partner_id', type_=sa.Integer(), existing_type=sa.String(length=36), existing_nullable=False)
        with op.batch_alter_table('products') as batch_op:
            batch_op.alter_column('partner_id', type_=sa.Integer(), existing_type=sa.String(length=36), existing_nullable=True)

    # 5. Re-add Primary Key
    with op.batch_alter_table('partners') as batch_op:
        batch_op.create_primary_key('partners_pkey', ['id'])

    # 6. Re-add Foreign Key constraints
    with op.batch_alter_table('partner_distributions') as batch_op:
        batch_op.create_foreign_key('partner_distributions_partner_id_fkey', 'partners', ['partner_id'], ['id'])
    with op.batch_alter_table('partner_wallet_transactions') as batch_op:
        batch_op.create_foreign_key('partner_wallet_transactions_partner_id_fkey', 'partners', ['partner_id'], ['id'], ondelete='RESTRICT')
    with op.batch_alter_table('products') as batch_op:
        batch_op.create_foreign_key('products_partner_id_fkey', 'partners', ['partner_id'], ['id'], ondelete='SET NULL')


def downgrade() -> None:
    # Restore columns
    with op.batch_alter_table('products') as batch_op:
        batch_op.alter_column('partner_id', type_=sa.String(length=36), existing_type=sa.Integer(), existing_nullable=True)
    with op.batch_alter_table('partners') as batch_op:
        batch_op.alter_column('id', type_=sa.String(length=36), existing_type=sa.Integer(), existing_nullable=False, autoincrement=True)
    with op.batch_alter_table('partner_wallet_transactions') as batch_op:
        batch_op.alter_column('partner_id', type_=sa.String(length=36), existing_type=sa.Integer(), existing_comment='Partner whose wallet changed', existing_nullable=False)
    with op.batch_alter_table('partner_distributions') as batch_op:
        batch_op.alter_column('partner_id', type_=sa.String(length=36), existing_type=sa.Integer(), existing_nullable=False)

    # Recreate product_assignments table
    op.create_table('product_assignments',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('partner_id', sa.String(length=36), nullable=False),
    sa.Column('product_id', sa.String(length=36), nullable=False),
    sa.Column('assigned_quantity', sa.Integer(), nullable=False),
    sa.Column('remaining_quantity', sa.Integer(), server_default='0', nullable=False),
    sa.Column('share_percentage', sa.Numeric(5, 2), nullable=False),
    sa.Column('status', sa.String(20), server_default='active', nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.Column('fulfilled_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_by', sa.String(length=36), nullable=True),
    sa.Column('branch_id', sa.String(length=36), nullable=True),
    sa.CheckConstraint('remaining_quantity >= 0', name='check_remaining_nonnegative'),
    sa.CheckConstraint('share_percentage >= 0 AND share_percentage <= 100', name='check_share_percentage_range'),
    sa.ForeignKeyConstraint(['partner_id'], ['partners.id']),
    sa.ForeignKeyConstraint(['product_id'], ['products.id']),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_product_assignments_product_id', 'product_assignments', ['product_id'], unique=False)
    op.create_index('ix_product_assignments_partner_id', 'product_assignments', ['partner_id'], unique=False)
    op.create_index('idx_product_assignment_active', 'product_assignments', ['product_id', 'status', 'remaining_quantity'], unique=False)
    op.create_index('idx_partner_assignments', 'product_assignments', ['partner_id'], unique=False)
