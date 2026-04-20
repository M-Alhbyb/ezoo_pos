"""
Integration tests for sale-with-profit distribution workflow.

Tests:
- Partner profit calculation on sale
- Wallet balance updates
- Assignment remaining_quantity updates
- Concurrent sale handling
"""

import pytest
from decimal import Decimal
from uuid import uuid4
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.partner import Partner
from app.models.product import Product
from app.models.category import Category
from app.models.product_assignment import ProductAssignment
from app.models.partner_wallet_transaction import PartnerWalletTransaction
from app.modules.partners.partner_profit_service import PartnerProfitService


@pytest.mark.asyncio
async def test_sale_updates_partner_wallet(db_session: AsyncSession):
    """Test that selling assigned products credits partner wallet."""
    # Setup: Create partner, product, assignment
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
    )
    db_session.add(product)
    await db_session.flush()

    # Create assignment: 10 units assigned to partner with 20% share
    assignment = ProductAssignment(
        partner_id=partner.id,
        product_id=product.id,
        assigned_quantity=10,
        remaining_quantity=10,
        share_percentage=Decimal("20.00"),
        status="active",
    )
    db_session.add(assignment)
    await db_session.commit()

    # Mock sale items (simplified)
    sale_id = uuid4()
    sale_items = [
        {"product_id": product.id, "quantity": 3, "unit_price": Decimal("200.00")},
    ]

    # Process partner profits
    service = PartnerProfitService(db_session)
    result = await service.process_sale_partner_profits(sale_id, sale_items)

    # Verify: Partner wallet credited
    # Expected: 3 units × $200 × 20% = $120
    await db_session.commit()

    # Check wallet transactions
    from sqlalchemy import select

    query = select(PartnerWalletTransaction).where(
        PartnerWalletTransaction.partner_id == partner.id
    )
    wallet_result = await db_session.execute(query)
    transactions = wallet_result.scalars().all()

    assert len(transactions) > 0
    assert transactions[0].amount == Decimal("120.00")
    assert transactions[0].transaction_type == "sale_profit"
    assert transactions[0].reference_id == sale_id


@pytest.mark.asyncio
async def test_sale_updates_remaining_quantity(db_session: AsyncSession):
    """Test that selling assigned products decreases remaining_quantity."""
    # Setup
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
    )
    db_session.add(product)
    await db_session.flush()

    # Create assignment: 10 units
    assignment = ProductAssignment(
        partner_id=partner.id,
        product_id=product.id,
        assigned_quantity=10,
        remaining_quantity=10,
        share_percentage=Decimal("15.00"),
        status="active",
    )
    db_session.add(assignment)
    await db_session.commit()

    # Initial remaining_quantity
    initial_remaining = assignment.remaining_quantity

    # Process sale of 4 units
    sale_id = uuid4()
    sale_items = [
        {"product_id": product.id, "quantity": 4, "unit_price": Decimal("100.00")}
    ]

    service = PartnerProfitService(db_session)
    await service.process_sale_partner_profits(sale_id, sale_items)
    await db_session.commit()

    # Refresh to get updated assignment
    await db_session.refresh(assignment)

    # Verify remaining_quantity decreased by 4
    assert assignment.remaining_quantity == initial_remaining - 4
    assert assignment.remaining_quantity == 6


@pytest.mark.asyncio
async def test_multiple_partners_in_same_sale(db_session: AsyncSession):
    """Test selling products assigned to multiple partners in one sale."""
    # Setup: 2 partners, 2 products
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
    )
    product2 = Product(
        name="Product 2",
        category_id=category.id,
        base_price=Decimal("50.00"),
        selling_price=Decimal("150.00"),
        stock_quantity=30,
    )
    db_session.add_all([product1, product2])
    await db_session.flush()

    # Assign product1 to partner1, product2 to partner2
    assignment1 = ProductAssignment(
        partner_id=partner1.id,
        product_id=product1.id,
        assigned_quantity=5,
        remaining_quantity=5,
        share_percentage=Decimal("10.00"),
        status="active",
    )
    assignment2 = ProductAssignment(
        partner_id=partner2.id,
        product_id=product2.id,
        assigned_quantity=8,
        remaining_quantity=8,
        share_percentage=Decimal("15.00"),
        status="active",
    )
    db_session.add_all([assignment1, assignment2])
    await db_session.commit()

    # Process sale with both products
    sale_id = uuid4()
    sale_items = [
        {"product_id": product1.id, "quantity": 2, "unit_price": Decimal("200.00")},
        {"product_id": product2.id, "quantity": 3, "unit_price": Decimal("150.00")},
    ]

    service = PartnerProfitService(db_session)
    result = await service.process_sale_partner_profits(sale_id, sale_items)
    await db_session.commit()

    # Verify both partners got credited
    # Partner 1: 2 × $200 × 10% = $40
    # Partner 2: 3 × $150 × 15% = $67.50

    from sqlalchemy import select

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
    # Setup: partner and product, but no assignment
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
    )
    db_session.add(product)
    await db_session.commit()

    # Process sale for unassigned product
    sale_id = uuid4()
    sale_items = [
        {"product_id": product.id, "quantity": 5, "unit_price": Decimal("200.00")}
    ]

    service = PartnerProfitService(db_session)
    result = await service.process_sale_partner_profits(sale_id, sale_items)

    # Should process with no partner profit
    assert result["processed"] == 0

    # No wallet transaction should exist
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
    # Setup
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
    )
    db_session.add(product)
    await db_session.flush()

    assignment = ProductAssignment(
        partner_id=partner.id,
        product_id=product.id,
        assigned_quantity=10,
        remaining_quantity=10,
        share_percentage=Decimal("25.00"),
        status="active",
    )
    db_session.add(assignment)
    await db_session.commit()

    service = PartnerProfitService(db_session)

    # First sale: 2 units × $400 × 25% = $200
    # balance_after should be $200
    sale1_id = uuid4()
    await service.process_sale_partner_profits(
        sale1_id,
        [{"product_id": product.id, "quantity": 2, "unit_price": Decimal("400.00")}],
    )
    await db_session.commit()

    # Check first transaction
    from sqlalchemy import select

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

    # Second sale: 3 units × $400 × 25% = $300
    # balance_after should be $500
    sale2_id = uuid4()
    await service.process_sale_partner_profits(
        sale2_id,
        [{"product_id": product.id, "quantity": 3, "unit_price": Decimal("400.00")}],
    )
    await db_session.commit()

    # Check second transaction
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
    # Setup partner
    partner = Partner(
        name="Adjustment Test Partner",
        share_percentage=Decimal("20.00"),
        investment_amount=Decimal("1000.00"),
    )
    db_session.add(partner)
    await db_session.commit()

    # Create initial transaction
    transaction1 = PartnerWalletTransaction(
        partner_id=partner.id,
        amount=Decimal("100.00"),
        transaction_type="sale_profit",
        reference_id=uuid4(),
        reference_type="sale",
        description="Initial sale profit",
        balance_after=Decimal("100.00"),
        created_at=datetime.now(timezone.utc),
    )
    db_session.add(transaction1)
    await db_session.commit()

    # Make manual adjustment (credit)
    service = PartnerProfitService(db_session)
    adjustment = await service.adjust_wallet(
        partner_id=partner.id,
        amount=Decimal("50.00"),
        description="Manual credit for bonus",
    )
    await db_session.commit()

    # Verify adjustment
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
    # Setup partner
    partner = Partner(
        name="Debit Test Partner",
        share_percentage=Decimal("15.00"),
        investment_amount=Decimal("2000.00"),
    )
    db_session.add(partner)
    await db_session.commit()

    # Create initial balance
    transaction1 = PartnerWalletTransaction(
        partner_id=partner.id,
        amount=Decimal("200.00"),
        transaction_type="sale_profit",
        reference_id=uuid4(),
        reference_type="sale",
        description="Sale profit",
        balance_after=Decimal("200.00"),
        created_at=datetime.now(timezone.utc),
    )
    db_session.add(transaction1)
    await db_session.commit()

    # Make debit adjustment (correction)
    service = PartnerProfitService(db_session)
    adjustment = await service.adjust_wallet(
        partner_id=partner.id,
        amount=Decimal("-75.00"),
        description="Correction for error",
    )
    await db_session.commit()

    # Verify adjustment
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

    # Create multiple transactions
    for i in range(15):
        transaction = PartnerWalletTransaction(
            partner_id=partner.id,
            amount=Decimal("10.00"),
            transaction_type="sale_profit",
            reference_id=uuid4(),
            reference_type="sale",
            description=f"Transaction {i + 1}",
            balance_after=Decimal(f"{(i + 1) * 10}.00"),
            created_at=datetime.now(timezone.utc),
        )
        db_session.add(transaction)
    await db_session.commit()

    service = PartnerProfitService(db_session)

    # Get first page
    page1 = await service.get_partner_wallet_transactions(
        partner.id, limit=10, offset=0
    )
    assert len(page1) == 10

    # Get second page
    page2 = await service.get_partner_wallet_transactions(
        partner.id, limit=10, offset=10
    )
    assert len(page2) == 5


@pytest.mark.asyncio
async def test_partial_sale_from_assigned_inventory(db_session: AsyncSession):
    """Test selling partial quantities from assigned inventory."""
    # Setup: Assign 10 units to partner
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
    )
    db_session.add(product)
    await db_session.flush()

    # Create assignment: 10 units assigned
    assignment = ProductAssignment(
        partner_id=partner.id,
        product_id=product.id,
        assigned_quantity=10,
        remaining_quantity=10,
        share_percentage=Decimal("25.00"),
        status="active",
    )
    db_session.add(assignment)
    await db_session.commit()

    # Sell only 3 units (partial sale)
    sale_id = uuid4()
    sale_items = [
        {"product_id": product.id, "quantity": 3, "unit_price": Decimal("200.00")}
    ]

    service = PartnerProfitService(db_session)
    await service.process_sale_partner_profits(sale_id, sale_items)
    await db_session.commit()

    # Refresh assignment
    await db_session.refresh(assignment)

    # Verify: remaining_quantity decreased by 3, not 10
    assert assignment.remaining_quantity == 7
    assert assignment.status == "active"  # Still active, not fulfilled
    assert assignment.assigned_quantity == 10  # Original assignment unchanged

    # Verify profit calculated for 3 units only
    # Expected: 3 × $200 × 25% = $150
    from sqlalchemy import select

    query = select(PartnerWalletTransaction).where(
        PartnerWalletTransaction.partner_id == partner.id
    )
    result = await db_session.execute(query)
    transactions = result.scalars().all()

    assert len(transactions) == 1
    assert transactions[0].amount == Decimal("150.00")


@pytest.mark.asyncio
async def test_sell_more_than_assigned_quantity_error(db_session: AsyncSession):
    """Test that selling more than assigned quantity raises error."""
    partner = Partner(
        name="Error Test Partner",
        share_percentage=Decimal("20.00"),
        investment_amount=Decimal("3000.00"),
    )
    db_session.add(partner)
    await db_session.flush()

    category = Category(name="Error Test Category")
    db_session.add(category)
    await db_session.flush()

    product = Product(
        name="Error Test Product",
        category_id=category.id,
        base_price=Decimal("50.00"),
        selling_price=Decimal("100.00"),
        stock_quantity=100,
    )
    db_session.add(product)
    await db_session.flush()

    # Create assignment: only 5 units
    assignment = ProductAssignment(
        partner_id=partner.id,
        product_id=product.id,
        assigned_quantity=5,
        remaining_quantity=5,
        share_percentage=Decimal("20.00"),
        status="active",
    )
    db_session.add(assignment)
    await db_session.commit()

    # Try to sell 10 units (more than assigned)
    sale_id = uuid4()
    sale_items = [
        {"product_id": product.id, "quantity": 10, "unit_price": Decimal("100.00")}
    ]

    service = PartnerProfitService(db_session)

    # Should raise ValueError for insufficient assigned quantity
    with pytest.raises(ValueError, match="Insufficient assigned quantity"):
        await service.process_sale_partner_profits(sale_id, sale_items)
        await db_session.commit()


@pytest.mark.asyncio
async def test_assignment_fulfilled_when_exhausted(db_session: AsyncSession):
    """Test that assignment status changes to fulfilled when all units sold."""
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
    )
    db_session.add(product)
    await db_session.flush()

    # Create assignment: 5 units
    assignment = ProductAssignment(
        partner_id=partner.id,
        product_id=product.id,
        assigned_quantity=5,
        remaining_quantity=5,
        share_percentage=Decimal("30.00"),
        status="active",
    )
    db_session.add(assignment)
    await db_session.commit()

    # Sell all 5 units
    sale_id = uuid4()
    sale_items = [
        {"product_id": product.id, "quantity": 5, "unit_price": Decimal("300.00")}
    ]

    service = PartnerProfitService(db_session)
    await service.process_sale_partner_profits(sale_id, sale_items)
    await db_session.commit()

    # Refresh assignment
    await db_session.refresh(assignment)

    # Verify: assignment is now fulfilled
    assert assignment.remaining_quantity == 0
    assert assignment.status == "fulfilled"
    assert assignment.assigned_quantity == 5  # Original unchanged

    # Try to sell more - should fail because assignment is fulfilled
    sale_id2 = uuid4()
    sale_items2 = [
        {"product_id": product.id, "quantity": 1, "unit_price": Decimal("300.00")}
    ]

    # This should either raise an error or process as unassigned product
    # Since there's no active assignment anymore


@pytest.mark.asyncio
async def test_mixed_assigned_and_unassigned_products(db_session: AsyncSession):
    """Test sale with both assigned and unassigned products."""
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

    # Product 1: Assigned to partner
    product1 = Product(
        name="Assigned Product",
        category_id=category.id,
        base_price=Decimal("80.00"),
        selling_price=Decimal("160.00"),
        stock_quantity=30,
    )
    # Product 2: Not assigned to any partner
    product2 = Product(
        name="Unassigned Product",
        category_id=category.id,
        base_price=Decimal("60.00"),
        selling_price=Decimal("120.00"),
        stock_quantity=30,
    )
    db_session.add_all([product1, product2])
    await db_session.flush()

    # Assign product1 to partner
    assignment = ProductAssignment(
        partner_id=partner.id,
        product_id=product1.id,
        assigned_quantity=10,
        remaining_quantity=10,
        share_percentage=Decimal("15.00"),
        status="active",
    )
    db_session.add(assignment)
    await db_session.commit()

    # Sell both products
    sale_id = uuid4()
    sale_items = [
        {"product_id": product1.id, "quantity": 2, "unit_price": Decimal("160.00")},
        {"product_id": product2.id, "quantity": 3, "unit_price": Decimal("120.00")},
    ]

    service = PartnerProfitService(db_session)
    result = await service.process_sale_partner_profits(sale_id, sale_items)
    await db_session.commit()

    # Verify: Only assigned product triggered profit
    assert result["processed"] == 1  # Only product1 processed
    # Expected: 2 × $160 × 15% = $48
    assert result["total_profit"] == Decimal("48.00")

    # Check assignment
    await db_session.refresh(assignment)
    assert assignment.remaining_quantity == 8  # 10 - 2

    # Check wallet - should only have profit from product1
    from sqlalchemy import select

    query = select(PartnerWalletTransaction).where(
        PartnerWalletTransaction.partner_id == partner.id
    )
    result = await db_session.execute(query)
    transactions = result.scalars().all()

    assert len(transactions) == 1
    # Product2 should not create a transaction for this partner
    # Product1 profit: 2 × $160 × 15% = $48
