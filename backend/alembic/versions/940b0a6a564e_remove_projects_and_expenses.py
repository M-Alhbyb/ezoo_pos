"""remove_projects_and_expenses

Revision ID: 940b0a6a564e
Revises: bc658d5d509a
Create Date: 2026-04-08 09:36:54.188335

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '940b0a6a564e'
down_revision = 'bc658d5d509a'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Drop dependants first
    op.drop_table('expenses')
    op.drop_table('project_items')
    
    # 2. Update partner_distributions
    # Drop index first
    op.drop_index('ix_partner_distributions_project_id', table_name='partner_distributions')
    # Drop foreign key constraint (assuming default name)
    op.drop_constraint('partner_distributions_project_id_fkey', 'partner_distributions', type_='foreignkey')
    # Drop the column
    op.drop_column('partner_distributions', 'project_id')
    
    # 3. Drop projects table
    op.drop_table('projects')
    
    # 4. Drop custom types (Enum)
    sa.Enum(name='projectstatus').drop(op.get_bind())
    sa.Enum(name='expensetype').drop(op.get_bind())


def downgrade() -> None:
    # NOTE: Reversing this would require restoring schemas and potentially lost data.
    # For now, we leave it as a no-op as the user requested total removal.
    pass
