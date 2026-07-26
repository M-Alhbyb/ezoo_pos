"""Timestamp ordering invariant tests.

Verifies that:
1. Python-side defaults produce microsecond-precision timestamps (no collisions)
2. Tie-breaking on Model.id provides deterministic ordering when timestamps match
3. Running balance chain is consistent for wallet/ledger tables
"""

import uuid

import pytest
from sqlalchemy import inspect, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.product import Product
from app.models.sale import Sale


async def test_created_at_has_python_default(db_session: AsyncSession):
    """BaseModel.created_at must have a Python-side default for microsecond precision."""
    from app.core.database import BaseModel

    mapper = inspect(Product)
    col = mapper.columns.created_at

    assert col.server_default is not None, "created_at must have server_default"
    assert col.default is not None, (
        "created_at must have a Python-side default. "
        "Without it, SQLite CURRENT_TIMESTAMP gives only second-level precision."
    )


async def test_tie_break_by_id_deterministic(db_session: AsyncSession):
    """When two rows share the same created_at second, order_by desc must be deterministic via id."""
    from app.models.payment_method import PaymentMethod

    pm = PaymentMethod(id=uuid.uuid4(), name="Cash")
    db_session.add(pm)
    await db_session.flush()

    now_str = "2026-01-01 12:00:00"

    id1 = uuid.uuid4()
    id2 = uuid.uuid4()

    s1 = Sale(
        id=id1,
        payment_method_id=pm.id,
        subtotal=100,
        grand_total=100,
    )
    s2 = Sale(
        id=id2,
        payment_method_id=pm.id,
        subtotal=200,
        grand_total=200,
    )
    db_session.add_all([s1, s2])
    await db_session.flush()

    # Override created_at to the same second to force tie
    await db_session.execute(
        text("UPDATE sales SET created_at = :ts WHERE id = :id").bindparams(ts=now_str, id=str(id1))
    )
    await db_session.execute(
        text("UPDATE sales SET created_at = :ts WHERE id = :id").bindparams(ts=now_str, id=str(id2))
    )

    query = (
        select(Sale)
        .where(Sale.id.in_([id1, id2]))
        .order_by(
            Sale.created_at.desc(),
            Sale.id.desc(),
        )
    )
    result = await db_session.execute(query)
    rows = list(result.scalars().all())

    assert len(rows) == 2

    if id2 > id1:
        assert rows[0].id == id2
        assert rows[1].id == id1
    else:
        assert rows[0].id == id1
        assert rows[1].id == id2


async def test_partner_wallet_transaction_timestamps(db_session: AsyncSession):
    """50 rapid inserts must produce distinct timestamps and a consistent balance chain."""
    from app.models.partner_wallet_transaction import PartnerWalletTransaction
    from app.models.partner import Partner

    partner = Partner(name="Timestamp Test Partner", investment_amount=0, share_percentage=50)
    db_session.add(partner)
    await db_session.flush()

    inserted_ids = []
    balance = 0
    for i in range(50):
        amount = 10.0 + i
        balance += amount
        txn = PartnerWalletTransaction(
            partner_id=partner.id,
            amount=amount,
            transaction_type="sale_profit",
            balance_after=balance,
            description=f"Row {i}",
        )
        db_session.add(txn)
        await db_session.flush()
        inserted_ids.append(txn.id)

    await db_session.commit()

    # Query in created_at order (desc), then id desc
    result = await db_session.execute(
        select(PartnerWalletTransaction)
        .where(PartnerWalletTransaction.partner_id == partner.id)
        .order_by(
            PartnerWalletTransaction.created_at.desc(),
            PartnerWalletTransaction.id.desc(),
        )
    )
    rows = list(result.scalars().all())

    assert len(rows) == 50

    # All created_at values must be distinct
    timestamps = [r.created_at for r in rows]
    assert len(set(timestamps)) == 50, (
        f"Expected 50 distinct timestamps, got {len(set(timestamps))}"
    )

    # Query order (desc) should match reversed insertion order
    reversed_ids = list(reversed(inserted_ids))
    actual_ids = [r.id for r in rows]
    assert actual_ids == reversed_ids, (
        "Query order does not match reversed insertion order"
    )

    # Running balance chain consistency: newer.balance_after = older.balance_after + newer.amount
    for i in range(len(rows) - 1):
        newer = rows[i]  # more recent
        older = rows[i + 1]  # older
        expected = float(older.balance_after) + float(newer.amount)
        assert float(newer.balance_after) == expected, (
            f"Balance chain broken at row {i}: "
            f"older.balance_after={older.balance_after} + newer.amount={newer.amount} = {expected}, "
            f"but newer.balance_after={newer.balance_after}"
        )


async def test_supplier_ledger_timestamps(db_session: AsyncSession):
    """50 rapid inserts must produce distinct timestamps and a consistent balance chain."""
    from app.models.supplier_ledger import SupplierLedger
    from app.models.supplier import Supplier
    from decimal import Decimal

    supplier = Supplier(name="Timestamp Test Supplier")
    db_session.add(supplier)
    await db_session.flush()

    inserted_ids = []
    balance = Decimal("0")
    for i in range(50):
        amount = Decimal(f"{10 + i}.00")
        balance += amount
        entry = SupplierLedger(
            supplier_id=supplier.id,
            type="purchase",
            amount=amount,
            note=f"Row {i}",
        )
        db_session.add(entry)
        await db_session.flush()
        inserted_ids.append(entry.id)

    await db_session.commit()

    result = await db_session.execute(
        select(SupplierLedger)
        .where(SupplierLedger.supplier_id == supplier.id)
        .order_by(
            SupplierLedger.created_at.desc(),
            SupplierLedger.id.desc(),
        )
    )
    rows = list(result.scalars().all())

    assert len(rows) == 50

    # All created_at values must be distinct
    timestamps = [r.created_at for r in rows]
    assert len(set(timestamps)) == 50, (
        f"Expected 50 distinct timestamps, got {len(set(timestamps))}"
    )

    # Query order (desc) should match reversed insertion order
    reversed_ids = list(reversed(inserted_ids))
    actual_ids = [r.id for r in rows]
    assert actual_ids == reversed_ids, (
        "Query order does not match reversed insertion order"
    )


async def test_customer_ledger_timestamps(db_session: AsyncSession):
    """50 rapid inserts must produce distinct timestamps and a consistent balance chain."""
    from app.models.customer import Customer, CustomerLedger
    from decimal import Decimal

    customer = Customer(name="Timestamp Test Customer", phone="0000", credit_limit=Decimal("99999.00"))
    db_session.add(customer)
    await db_session.flush()

    inserted_ids = []
    for i in range(50):
        entry = CustomerLedger(
            customer_id=customer.id,
            type="credit",
            amount=Decimal(f"{10 + i}.00"),
            note=f"Row {i}",
        )
        db_session.add(entry)
        await db_session.flush()
        inserted_ids.append(entry.id)

    await db_session.commit()

    result = await db_session.execute(
        select(CustomerLedger)
        .where(CustomerLedger.customer_id == customer.id)
        .order_by(
            CustomerLedger.created_at.desc(),
            CustomerLedger.id.desc(),
        )
    )
    rows = list(result.scalars().all())

    assert len(rows) == 50

    # All created_at values must be distinct
    timestamps = [r.created_at for r in rows]
    assert len(set(timestamps)) == 50, (
        f"Expected 50 distinct timestamps, got {len(set(timestamps))}"
    )

    # Query order (desc) should match reversed insertion order
    reversed_ids = list(reversed(inserted_ids))
    actual_ids = [r.id for r in rows]
    assert actual_ids == reversed_ids, (
        "Query order does not match reversed insertion order"
    )
