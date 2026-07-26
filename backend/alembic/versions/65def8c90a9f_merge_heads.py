"""merge_heads

Revision ID: 65def8c90a9f
Revises: a001_add_users_table, t013_customer_accounting
Create Date: 2026-07-26 10:44:46.266704

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '65def8c90a9f'
down_revision = ('a001_add_users_table', 't013_customer_accounting')
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
