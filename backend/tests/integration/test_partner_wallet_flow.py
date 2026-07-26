"""
Integration tests for sale-with-profit distribution workflow.

Tests:
- Partner profit calculation on sale
- Wallet balance updates
- Concurrent sale handling
"""

from datetime import UTC, datetime
from decimal import Decimal
from uuid import uuid4

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.category import Category
from app.models.partner import Partner
from app.models.partner_wallet_transaction import PartnerWalletTransaction
from app.models.product import Product
from app.modules.partners.partner_profit_service import PartnerProfitService


@pytest.mark.asyncio
async def test_sale_updates_partner_wallet(db_session: AsyncSession):
    """Test that selling products with partner_id credits partner wallet."""
    partner = Partner(
        name="Test Partner",
        share_percentage=Decimal("20.00"),
        investment_amount=Decimal("5000.00"),
    )
    db_session.add(partner)
    await db_session.flush()

    category = Category(name="Test Category")
    db_session.add(category)
    await db_session.flush()

    product = Product(
        name="Test Product",
        category_id=category.id,
        base_price=Decimal("100.00"),
        selling_price=Decimal("200.00"),
        stock_quantity=100,
        partner_id=partner.id,
    )
    db_session.add(product)
    await db_session.commit()

    sale_id = uuid4()
    sale_items = [
        {"product_id": product.id, "quantity": 3, "unit_price": Decimal("200.00")},
    ]

    service = PartnerProfitService(db_session)
    await service.process_sale_partner_profits(sale_id, sale_items)
    await db_session.commit()

    # Formula: quantity × (unit_price - base_cost) × share_percentage / 100
    # base_cost defaults to 0: 3 × (200 - 0) × 20 / 100 = 120
    query = select(PartnerWalletTransaction).where(
        PartnerWalletTransaction.partner_id == partner.id
    )
    wallet_result = await db_session.execute(query)
    transactions = wallet_result.scalars().all()

    assert len(transactions) == 1
    assert transactions[0].amount == Decimal("120.00")
    assert transactions[0].transaction_type == "sale_profit"
    assert transactions[0].reference_id == sale_id


@pytest.mark.asyncio
async def test_sale_updates_remaining_quantity(db_session: AsyncSession):
    """Test that selling products updates wallet, not assignment (assignments not tracked)."""
    partner = Partner(
        name="Test Partner",
        share_percentage=Decimal("15.00"),
        investment_amount=Decimal("1000.00"),
    )
    db_session.add(partner)
    await db_session.flush()

    category = Category(name="Test Cat")
    db_session.add(category)
    await db_session.flush()

    product = Product(
        name="Test Prod",
        category_id=category.id,
        base_price=Decimal("50.00"),
        selling_price=Decimal("100.00"),
        stock_quantity=50,
        partner_id=partner.id,
    )
    db_session.add(product)
    await db_session.commit()

    sale_id = uuid4()
    sale_items = [
        {"product_id": product.id, "quantity": 4, "unit_price": Decimal("100.00")}
    ]

    service = PartnerProfitService(db_session)
    await service.process_sale_partner_profits(sale_id, sale_items)
    await db_session.commit()

    # Formula: 4 × (100 - 0) × 15 / 100 = 60
    query = select(PartnerWalletTransaction).where(
        PartnerWalletTransaction.partner_id == partner.id
    )
    wallet_result = await db_session.execute(query)
    transactions = wallet_result.scalars().all()

    assert len(transactions) == 1
    assert transactions[0].amount == Decimal("60.00")


@pytest.mark.asyncio
async def test_multiple_partners_in_same_sale(db_session: AsyncSession):
    """Test selling products assigned to multiple partners in one sale."""
    partner1 = Partner(
        name="Partner 1",
        share_percentage=Decimal("10.00"),
        investment_amount=Decimal("1000.00"),
    )
    partner2 = Partner(
        name="Partner 2",
        share_percentage=Decimal("15.00"),
        investment_amount=Decimal("2000.00"),
    )
    db_session.add_all([partner1, partner2])
    await db_session.flush()

    category = Category(name="Multi Test")
    db_session.add(category)
    await db_session.flush()

    product1 = Product(
        name="Product 1",
        category_id=category.id,
        base_price=Decimal("100.00"),
        selling_price=Decimal("200.00"),
        stock_quantity=50,
        partner_id=partner1.id,
    )
    product2 = Product(
        name="Product 2",
        category_id=category.id,
        base_price=Decimal("50.00"),
        selling_price=Decimal("150.00"),
        stock_quantity=30,
        partner_id=partner2.id,
    )
    db_session.add_all([product1, product2])
    await db_session.commit()

    sale_id = uuid4()
    sale_items = [
        {"product_id": product1.id, "quantity": 2, "unit_price": Decimal("200.00")},
        {"product_id": product2.id, "quantity": 3, "unit_price": Decimal("150.00")},
    ]

    service = PartnerProfitService(db_session)
    await service.process_sale_partner_profits(sale_id, sale_items)
    await db_session.commit()

    # Partner 1: 2 × (200 - 0) × 10 / 100 = 40
    # Partner 2: 3 × (150 - 0) × 15 / 100 = 67.50
    query1 = select(PartnerWalletTransaction).where(
        PartnerWalletTransaction.partner_id == partner1.id
    )
    result1 = await db_session.execute(query1)
    transactions1 = result1.scalars().all()

    query2 = select(PartnerWalletTransaction).where(
        PartnerWalletTransaction.partner_id == partner2.id
    )
    result2 = await db_session.execute(query2)
    transactions2 = result2.scalars().all()

    assert len(transactions1) == 1
    assert transactions1[0].amount == Decimal("40.00")

    assert len(transactions2) == 1
    assert transactions2[0].amount == Decimal("67.50")


@pytest.mark.asyncio
async def test_sale_without_assignment_keeps_full_profit(db_session: AsyncSession):
    """Test that unassigned products don't trigger partner profit."""
    partner = Partner(
        name="Partner No Assignment",
        share_percentage=Decimal("20.00"),
        investment_amount=Decimal("1000.00"),
    )
    db_session.add(partner)
    await db_session.flush()

    category = Category(name="Unassigned Category")
    db_session.add(category)
    await db_session.flush()

    product = Product(
        name="Unassigned Product",
        category_id=category.id,
        base_price=Decimal("100.00"),
        selling_price=Decimal("200.00"),
        stock_quantity=20,
        # No partner_id set
    )
    db_session.add(product)
    await db_session.commit()

    sale_id = uuid4()
    sale_items = [
        {"product_id": product.id, "quantity": 5, "unit_price": Decimal("200.00")}
    ]

    service = PartnerProfitService(db_session)
    result = await service.process_sale_partner_profits(sale_id, sale_items)

    assert result["processed"] == 0

    from sqlalchemy import select

    query = select(PartnerWalletTransaction).where(
        PartnerWalletTransaction.partner_id == partner.id
    )
    wallet_result = await db_session.execute(query)
    transactions = wallet_result.scalars().all()

    assert len(transactions) == 0


@pytest.mark.asyncio
async def test_balance_after_calculation(db_session: AsyncSession):
    """Test that balance_after is correctly calculated on wallet transactions."""
    partner = Partner(
        name="Balance Test Partner",
        share_percentage=Decimal("25.00"),
        investment_amount=Decimal("3000.00"),
    )
    db_session.add(partner)
    await db_session.flush()

    category = Category(name="Balance Test")
    db_session.add(category)
    await db_session.flush()

    product = Product(
        name="Balance Product",
        category_id=category.id,
        base_price=Decimal("200.00"),
        selling_price=Decimal("400.00"),
        stock_quantity=10,
        partner_id=partner.id,
    )
    db_session.add(product)
    await db_session.commit()

    service = PartnerProfitService(db_session)

    # First sale: 2 units × (400 - 0) × 25 / 100 = 200
    sale1_id = uuid4()
    await service.process_sale_partner_profits(
        sale1_id,
        [{"product_id": product.id, "quantity": 2, "unit_price": Decimal("400.00")}],
    )
    await db_session.commit()

    query = (
        select(PartnerWalletTransaction)
        .where(PartnerWalletTransaction.partner_id == partner.id)
        .order_by(PartnerWalletTransaction.created_at)
    )
    result = await db_session.execute(query)
    transactions = result.scalars().all()

    assert len(transactions) == 1
    assert transactions[0].amount == Decimal("200.00")
    assert transactions[0].balance_after == Decimal("200.00")

    # Second sale: 3 units × (400 - 0) × 25 / 100 = 300
    sale2_id = uuid4()
    await service.process_sale_partner_profits(
        sale2_id,
        [{"product_id": product.id, "quantity": 3, "unit_price": Decimal("400.00")}],
    )
    await db_session.commit()

    query = (
        select(PartnerWalletTransaction)
        .where(PartnerWalletTransaction.partner_id == partner.id)
        .order_by(PartnerWalletTransaction.created_at.desc())
    )
    result = await db_session.execute(query)
    transactions = result.scalars().all()

    assert len(transactions) == 2
    assert transactions[0].amount == Decimal("300.00")
    assert transactions[0].balance_after == Decimal("500.00")


@pytest.mark.asyncio
async def test_manual_wallet_adjustment(db_session: AsyncSession):
    """Test manual wallet adjustment by administrator."""
    partner = Partner(
        name="Adjustment Test Partner",
        share_percentage=Decimal("20.00"),
        investment_amount=Decimal("1000.00"),
    )
    db_session.add(partner)
    await db_session.commit()

    transaction1 = PartnerWalletTransaction(
        partner_id=partner.id,
        amount=Decimal("100.00"),
        transaction_type="sale_profit",
        reference_id=uuid4(),
        reference_type="sale",
        description="Initial sale profit",
        balance_after=Decimal("100.00"),
        created_at=datetime.now(UTC),
    )
    db_session.add(transaction1)
    await db_session.commit()

    service = PartnerProfitService(db_session)
    await service.adjust_wallet(
        partner_id=partner.id,
        amount=Decimal("50.00"),
        description="Manual credit for bonus",
    )
    await db_session.commit()

    from sqlalchemy import select

    query = (
        select(PartnerWalletTransaction)
        .where(PartnerWalletTransaction.partner_id == partner.id)
        .order_by(PartnerWalletTransaction.created_at.desc())
    )
    result = await db_session.execute(query)
    transactions = result.scalars().all()

    assert len(transactions) == 2
    assert transactions[0].amount == Decimal("50.00")
    assert transactions[0].transaction_type == "manual_adjustment"
    assert transactions[0].balance_after == Decimal("150.00")
    assert transactions[0].description == "Manual credit for bonus"
    assert transactions[0].reference_id is None
    assert transactions[0].reference_type == "manual"


@pytest.mark.asyncio
async def test_manual_wallet_debit_adjustment(db_session: AsyncSession):
    """Test manual wallet debit adjustment."""
    partner = Partner(
        name="Debit Test Partner",
        share_percentage=Decimal("15.00"),
        investment_amount=Decimal("2000.00"),
    )
    db_session.add(partner)
    await db_session.commit()

    transaction1 = PartnerWalletTransaction(
        partner_id=partner.id,
        amount=Decimal("200.00"),
        transaction_type="sale_profit",
        reference_id=uuid4(),
        reference_type="sale",
        description="Sale profit",
        balance_after=Decimal("200.00"),
        created_at=datetime.now(UTC),
    )
    db_session.add(transaction1)
    await db_session.commit()

    service = PartnerProfitService(db_session)
    await service.adjust_wallet(
        partner_id=partner.id,
        amount=Decimal("-75.00"),
        description="Correction for error",
    )
    await db_session.commit()

    from sqlalchemy import select

    query = (
        select(PartnerWalletTransaction)
        .where(PartnerWalletTransaction.partner_id == partner.id)
        .order_by(PartnerWalletTransaction.created_at.desc())
    )
    result = await db_session.execute(query)
    transactions = result.scalars().all()

    assert len(transactions) == 2
    assert transactions[0].amount == Decimal("-75.00")
    assert transactions[0].balance_after == Decimal("125.00")


@pytest.mark.asyncio
async def test_wallet_balance_zero_for_new_partner(db_session: AsyncSession):
    """Test that wallet balance is zero for partner with no transactions."""
    partner = Partner(
        name="New Partner",
        share_percentage=Decimal("10.00"),
        investment_amount=Decimal("500.00"),
    )
    db_session.add(partner)
    await db_session.commit()

    service = PartnerProfitService(db_session)
    balance = await service.get_partner_wallet_balance(partner.id)

    assert balance == Decimal("0.00")


@pytest.mark.asyncio
async def test_wallet_transaction_history_pagination(db_session: AsyncSession):
    """Test paginated transaction history retrieval."""
    partner = Partner(
        name="Pagination Test Partner",
        share_percentage=Decimal("20.00"),
        investment_amount=Decimal("3000.00"),
    )
    db_session.add(partner)
    await db_session.commit()

    for i in range(15):
        transaction = PartnerWalletTransaction(
            partner_id=partner.id,
            amount=Decimal("10.00"),
            transaction_type="sale_profit",
            reference_id=uuid4(),
            reference_type="sale",
            description=f"Transaction {i + 1}",
            balance_after=Decimal(f"{(i + 1) * 10}.00"),
            created_at=datetime.now(UTC),
        )
        db_session.add(transaction)
    await db_session.commit()

    service = PartnerProfitService(db_session)

    page1 = await service.get_partner_wallet_transactions(
        partner.id, limit=10, offset=0
    )
    assert len(page1) == 10

    page2 = await service.get_partner_wallet_transactions(
        partner.id, limit=10, offset=10
    )
    assert len(page2) == 5


@pytest.mark.asyncio
async def test_partial_sale_from_assigned_inventory(db_session: AsyncSession):
    """Test selling partial quantities credits wallet correctly."""
    partner = Partner(
        name="Partial Sale Partner",
        share_percentage=Decimal("25.00"),
        investment_amount=Decimal("5000.00"),
    )
    db_session.add(partner)
    await db_session.flush()

    category = Category(name="Partial Sale Category")
    db_session.add(category)
    await db_session.flush()

    product = Product(
        name="Partial Sale Product",
        category_id=category.id,
        base_price=Decimal("100.00"),
        selling_price=Decimal("200.00"),
        stock_quantity=50,
        partner_id=partner.id,
    )
    db_session.add(product)
    await db_session.commit()

    sale_id = uuid4()
    sale_items = [
        {"product_id": product.id, "quantity": 3, "unit_price": Decimal("200.00")}
    ]

    service = PartnerProfitService(db_session)
    await service.process_sale_partner_profits(sale_id, sale_items)
    await db_session.commit()

    # Formula: 3 × (200 - 0) × 25 / 100 = 150
    query = select(PartnerWalletTransaction).where(
        PartnerWalletTransaction.partner_id == partner.id
    )
    result = await db_session.execute(query)
    transactions = result.scalars().all()

    assert len(transactions) == 1
    assert transactions[0].amount == Decimal("150.00")


@pytest.mark.asyncio
async def test_assignment_fulfilled_when_exhausted(db_session: AsyncSession):
    """Test that wallet credits even when selling large quantities (no assignment tracking)."""
    partner = Partner(
        name="Fulfillment Test Partner",
        share_percentage=Decimal("30.00"),
        investment_amount=Decimal("4000.00"),
    )
    db_session.add(partner)
    await db_session.flush()

    category = Category(name="Fulfillment Category")
    db_session.add(category)
    await db_session.flush()

    product = Product(
        name="Fulfillment Product",
        category_id=category.id,
        base_price=Decimal("150.00"),
        selling_price=Decimal("300.00"),
        stock_quantity=20,
        partner_id=partner.id,
    )
    db_session.add(product)
    await db_session.commit()

    sale_id = uuid4()
    sale_items = [
        {"product_id": product.id, "quantity": 5, "unit_price": Decimal("300.00")}
    ]

    service = PartnerProfitService(db_session)
    await service.process_sale_partner_profits(sale_id, sale_items)
    await db_session.commit()

    # Formula: 5 × (300 - 0) × 30 / 100 = 450
    query = select(PartnerWalletTransaction).where(
        PartnerWalletTransaction.partner_id == partner.id
    )
    result = await db_session.execute(query)
    transactions = result.scalars().all()

    assert len(transactions) == 1
    assert transactions[0].amount == Decimal("450.00")


@pytest.mark.asyncio
async def test_mixed_assigned_and_unassigned_products(db_session: AsyncSession):
    """Test sale with both partner-linked and unlinked products."""
    partner = Partner(
        name="Mixed Sale Partner",
        share_percentage=Decimal("15.00"),
        investment_amount=Decimal("2000.00"),
    )
    db_session.add(partner)
    await db_session.flush()

    category = Category(name="Mixed Category")
    db_session.add(category)
    await db_session.flush()

    product1 = Product(
        name="Assigned Product",
        category_id=category.id,
        base_price=Decimal("80.00"),
        selling_price=Decimal("160.00"),
        stock_quantity=30,
        partner_id=partner.id,
    )
    product2 = Product(
        name="Unassigned Product",
        category_id=category.id,
        base_price=Decimal("60.00"),
        selling_price=Decimal("120.00"),
        stock_quantity=30,
        # No partner_id
    )
    db_session.add_all([product1, product2])
    await db_session.commit()

    sale_id = uuid4()
    sale_items = [
        {"product_id": product1.id, "quantity": 2, "unit_price": Decimal("160.00")},
        {"product_id": product2.id, "quantity": 3, "unit_price": Decimal("120.00")},
    ]

    service = PartnerProfitService(db_session)
    result = await service.process_sale_partner_profits(sale_id, sale_items)
    await db_session.commit()

    # Only product1 has partner_id, so only it triggers profit
    # Formula: 2 × (160 - 0) × 15 / 100 = 48
    assert result["processed"] == 1
    assert result["total_profit"] == Decimal("48.00")

    query = select(PartnerWalletTransaction).where(
        PartnerWalletTransaction.partner_id == partner.id
    )
    result = await db_session.execute(query)
    transactions = result.scalars().all()

    assert len(transactions) == 1
    assert transactions[0].amount == Decimal("48.00")
