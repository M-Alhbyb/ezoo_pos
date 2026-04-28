from alembic import op
import sqlalchemy as sa

revision = '940b0a6a564e'
down_revision = 'bc658d5d509a'
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    is_postgres = bind.dialect.name == 'postgresql'

    # 1. Drop dependants first
    op.drop_table('expenses')
    op.drop_table('project_items')

    # 2. Update partner_distributions - use batch for constraint and column ops
    op.drop_index('ix_partner_distributions_project_id', table_name='partner_distributions')
    if is_postgres:
        op.drop_constraint('partner_distributions_project_id_fkey', 'partner_distributions', type_='foreignkey')
    # For SQLite, the FK will be dropped automatically when we drop the column via batch
    with op.batch_alter_table('partner_distributions') as batch_op:
        batch_op.drop_column('project_id')

    # 3. Drop projects table
    op.drop_table('projects')

    # 4. Drop custom types (Enum) - PostgreSQL only
    if is_postgres:
        sa.Enum(name='projectstatus').drop(bind)
        sa.Enum(name='expensetype').drop(bind)


def downgrade() -> None:
    pass
