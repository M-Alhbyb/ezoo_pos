from alembic import op

revision = 'bc658d5d509a'
down_revision = '378166ead740'
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table('partners') as batch_op:
        batch_op.alter_column('profit_percentage', new_column_name='share_percentage')


def downgrade() -> None:
    with op.batch_alter_table('partners') as batch_op:
        batch_op.alter_column('share_percentage', new_column_name='profit_percentage')
