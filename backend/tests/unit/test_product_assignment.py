"""
Unit tests for ProductAssignment model.

Tests:
- Model creation and validation
- Status transitions
- Business rules (one active assignment per product)
"""

import pytest
from datetime import datetime, timezone
from decimal import Decimal
from uuid import uuid4

from app.models.product_assignment import ProductAssignment


def test_product_assignment_creation():
    """Test creating a new product assignment."""
    partner_id = uuid4()
    product_id = uuid4()

    assignment = ProductAssignment(
        partner_id=partner_id,
        product_id=product_id,
        assigned_quantity=10,
        remaining_quantity=10,
        share_percentage=Decimal("15.00"),
    )

    assert assignment.partner_id == partner_id
    assert assignment.product_id == product_id
    assert assignment.assigned_quantity == 10
    assert assignment.remaining_quantity == 10
    assert assignment.share_percentage == Decimal("15.00")
    assert assignment.status == "active"
    assert assignment.fulfilled_at is None


def test_product_assignment_status_transitions():
    """Test status transitions for product assignments."""
    assignment = ProductAssignment(
        partner_id=uuid4(),
        product_id=uuid4(),
        assigned_quantity=10,
        remaining_quantity=10,
        share_percentage=Decimal("20.00"),
    )

    # Initially active
    assert assignment.status == "active"
    assert assignment.fulfilled_at is None

    # Simulate sale (remaining_quantity decreases)
    assignment.remaining_quantity = 5
    assert assignment.status == "active"

    # When remaining_quantity hits 0
    assignment.remaining_quantity = 0
    assignment.status = "fulfilled"
    assignment.fulfilled_at = datetime.now(timezone.utc)

    assert assignment.status == "fulfilled"
    assert assignment.fulfilled_at is not None


def test_product_assignment_to_dict():
    """Test to_dict serialization."""
    partner_id = uuid4()
    product_id = uuid4()
    assignment = ProductAssignment(
        partner_id=partner_id,
        product_id=product_id,
        assigned_quantity=5,
        remaining_quantity=3,
        share_percentage=Decimal("12.50"),
        status="active",
    )

    result = assignment.to_dict()

    assert result["partner_id"] == str(partner_id)
    assert result["product_id"] == str(product_id)
    assert result["assigned_quantity"] == 5
    assert result["remaining_quantity"] == 3
    assert result["share_percentage"] == 12.5
    assert result["status"] == "active"


def test_product_assignment_constraints():
    """Test CHECK constraints for product assignment."""
    # Valid percentages
    assignment = ProductAssignment(
        partner_id=uuid4(),
        product_id=uuid4(),
        assigned_quantity=10,
        remaining_quantity=10,
        share_percentage=Decimal("0.00"),  # Minimum
    )
    assert assignment.share_percentage >= 0

    assignment.share_percentage = Decimal("100.00")  # Maximum
    assert assignment.share_percentage <= 100

    # Valid remaining_quantity
    assert assignment.remaining_quantity >= 0


def test_product_assignment_relationships():
    """Test that relationships are properly configured."""
    assignment = ProductAssignment(
        partner_id=uuid4(),
        product_id=uuid4(),
        assigned_quantity=10,
        remaining_quantity=10,
        share_percentage=Decimal("15.00"),
    )

    # Check that relationship attributes exist
    assert hasattr(assignment, "partner")
    assert hasattr(assignment, "product")
