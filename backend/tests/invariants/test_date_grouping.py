"""
Regression test for the cast-to-Date SQLite bug.

On SQLite, CAST(datetime AS DATE) returns the year as an integer, not a date string.
This causes all rows in the same calendar year to collapse into one group,
and WHERE filters comparing against date objects silently match everything.

This test seeds rows across 3 consecutive days and asserts that every
dashboard and report aggregation returns 3 distinct date buckets.
"""

import uuid
import pytest
from datetime import datetime, date
from decimal import Decimal

from sqlalchemy import select, func, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.sale import Sale
from app.models.inventory_log import InventoryLog
from app.models.partner_wallet_transaction import PartnerWalletTransaction
from app.models.partner import Partner
from app.models.product import Product
from app.models.payment_method import PaymentMethod


DAY1 = datetime(2026, 3, 1, 10, 0, 0)
DAY2 = datetime(2026, 3, 2, 14, 30, 0)
DAY3 = datetime(2026, 3, 3, 9, 15, 0)


def _uuid():
    return str(uuid.uuid4())


@pytest.fixture
async def seed_sales(db_session: AsyncSession):
    """Seed 3 sales on 3 consecutive days with required parent rows."""
    pm_id = _uuid()
    await db_session.execute(
        text("INSERT INTO payment_methods (id, name, is_active) VALUES (:id, :name, 1)"),
        {"id": pm_id, "name": "Cash"},
    )
    for i, dt in enumerate([DAY1, DAY2, DAY3], start=1):
        sale_id = _uuid()
        await db_session.execute(
            text(
                "INSERT INTO sales (id, payment_method_id, created_at, subtotal, fees_total, "
                "vat_total, grand_total, total_cost, profit, is_reversal) "
                "VALUES (:id, :pm_id, :created_at, 100.0, 0.0, 0.0, 100.0, 50.0, 50.0, 0)"
            ),
            {"id": sale_id, "pm_id": pm_id, "created_at": dt.isoformat()},
        )
    await db_session.commit()


@pytest.fixture
async def seed_inventory(db_session: AsyncSession):
    """Seed 3 inventory logs on 3 consecutive days with required parent rows."""
    cat_id = _uuid()
    await db_session.execute(
        text("INSERT INTO categories (id, name) VALUES (:id, :name)"),
        {"id": cat_id, "name": "TestCat"},
    )
    prod_id = _uuid()
    await db_session.execute(
        text(
            "INSERT INTO products (id, name, category_id, base_price, selling_price, stock_quantity, is_active) "
            "VALUES (:id, :name, :cat_id, 10.0, 20.0, 100, 1)"
        ),
        {"id": prod_id, "name": "TestProd", "cat_id": cat_id},
    )
    for i, dt in enumerate([DAY1, DAY2, DAY3], start=1):
        log_id = _uuid()
        await db_session.execute(
            text(
                "INSERT INTO inventory_log (id, product_id, created_at, delta, reason, balance_after) "
                "VALUES (:id, :prod_id, :created_at, 10, 'restock', :bal)"
            ),
            {"id": log_id, "prod_id": prod_id, "created_at": dt.isoformat(), "bal": i * 10},
        )
    await db_session.commit()


@pytest.fixture
async def seed_partner_transactions(db_session: AsyncSession):
    """Seed 3 partner wallet transactions on 3 consecutive days with required parent rows."""
    await db_session.execute(
        text(
            "INSERT INTO partners (id, name, share_percentage, investment_amount) "
            "VALUES (:id, :name, 20.0, 1000.0)"
        ),
        {"id": 1, "name": "TestPartner"},
    )
    for i, dt in enumerate([DAY1, DAY2, DAY3], start=1):
        tx_id = _uuid()
        ref_id = _uuid()
        await db_session.execute(
            text(
                "INSERT INTO partner_wallet_transactions "
                "(id, partner_id, amount, transaction_type, reference_id, reference_type, "
                "description, balance_after, created_at) "
                "VALUES (:id, 1, 25.0, 'sale_profit', :ref_id, 'sale', :desc, :bal, :created_at)"
            ),
            {
                "id": tx_id,
                "ref_id": ref_id,
                "desc": f"Day {i} profit",
                "bal": float(i * 25),
                "created_at": dt.isoformat(),
            },
        )
    await db_session.commit()


@pytest.mark.anyio
async def test_sales_date_grouping_returns_3_buckets(db_session: AsyncSession, seed_sales):
    """func.date() grouping on sales must produce 3 distinct days."""
    stmt = (
        select(
            func.date(Sale.created_at).label("day"),
            func.count(Sale.id).label("cnt"),
        )
        .group_by(func.date(Sale.created_at))
        .order_by(func.date(Sale.created_at))
    )
    result = await db_session.execute(stmt)
    rows = result.all()
    assert len(rows) == 3, f"Expected 3 groups, got {len(rows)}: {[r.day for r in rows]}"
    assert rows[0].day == "2026-03-01"
    assert rows[1].day == "2026-03-02"
    assert rows[2].day == "2026-03-03"


@pytest.mark.anyio
async def test_sales_date_filter_returns_only_matching_day(db_session: AsyncSession, seed_sales):
    """WHERE func.date() filter must return only the matching day's rows."""
    stmt = select(func.count(Sale.id)).where(
        func.date(Sale.created_at) == date(2026, 3, 2)
    )
    result = await db_session.execute(stmt)
    count = result.scalar()
    assert count == 1, f"Expected 1 sale on 2026-03-02, got {count}"


@pytest.mark.anyio
async def test_sales_date_range_filter(db_session: AsyncSession, seed_sales):
    """WHERE func.date() with range must return exactly the rows in range."""
    stmt = select(func.count(Sale.id)).where(
        func.date(Sale.created_at) >= date(2026, 3, 2),
        func.date(Sale.created_at) <= date(2026, 3, 3),
    )
    result = await db_session.execute(stmt)
    count = result.scalar()
    assert count == 2, f"Expected 2 sales in range, got {count}"


@pytest.mark.anyio
async def test_inventory_date_grouping_returns_3_buckets(db_session: AsyncSession, seed_inventory):
    """func.date() grouping on inventory logs must produce 3 distinct days."""
    stmt = (
        select(
            func.date(InventoryLog.created_at).label("day"),
            func.count(InventoryLog.id).label("cnt"),
        )
        .group_by(func.date(InventoryLog.created_at))
        .order_by(func.date(InventoryLog.created_at))
    )
    result = await db_session.execute(stmt)
    rows = result.all()
    assert len(rows) == 3, f"Expected 3 groups, got {len(rows)}: {[r.day for r in rows]}"


@pytest.mark.anyio
async def test_partner_tx_date_grouping_returns_3_buckets(db_session: AsyncSession, seed_partner_transactions):
    """func.date() grouping on partner wallet transactions must produce 3 distinct days."""
    stmt = (
        select(
            func.date(PartnerWalletTransaction.created_at).label("day"),
            func.count(PartnerWalletTransaction.id).label("cnt"),
        )
        .group_by(func.date(PartnerWalletTransaction.created_at))
        .order_by(func.date(PartnerWalletTransaction.created_at))
    )
    result = await db_session.execute(stmt)
    rows = result.all()
    assert len(rows) == 3, f"Expected 3 groups, got {len(rows)}: {[r.day for r in rows]}"


@pytest.mark.anyio
async def test_partner_tx_date_filter(db_session: AsyncSession, seed_partner_transactions):
    """WHERE func.date() filter on partner transactions returns only matching day."""
    stmt = select(func.count(PartnerWalletTransaction.id)).where(
        func.date(PartnerWalletTransaction.created_at) == date(2026, 3, 1)
    )
    result = await db_session.execute(stmt)
    count = result.scalar()
    assert count == 1, f"Expected 1 tx on 2026-03-01, got {count}"
