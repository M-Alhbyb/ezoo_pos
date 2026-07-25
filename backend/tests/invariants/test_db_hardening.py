"""Database hardening tests.

Verifies that SQLite PRAGMAs are correctly configured and that foreign
key enforcement is active.
"""

import uuid

import pytest
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from app.models.sale_item import SaleItem


async def test_foreign_keys_are_enabled(engine):
    """PRAGMA foreign_keys must be 1 on every connection from the engine."""
    async with engine.connect() as conn:
        result = await conn.execute(text("PRAGMA foreign_keys"))
        fk = result.scalar()
    assert fk == 1, f"foreign_keys pragma is {fk}, expected 1"


async def test_journal_mode_is_wal(engine):
    """PRAGMA journal_mode must be WAL."""
    async with engine.connect() as conn:
        result = await conn.execute(text("PRAGMA journal_mode"))
        mode = result.scalar()
    assert mode == "wal", f"journal_mode is {mode!r}, expected 'wal'"


async def test_insert_orphan_sale_item_raises(engine):
    """Inserting a SaleItem with a nonexistent sale_id must raise IntegrityError."""
    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

    maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with maker() as session:
        orphan = SaleItem(
            id=uuid.uuid4(),
            sale_id=uuid.uuid4(),  # does not exist
            product_id=uuid.uuid4(),  # does not exist either, but FK on sale_id fires first
            product_name="Test",
            quantity=1,
            unit_price=100,
            line_total=100,
        )
        session.add(orphan)
        with pytest.raises(IntegrityError):
            await session.flush()
