"""
Unit tests for customer accounting balance calculation.
Task: T031
"""

import pytest
from decimal import Decimal
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.customer import Customer, CustomerLedger
from app.modules.customers.service import CustomerService
from app.core.constants import LedgerTransactionType


@pytest.mark.asyncio
async def test_balance_calculation(db: AsyncSession):
    """Test that balance is correctly derived from ledger entries."""
    service = CustomerService(db)

    customer = Customer(
        name=f"Test Customer {uuid4()}",
        phone="123456789",
        credit_limit=Decimal("1000.00"),
    )
    db.add(customer)
    await db.flush()

    await service.record_ledger_entry(
        customer_id=customer.id,
        type=LedgerTransactionType.SALE,
        amount=Decimal("500.00"),
    )
    await db.flush()

    await service.record_ledger_entry(
        customer_id=customer.id,
        type=LedgerTransactionType.PAYMENT,
        amount=Decimal("200.00"),
    )
    await db.flush()

    await service.record_ledger_entry(
        customer_id=customer.id,
        type=LedgerTransactionType.RETURN,
        amount=Decimal("50.00"),
    )
    await db.commit()

    summary = await service.get_customer_summary(customer.id)
    assert summary.total_sales == Decimal("500.00")
    assert summary.total_payments == Decimal("200.00")
    assert summary.total_returns == Decimal("50.00")
    assert summary.balance == Decimal("250.00")


@pytest.mark.asyncio
async def test_credit_limit_check(db: AsyncSession):
    """Test credit limit enforcement."""
    service = CustomerService(db)

    customer = Customer(
        name=f"Test Customer {uuid4()}",
        phone="123456789",
        credit_limit=Decimal("100.00"),
    )
    db.add(customer)
    await db.flush()

    is_exceeded, balance, limit = await service.check_credit_limit(
        customer.id, Decimal("150.00")
    )
    assert not is_exceeded
    assert balance == Decimal("0")
    assert limit == Decimal("100.00")

    is_exceeded, balance, limit = await service.check_credit_limit(
        customer.id, Decimal("50.00")
    )
    assert not is_exceeded

    is_exceeded, balance, limit = await service.check_credit_limit(
        customer.id, Decimal("101.00")
    )
    assert is_exceeded


@pytest.mark.asyncio
async def test_ledger_immutability(db: AsyncSession):
    """Test that ledger entries cannot be updated."""
    service = CustomerService(db)

    customer = Customer(
        name=f"Test Customer {uuid4()}",
        phone="123456789",
        credit_limit=Decimal("1000.00"),
    )
    db.add(customer)
    await db.flush()

    entry = await service.record_ledger_entry(
        customer_id=customer.id,
        type=LedgerTransactionType.SALE,
        amount=Decimal("100.00"),
    )
    await db.commit()

    entry.amount = Decimal("999.00")
    with pytest.raises(RuntimeError, match="immutable"):
        await db.commit()


@pytest.mark.asyncio
async def test_payment_idempotency(db: AsyncSession):
    """Test that duplicate payments are prevented via idempotency key."""
    service = CustomerService(db)

    customer = Customer(
        name=f"Test Customer {uuid4()}",
        phone="123456789",
        credit_limit=Decimal("1000.00"),
    )
    db.add(customer)
    await db.flush()

    idempotency_key = "payment-12345"

    entry1 = await service.record_payment(
        customer_id=customer.id,
        amount=Decimal("100.00"),
        payment_method="Cash",
        note="Test payment",
        idempotency_key=idempotency_key,
    )
    assert entry1 is not None

    entry2 = await service.record_payment(
        customer_id=customer.id,
        amount=Decimal("100.00"),
        payment_method="Cash",
        note="Duplicate payment",
        idempotency_key=idempotency_key,
    )
    assert entry2.id == entry1.id