"""rename_profit_percentage_to_share_percentage

Revision ID: bc658d5d509a
Revises: 378166ead740
Create Date: 2026-04-06 11:21:11.796797

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bc658d5d509a'
down_revision = '378166ead740'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column('partners', 'profit_percentage', new_column_name='share_percentage')


def downgrade() -> None:
    op.alter_column('partners', 'share_percentage', new_column_name='profit_percentage')
