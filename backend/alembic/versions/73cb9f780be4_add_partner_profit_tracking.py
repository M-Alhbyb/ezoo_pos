from alembic import op
import sqlalchemy as sa

revision = '73cb9f780be4'
down_revision = '940b0a6a564e'
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    is_postgres = bind.dialect.name == 'postgresql'

    # Create product_assignments table
    op.create_table(
        'product_assignments',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('partner_id', sa.String(length=36), sa.ForeignKey('partners.id', ondelete='RESTRICT'), nullable=False),
        sa.Column('product_id', sa.String(length=36), sa.ForeignKey('products.id', ondelete='RESTRICT'), nullable=False),
        sa.Column('assigned_quantity', sa.Integer(), nullable=False),
        sa.Column('remaining_quantity', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('share_percentage', sa.Numeric(5, 2), nullable=False),
        sa.Column('status', sa.String(20), nullable=False, server_default='active'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('fulfilled_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_by', sa.String(length=36), nullable=True),
        sa.Column('branch_id', sa.String(length=36), nullable=True),
    )

    # Add unique constraint for one partner per product (partial index - PostgreSQL only)
    if is_postgres:
        op.create_index(
            'idx_product_assignments_product_active',
            'product_assignments',
            ['product_id', 'status'],
            unique=False,
            postgresql_where=sa.text('status = active')
        )

    # Create partner_wallet_transactions table
    op.create_table(
        'partner_wallet_transactions',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('partner_id', sa.String(length=36), sa.ForeignKey('partners.id', ondelete='RESTRICT'), nullable=False),
        sa.Column('amount', sa.Numeric(12, 2), nullable=False),
        sa.Column('transaction_type', sa.String(50), nullable=False),
        sa.Column('reference_id', sa.String(length=36), nullable=True),
        sa.Column('reference_type', sa.String(50), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('balance_after', sa.Numeric(12, 2), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('created_by', sa.String(length=36), nullable=True),
        sa.CheckConstraint('amount != 0', name='check_partner_wallet_amount_nonzero'),
    )

    # Add indexes
    op.create_index(
        'idx_partner_wallet_transactions_partner',
        'partner_wallet_transactions',
        ['partner_id', 'created_at'],
    )


def downgrade():
    op.drop_table('partner_wallet_transactions')
    op.drop_table('product_assignments')
