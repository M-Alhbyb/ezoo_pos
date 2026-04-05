"""add missing settings columns

Revision ID: t008_settings_sync
Revises: t007_sale_reversals
Create Date: 2026-04-04 22:31:31.200130

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 't008_settings_sync'
down_revision = 't007_sale_reversals'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add missing columns
    op.add_column("settings", sa.Column("description", sa.String(), nullable=True))
    op.add_column("settings", sa.Column("user_id", sa.UUID(), nullable=True))
    op.add_column("settings", sa.Column("branch_id", sa.UUID(), nullable=True))
    
    # Alter 'key' column length from 50 to 100
    op.alter_column("settings", "key", 
                    type_=sa.String(100), 
                    existing_type=sa.String(50))
    
    # Alter 'value' column from JSONB to String
    # Using explicit cast for PostgreSQL
    from sqlalchemy.dialects import postgresql
    op.alter_column("settings", "value", 
                    type_=sa.String(), 
                    existing_type=postgresql.JSONB(),
                    postgresql_using="value::text")


def downgrade() -> None:
    # Revert 'value' column from String to JSONB
    from sqlalchemy.dialects import postgresql
    op.alter_column("settings", "value", 
                    type_=postgresql.JSONB(), 
                    existing_type=sa.String(),
                    postgresql_using="value::jsonb")
    
    # Revert 'key' column length
    op.alter_column("settings", "key", 
                    type_=sa.String(50), 
                    existing_type=sa.String(100))
    
    # Remove columns
    op.drop_column("settings", "branch_id")
    op.drop_column("settings", "user_id")
    op.drop_column("settings", "description")
