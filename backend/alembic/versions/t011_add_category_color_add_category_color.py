from alembic import op
import sqlalchemy as sa

revision = 't011_add_category_color'
down_revision = 'b7c8b4e1ddfa'
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table('categories') as batch_op:
        batch_op.add_column(sa.Column('color', sa.String(length=50), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table('categories') as batch_op:
        batch_op.drop_column('color')
