"""add users table

Revision ID: a001_add_users_table
Revises: 940b0a6a564e
Create Date: 2026-07-25 15:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = 'a001_add_users_table'
down_revision = '940b0a6a564e'
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    is_postgres = bind.dialect.name == 'postgresql'

    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('email', sa.String(255), nullable=False, unique=True, index=True),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('full_name', sa.String(255), nullable=True),
        sa.Column('role', sa.String(20), nullable=False, server_default='operator'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('1')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('user_id', sa.String(36), nullable=True),
        sa.Column('branch_id', sa.String(36), nullable=True),
    )

    # Seed default admin user
    # password: password123  bcrypt hash
    # NOTE: dormant — no endpoint currently authenticates; auth code is kept for future use.
    admin_hash = '$2b$12$neBwOJG32Kg.3ebYBFtp/ObxyARXAjjN7xKXSC6SOMoZVYIKm8ybO'
    if is_postgres:
        op.execute(f"""
            INSERT INTO users (id, email, password_hash, full_name, role, is_active)
            VALUES (gen_random_uuid(), 'admin@ezoo.pos', '{admin_hash}', 'Administrator', 'admin', true)
            ON CONFLICT (email) DO NOTHING;
        """)
    else:
        op.execute(f"""
            INSERT INTO users (id, email, password_hash, full_name, role, is_active)
            VALUES (lower(hex(randomblob(16))), 'admin@ezoo.pos', '{admin_hash}', 'Administrator', 'admin', 1);
        """)


def downgrade() -> None:
    op.drop_table('users')
