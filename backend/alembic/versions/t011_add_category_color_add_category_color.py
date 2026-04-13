"""add category color

Revision ID: t011_add_category_color
Revises: b7c8b4e1ddfa
Create Date: 2026-04-13 12:07:49.598502

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 't011_add_category_color'
down_revision = 'b7c8b4e1ddfa'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add color column to categories
    op.add_column('categories', sa.Column('color', sa.String(length=50), nullable=True))


def downgrade() -> None:
    # Remove color column from categories
    op.drop_column('categories', 'color')
