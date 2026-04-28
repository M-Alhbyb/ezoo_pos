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
    with op.batch_alter_table("settings") as batch_op:
        batch_op.add_column(sa.Column("description", sa.String(), nullable=True))
        batch_op.add_column(sa.Column("user_id", sa.String(length=36), nullable=True))
        batch_op.add_column(sa.Column("branch_id", sa.String(length=36), nullable=True))
        batch_op.alter_column("key", type_=sa.String(100), existing_type=sa.String(50))
        from sqlalchemy.dialects import postgresql
        bind = op.get_bind()
        if bind.dialect.name == "postgresql":
            batch_op.alter_column("value", type_=sa.String(), existing_type=postgresql.JSONB(), postgresql_using="value::text")
        else:
            batch_op.alter_column("value", type_=sa.String(), existing_type=sa.Text())


def downgrade() -> None:
    with op.batch_alter_table("settings") as batch_op:
        from sqlalchemy.dialects import postgresql
        bind = op.get_bind()
        if bind.dialect.name == "postgresql":
            batch_op.alter_column("value", type_=postgresql.JSONB(), existing_type=sa.String(), postgresql_using="value::jsonb")
        else:
            batch_op.alter_column("value", type_=sa.Text(), existing_type=sa.String())
        batch_op.alter_column("key", type_=sa.String(50), existing_type=sa.String(100))
        batch_op.drop_column("branch_id")
        batch_op.drop_column("user_id")
        batch_op.drop_column("description")
