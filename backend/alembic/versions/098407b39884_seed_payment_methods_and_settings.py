from alembic import op

revision = '098407b39884'
down_revision = 't008_settings_sync'
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == 'postgresql':
        op.execute(
            '''
            INSERT INTO payment_methods (id, name, is_active)
            VALUES
                (gen_random_uuid(), 'Cash', true),
                (gen_random_uuid(), 'Card', true),
                (gen_random_uuid(), 'Bank Transfer', true)
            ON CONFLICT (name) DO NOTHING;
            '''
        )
        op.execute(
            '''
            INSERT INTO settings (id, key, value, description)
            VALUES
                (gen_random_uuid(), 'vat_enabled', 'false', 'Enable/disable VAT calculation'),
                (gen_random_uuid(), 'vat_rate', '0', 'Standard VAT rate (e.g., 0.16)'),
                (gen_random_uuid(), 'vat_type', 'percent', 'VAT calculation type (fixed or percent)'),
                (gen_random_uuid(), 'currency', 'GBP', 'System currency symbol')
            ON CONFLICT (key) DO NOTHING;
            '''
        )
    else:
        op.execute(
            '''
            INSERT INTO payment_methods (id, name, is_active)
            VALUES
                (lower(hex(randomblob(16))), 'Cash', true),
                (lower(hex(randomblob(16))), 'Card', true),
                (lower(hex(randomblob(16))), 'Bank Transfer', true);
            '''
        )
        op.execute(
            '''
            INSERT INTO settings (id, key, value, description)
            VALUES
                (lower(hex(randomblob(16))), 'vat_enabled', 'false', 'Enable/disable VAT calculation'),
                (lower(hex(randomblob(16))), 'vat_rate', '0', 'Standard VAT rate (e.g., 0.16)'),
                (lower(hex(randomblob(16))), 'vat_type', 'percent', 'VAT calculation type (fixed or percent)'),
                (lower(hex(randomblob(16))), 'currency', 'GBP', 'System currency symbol');
            '''
        )


def downgrade() -> None:
    op.execute(
        '''DELETE FROM payment_methods WHERE name IN ('Cash', 'Card', 'Bank Transfer');'''
    )
    op.execute(
        '''DELETE FROM settings WHERE key IN ('vat_enabled', 'vat_rate', 'vat_type', 'currency');'''
    )
