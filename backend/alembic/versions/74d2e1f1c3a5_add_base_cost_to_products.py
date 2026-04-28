from alembic import op
import sqlalchemy as sa

revision = '74d2e1f1c3a5'
down_revision = '73cb9f780be4'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('products') as batch_op:
        batch_op.add_column(sa.Column('base_cost', sa.Numeric(12, 2), nullable=False, server_default='0'))


def downgrade():
    with op.batch_alter_table('products') as batch_op:
        batch_op.drop_column('base_cost')
