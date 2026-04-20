"""seed default fee presets

Revision ID: t009_seed_fee_presets
Revises: 098407b39884
Create Date: 2026-04-05 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 't009_seed_fee_presets'
down_revision = '098407b39884'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Seed default fee presets for location 1 (10, 30, 50, 100 for each fee type)."""
    # T053: Seed default fee presets for each fee type per location
    op.execute(
        """
        INSERT INTO settings (key, value, description)
        VALUES
            ('fee_presets_1_shipping', '[10, 30, 50, 100]', 'Default shipping fee presets for location 1'),
            ('fee_presets_1_installation', '[10, 30, 50, 100]', 'Default installation fee presets for location 1'),
            ('fee_presets_1_custom', '[10, 30, 50, 100]', 'Default custom fee presets for location 1')
        ON CONFLICT (key) DO NOTHING;
        """
    )


def downgrade() -> None:
    """Remove seeded fee presets."""
    op.execute(
        "DELETE FROM settings WHERE key IN ('fee_presets_1_shipping', 'fee_presets_1_installation', 'fee_presets_1_custom');"
    )
