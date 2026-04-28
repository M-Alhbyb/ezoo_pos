from alembic import op
import sqlalchemy as sa

revision = '378166ead740'
down_revision = 'de35f06ee1ad'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create partner_distributions table (create_table is fine)
    op.create_table('partner_distributions',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('partner_id', sa.String(length=36), nullable=False),
    sa.Column('project_id', sa.String(length=36), nullable=False),
    sa.Column('payout_amount', sa.Numeric(precision=12, scale=2), nullable=False),
    sa.Column('snapshot_fields', sa.Text(), server_default='{}', nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.ForeignKeyConstraint(['partner_id'], ['partners.id']),
    sa.ForeignKeyConstraint(['project_id'], ['projects.id']),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_partner_distributions_partner_id'), 'partner_distributions', ['partner_id'], unique=False)
    op.create_index(op.f('ix_partner_distributions_project_id'), 'partner_distributions', ['project_id'], unique=False)

    # Modify partners table - use batch
    with op.batch_alter_table('partners') as batch_op:
        batch_op.add_column(sa.Column('investment_amount', sa.Numeric(precision=12, scale=2), server_default='0', nullable=False))
        batch_op.add_column(sa.Column('profit_percentage', sa.Numeric(precision=5, scale=2), nullable=False))
        batch_op.drop_column('percentage')


def downgrade() -> None:
    # Restore partners columns
    with op.batch_alter_table('partners') as batch_op:
        batch_op.add_column(sa.Column('percentage', sa.NUMERIC(precision=5, scale=2), nullable=False))
        batch_op.drop_column('profit_percentage')
        batch_op.drop_column('investment_amount')

    op.drop_index(op.f('ix_partner_distributions_project_id'), table_name='partner_distributions')
    op.drop_index(op.f('ix_partner_distributions_partner_id'), table_name='partner_distributions')
    op.drop_table('partner_distributions')
