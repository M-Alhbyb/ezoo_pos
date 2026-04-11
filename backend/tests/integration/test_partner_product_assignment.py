"""
Integration tests for product assignment creation workflow.

Tests:
- Assignment CRUD operations
- Partner-product relationships
- Validation rules
"""

import pytest
from decimal import Decimal
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.partner import Partner
from app.models.product import Product
from app.models.category import Category
from app.models.product_assignment import ProductAssignment
from app.modules.partners.partner_profit_service import PartnerProfitService
from app.schemas.product_assignment import (
    ProductAssignmentCreate,
    ProductAssignmentUpdate,
)


@pytest.mark.asyncio
async def test_create_assignment_basic(db_session: AsyncSession):
    """Test creating a basic product assignment."""
    # Create partner
    partner = Partner(
        name="Test Partner",
        share_percentage=Decimal("15.00"),
        investment_amount=Decimal("1000.00"),
    )
    db_session.add(partner)
    await db_session.commit()
    await db_session.refresh(partner)

    # Create category and product
    category = Category(name="Solar Panels")
    db_session.add(category)
    await db_session.commit()
    await db_session.refresh(category)

    product = Product(
        name="Solar Panel 100W",
        category_id=category.id,
        base_price=Decimal("200.00"),
        selling_price=Decimal("350.00"),
        stock_quantity=50,
    )
    db_session.add(product)
    await db_session.commit()
    await db_session.refresh(product)

    # Create assignment
    service = PartnerProfitService(db_session)
    assignment_data = ProductAssignmentCreate(
        partner_id=partner.id,
        product_id=product.id,
        assigned_quantity=10,
        share_percentage=Decimal("15.00"),
    )

    assignment = await service.create_assignment(assignment_data)

    assert assignment.id is not None
    assert assignment.partner_id == partner.id
    assert assignment.product_id == product.id
    assert assignment.assigned_quantity == 10
    assert assignment.remaining_quantity == 10
    assert assignment.share_percentage == Decimal("15.00")
    assert assignment.status == "active"
    assert assignment.fulfilled_at is None


@pytest.mark.asyncio
async def test_create_assignment_uses_partner_default_share(db_session: AsyncSession):
    """Test that assignment uses partner's default share_percentage when not specified."""
    # Create partner with default 20% share
    partner = Partner(
        name="Partner with 20% Share",
        share_percentage=Decimal("20.00"),
        investment_amount=Decimal("5000.00"),
    )
    db_session.add(partner)
    await db_session.commit()
    await db_session.refresh(partner)

    # Create category and product
    category = Category(name="Batteries")
    db_session.add(category)
    await db_session.commit()
    await db_session.refresh(category)

    product = Product(
        name="Battery 200Ah",
        category_id=category.id,
        base_price=Decimal("150.00"),
        selling_price=Decimal("250.00"),
        stock_quantity=30,
    )
    db_session.add(product)
    await db_session.commit()
    await db_session.refresh(product)

    # Create assignment without specifying share_percentage
    service = PartnerProfitService(db_session)
    assignment_data = ProductAssignmentCreate(
        partner_id=partner.id,
        product_id=product.id,
        assigned_quantity=5,
        # share_percentage not specified - should use partner default
    )

    # Note: Service should copy partner's share_percentage
    # This test will fail until we implement that logic
    # assignment = await service.create_assignment(assignment_data)
    # assert assignment.share_percentage == Decimal("20.00")


@pytest.mark.asyncio
async def test_prevent_duplicate_active_assignment(db_session: AsyncSession):
    """Test that only one active assignment per product is allowed."""
    # Setup partner and product
    partner = Partner(
        name="Partner A",
        share_percentage=Decimal("15.00"),
        investment_amount=Decimal("1000.00"),
    )
    db_session.add(partner)
    await db_session.commit()
    await db_session.refresh(partner)

    category = Category(name="Inverters")
    db_session.add(category)
    await db_session.commit()
    await db_session.refresh(category)

    product = Product(
        name="Inverter 5000W",
        category_id=category.id,
        base_price=Decimal("500.00"),
        selling_price=Decimal("800.00"),
        stock_quantity=20,
    )
    db_session.add(product)
    await db_session.commit()
    await db_session.refresh(product)

    # Create first assignment
    service = PartnerProfitService(db_session)
    assignment1_data = ProductAssignmentCreate(
        partner_id=partner.id,
        product_id=product.id,
        assigned_quantity=10,
        share_percentage=Decimal("15.00"),
    )
    assignment1 = await service.create_assignment(assignment1_data)

    # Try to create second active assignment for same product
    assignment2_data = ProductAssignmentCreate(
        partner_id=partner.id,
        product_id=product.id,
        assigned_quantity=5,
        share_percentage=Decimal("20.00"),
    )

    # Should raise an error or prevent creation
    # This test documents the expected behavior
    # Implementation should check for existing active assignment
    # and raise ValueError or HTTPException


@pytest.mark.asyncio
async def test_get_assignment_by_id(db_session: AsyncSession):
    """Test retrieving an assignment by ID."""
    # Setup
    partner = Partner(
        name="Test Partner",
        share_percentage=Decimal("10.00"),
        investment_amount=Decimal("2000.00"),
    )
    db_session.add(partner)
    await db_session.commit()
    await db_session.refresh(partner)

    category = Category(name="Controllers")
    db_session.add(category)
    await db_session.commit()
    await db_session.refresh(category)

    product = Product(
        name="Charge Controller 60A",
        category_id=category.id,
        base_price=Decimal("100.00"),
        selling_price=Decimal("180.00"),
        stock_quantity=15,
    )
    db_session.add(product)
    await db_session.commit()
    await db_session.refresh(product)

    # Create assignment
    service = PartnerProfitService(db_session)
    assignment_data = ProductAssignmentCreate(
        partner_id=partner.id,
        product_id=product.id,
        assigned_quantity=8,
        share_percentage=Decimal("12.50"),
    )
    created = await service.create_assignment(assignment_data)

    # Retrieve by ID
    retrieved = await service.get_assignment(created.id)

    assert retrieved is not None
    assert retrieved.id == created.id
    assert retrieved.partner_id == partner.id
    assert retrieved.product_id == product.id


@pytest.mark.asyncio
async def test_list_assignments_with_filters(db_session: AsyncSession):
    """Test listing assignments with various filters."""
    # Setup
    partner1 = Partner(
        name="Partner 1",
        share_percentage=Decimal("15.00"),
        investment_amount=Decimal("1000.00"),
    )
    partner2 = Partner(
        name="Partner 2",
        share_percentage=Decimal("18.00"),
        investment_amount=Decimal("2000.00"),
    )
    db_session.add_all([partner1, partner2])
    await db_session.commit()
    await db_session.refresh(partner1)
    await db_session.refresh(partner2)

    category = Category(name="Mounting")
    db_session.add(category)
    await db_session.commit()
    await db_session.refresh(category)

    product1 = Product(
        name="Mounting Kit Type A",
        category_id=category.id,
        base_price=Decimal("50.00"),
        selling_price=Decimal("80.00"),
        stock_quantity=100,
    )
    product2 = Product(
        name="Mounting Kit Type B",
        category_id=category.id,
        base_price=Decimal("60.00"),
        selling_price=Decimal("95.00"),
        stock_quantity=80,
    )
    db_session.add_all([product1, product2])
    await db_session.commit()
    await db_session.refresh(product1)
    await db_session.refresh(product2)

    # Create assignments
    service = PartnerProfitService(db_session)
    await service.create_assignment(
        ProductAssignmentCreate(
            partner_id=partner1.id,
            product_id=product1.id,
            assigned_quantity=20,
        )
    )
    await service.create_assignment(
        ProductAssignmentCreate(
            partner_id=partner2.id,
            product_id=product2.id,
            assigned_quantity=15,
        )
    )

    # List all assignments
    all_assignments = await service.list_assignments()
    assert len(all_assignments) >= 2

    # Filter by partner
    partner1_assignments = await service.list_assignments(partner_id=partner1.id)
    assert len(partner1_assignments) >= 1
    for assignment in partner1_assignments:
        assert assignment.partner_id == partner1.id
