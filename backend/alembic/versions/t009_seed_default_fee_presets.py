from alembic import op

revision = 't009_seed_fee_presets'
down_revision = '098407b39884'
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == 'postgresql':
        op.execute(
            '''
            INSERT INTO settings (id, key, value, description)
            VALUES
                (gen_random_uuid(), 'fee_presets_1_shipping', '[10, 30, 50, 100]', 'Default shipping fee presets for location 1'),
                (gen_random_uuid(), 'fee_presets_1_installation', '[10, 30, 50, 100]', 'Default installation fee presets for location 1'),
                (gen_random_uuid(), 'fee_presets_1_custom', '[10, 30, 50, 100]', 'Default custom fee presets for location 1')
            ON CONFLICT (key) DO NOTHING;
            '''
        )
    else:
        op.execute(
            '''
            INSERT INTO settings (id, key, value, description)
            VALUES
                (lower(hex(randomblob(16))), 'fee_presets_1_shipping', '[10, 30, 50, 100]', 'Default shipping fee presets for location 1'),
                (lower(hex(randomblob(16))), 'fee_presets_1_installation', '[10, 30, 50, 100]', 'Default installation fee presets for location 1'),
                (lower(hex(randomblob(16))), 'fee_presets_1_custom', '[10, 30, 50, 100]', 'Default custom fee presets for location 1');
            '''
        )


def downgrade() -> None:
    op.execute(
        '''DELETE FROM settings WHERE key IN ('fee_presets_1_shipping', 'fee_presets_1_installation', 'fee_presets_1_custom');'''
    )
