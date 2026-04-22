"""
Integration tests for customer credit limit enforcement.
Task: T032
"""

import pytest
from decimal import Decimal
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.customer import Customer, CustomerLedger
from app.models.sale import Sale
from app.models.payment_method import PaymentMethod
from app.modules.customers.service import CustomerService
from app.modules.pos.service import SaleService
from app.schemas.sale import SaleCreate, SaleItemCreate
from app.core.constants import LedgerTransactionType


@pytest.mark.asyncio
async def test_credit_sale_within_limit(db: AsyncSession):
    """Test that credit sales work when within limit."""
    service = CustomerService(db)

    customer = Customer(
        name=f"Test Customer {uuid4()}",
        phone="123456789",
        credit_limit=Decimal("1000.00"),
    )
    db.add(customer)

    pm = PaymentMethod(name="Cash", is_active=True)
    db.add(pm)
    await db.flush()

    product = await create_test_product(db)
    await db.flush()

    sale_service = SaleService(db)

    sale_data = SaleCreate(
        items=[SaleItemCreate(product_id=product.id, quantity=1)],
        payments=[{"payment_method_id": str(pm.id), "amount": "50.00"}],
        customer_id=str(customer.id),
    )

    sale = await sale_service.create_sale(sale_data)
    assert sale.customer_id == customer.id

    summary = await service.get_customer_summary(customer.id)
    assert summary.total_sales == Decimal("50.00")


@pytest.mark.asyncio
async def test_credit_limit_exceeded_raises(db: AsyncSession):
    """Test that sales exceeding credit limit are rejected."""
    service = CustomerService(db)

    customer = Customer(
        name=f"Test Customer {uuid4()}",
        phone="123456789",
        credit_limit=Decimal("100.00"),
    )
    db.add(customer)

    pm = PaymentMethod(name="Cash", is_active=True)
    db.add(pm)
    await db.flush()

    product = await create_test_product(db, selling_price=Decimal("200.00"))
    await db.flush()

    sale_service = SaleService(db)

    sale_data = SaleCreate(
        items=[SaleItemCreate(product_id=product.id, quantity=1)],
        payments=[{"payment_method_id": str(pm.id), "amount": "50.00"}],
        customer_id=str(customer.id),
    )

    with pytest.raises(ValueError, match="Credit limit exceeded"):
        await sale_service.create_sale(sale_data)


@pytest.mark.asyncio
async def test_reversal_creates_return_entry(db: AsyncSession):
    """Test that reversing a customer-linked sale creates RETURN entry."""
    service = CustomerService(db)

    customer = Customer(
        name=f"Test Customer {uuid4()}",
        phone="123456789",
        credit_limit=Decimal("1000.00"),
    )
    db.add(customer)

    pm = PaymentMethod(name="Cash", is_active=True)
    db.add(pm)
    await db.flush()

    product = await create_test_product(db)
    await db.flush()

    sale_service = SaleService(db)

    sale_data = SaleCreate(
        items=[SaleItemCreate(product_id=product.id, quantity=1)],
        payments=[{"payment_method_id": str(pm.id), "amount": "50.00"}],
        customer_id=str(customer.id),
    )

    sale = await sale_service.create_sale(sale_data)

    reversal = await sale_service.reverse_sale(sale.id, "Test reversal")

    summary = await service.get_customer_summary(customer.id)
    assert summary.total_returns > 0
    assert summary.balance >= 0


async def create_test_product(db: AsyncSession, selling_price: Decimal = Decimal("50.00")):
    """Helper to create a test product."""
    from app.models.product import Product

    product = Product(
        name=f"Test Product {uuid4()}",
        sku=f"SKU-{uuid4()}",
        selling_price=selling_price,
        base_price=Decimal("25.00"),
        stock_quantity=100,
        is_active=True,
    )
    db.add(product)
    return product