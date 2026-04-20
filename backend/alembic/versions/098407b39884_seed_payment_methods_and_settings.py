"""seed_payment_methods_and_settings

Revision ID: 098407b39884
Revises: t008_settings_sync
Create Date: 2026-04-04 23:28:17.024612

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '098407b39884'
down_revision = 't008_settings_sync'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Seed Payment Methods
    op.execute(
        """
        INSERT INTO payment_methods (name, is_active)
        VALUES
            ('Cash', true),
            ('Card', true),
            ('Bank Transfer', true)
        ON CONFLICT (name) DO NOTHING;
        """
    )

    # Seed Settings
    op.execute(
        """
        INSERT INTO settings (key, value, description)
        VALUES
            ('vat_enabled', 'false', 'Enable/disable VAT calculation'),
            ('vat_rate', '0', 'Standard VAT rate (e.g., 0.16)'),
            ('vat_type', 'percent', 'VAT calculation type (fixed or percent)'),
            ('currency', 'GBP', 'System currency symbol')
        ON CONFLICT (key) DO NOTHING;
        """
    )


def downgrade() -> None:
    # Remove seeded payment methods
    op.execute("DELETE FROM payment_methods WHERE name IN ('Cash', 'Card', 'Bank Transfer');")
    
    # Remove seeded settings
    op.execute("DELETE FROM settings WHERE key IN ('vat_enabled', 'vat_rate', 'vat_type', 'currency');")
