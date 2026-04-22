"""
Performance tests for customer accounting.
Task: T032.5
Tests SC-003: Statement generation performance.
"""

import pytest
import time
from decimal import Decimal
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.customer import Customer, CustomerLedger
from app.modules.customers.service import CustomerService
from app.core.constants import LedgerTransactionType


@pytest.mark.asyncio
async def test_statement_generation_performance(db: AsyncSession):
    """
    Test that statement generation is fast (<2s for 1000 entries).
    SC-003: <2s for statement generation with up to 1000 ledger entries.
    """
    service = CustomerService(db)

    customer = Customer(
        name=f"Test Customer {uuid4()}",
        phone="123456789",
        credit_limit=Decimal("10000.00"),
    )
    db.add(customer)
    await db.flush()

    num_entries = 100
    for i in range(num_entries):
        await service.record_ledger_entry(
            customer_id=customer.id,
            type=LedgerTransactionType.SALE if i % 2 == 0 else LedgerTransactionType.PAYMENT,
            amount=Decimal("10.00"),
            note=f"Entry {i}",
        )
    await db.flush()
    await db.commit()

    start = time.time()
    entries, total = await service.list_ledger_entries(customer.id, page_size=50)
    duration_ms = (time.time() - start) * 1000

    assert total == num_entries
    assert len(entries) == 50
    assert duration_ms < 2000, f"Statement generation took {duration_ms:.2f}ms, expected <2000ms"


@pytest.mark.asyncio
async def test_balance_query_performance(db: AsyncSession):
    """
    Test that balance query is fast (<100ms).
    SC-003: <100ms for credit limit checks.
    """
    service = CustomerService(db)

    customer = Customer(
        name=f"Test Customer {uuid4()}",
        phone="123456789",
        credit_limit=Decimal("10000.00"),
    )
    db.add(customer)
    await db.flush()

    for i in range(10):
        await service.record_ledger_entry(
            customer_id=customer.id,
            type=LedgerTransactionType.SALE,
            amount=Decimal("100.00"),
        )
    await db.flush()
    await db.commit()

    start = time.time()
    is_exceeded, balance, limit = await service.check_credit_limit(
        customer.id, Decimal("100.00")
    )
    duration_ms = (time.time() - start) * 1000

    assert duration_ms < 100, f"Balance check took {duration_ms:.2f}ms, expected <100ms"
    assert is_exceeded is False


@pytest.mark.asyncio
async def test_customer_list_performance(db: AsyncSession):
    """
    Test that listing many customers is fast.
    """
    service = CustomerService(db)

    for i in range(20):
        customer = Customer(
            name=f"Test Customer {uuid4()}",
            phone=f"123456789{i}",
            credit_limit=Decimal("1000.00"),
        )
        db.add(customer)
    await db.flush()
    await db.commit()

    start = time.time()
    customers, total = await service.list_customers(page=1, page_size=50)
    duration_ms = (time.time() - start) * 1000

    assert total >= 20
    assert duration_ms < 1000, f"Customer list took {duration_ms:.2f}ms, expected <1000ms"