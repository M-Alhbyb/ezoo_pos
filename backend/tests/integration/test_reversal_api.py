"""
Integration tests for Sale Reversal API endpoints.

Tests cover:
- Sale reversal with stock restoration - T091
- Double reversal prevention - T092
- Reversal record linking - T093
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from decimal import Decimal
from uuid import uuid4

from app.models.product import Product
from app.models.category import Category
from app.models.payment_method import PaymentMethod


@pytest.fixture
async def test_category(db_session: AsyncSession) -> Category:
    """Create a test category."""
    category = Category(name="Test Category")
    db_session.add(category)
    await db_session.commit()
    await db_session.refresh(category)
    return category


@pytest.fixture
async def test_payment_method(db_session: AsyncSession) -> PaymentMethod:
    """Create a test payment method."""
    pm = PaymentMethod(name="Cash", is_active=True)
    db_session.add(pm)
    await db_session.commit()
    await db_session.refresh(pm)
    return pm


@pytest.fixture
async def test_product(db_session: AsyncSession, test_category: Category) -> Product:
    """Create a test product with stock."""
    product = Product(
        name="Test Product",
        sku="TEST-001",
        category_id=test_category.id,
        base_price=Decimal("100.00"),
        selling_price=Decimal("150.00"),
        stock_quantity=10,
        is_active=True,
    )
    db_session.add(product)
    await db_session.commit()
    await db_session.refresh(product)
    return product


class TestSaleReversal:
    """Tests for sale reversal functionality (T091)."""

    @pytest.mark.asyncio
    async def test_reverse_sale_success(
        self,
        client: AsyncClient,
        test_product: Product,
        test_payment_method: PaymentMethod,
        db_session: AsyncSession,
    ):
        """Test successful sale reversal with stock restoration."""
        # Create a sale first
        initial_stock = test_product.stock_quantity

        sale_response = await client.post(
            "/api/sales",
            json={
                "items": [
                    {
                        "product_id": str(test_product.id),
                        "quantity": 2,
                    }
                ],
                "fees": [],
                "payment_method_id": str(test_payment_method.id),
            },
        )

        assert sale_response.status_code == 201
        sale_data = sale_response.json()
        sale_id = sale_data["id"]

        # Verify stock was deducted
        product_response = await client.get(f"/api/products/{test_product.id}")
        product_data = product_response.json()
        assert product_data["stock_quantity"] == initial_stock - 2

        # Reverse the sale
        reversal_response = await client.post(
            f"/api/sales/{sale_id}/reverse",
            json={"reason": "Customer returned items"},
        )

        assert reversal_response.status_code == 200
        reversal_data = reversal_response.json()

        assert reversal_data["original_sale_id"] == sale_id
        assert reversal_data["reason"] == "Customer returned items"
        assert "id" in reversal_data
        assert "created_at" in reversal_data

        # Verify stock was restored
        product_response = await client.get(f"/api/products/{test_product.id}")
        product_data = product_response.json()
        assert product_data["stock_quantity"] == initial_stock

    @pytest.mark.asyncio
    async def test_reverse_sale_stock_restoration(
        self,
        client: AsyncClient,
        test_product: Product,
        test_payment_method: PaymentMethod,
        db_session: AsyncSession,
    ):
        """Test that stock is fully restored after reversal."""
        initial_stock = test_product.stock_quantity

        # Create sale with multiple items
        sale_response = await client.post(
            "/api/sales",
            json={
                "items": [
                    {
                        "product_id": str(test_product.id),
                        "quantity": 5,
                    }
                ],
                "fees": [],
                "payment_method_id": str(test_payment_method.id),
            },
        )

        assert sale_response.status_code == 201
        sale_id = sale_response.json()["id"]

        # Check stock after sale
        product_response = await client.get(f"/api/products/{test_product.id}")
        assert product_response.json()["stock_quantity"] == initial_stock - 5

        # Reverse sale
        reversal_response = await client.post(
            f"/api/sales/{sale_id}/reverse",
            json={"reason": "Test reversal"},
        )

        assert reversal_response.status_code == 200

        # Verify stock restored
        product_response = await client.get(f"/api/products/{test_product.id}")
        assert product_response.json()["stock_quantity"] == initial_stock

    @pytest.mark.asyncio
    async def test_reverse_nonexistent_sale(
        self,
        client: AsyncClient,
    ):
        """Test reversing a non-existent sale."""
        fake_id = str(uuid4())

        reversal_response = await client.post(
            f"/api/sales/{fake_id}/reverse",
            json={"reason": "Test"},
        )

        assert reversal_response.status_code == 404
        data = reversal_response.json()
        assert data["detail"]["error"]["code"] == "NOT_FOUND"


class TestDoubleReversalPrevention:
    """Tests for double reversal prevention (T092)."""

    @pytest.mark.asyncio
    async def test_prevent_double_reversal(
        self,
        client: AsyncClient,
        test_product: Product,
        test_payment_method: PaymentMethod,
        db_session: AsyncSession,
    ):
        """Test that a sale cannot be reversed twice."""
        # Create a sale
        sale_response = await client.post(
            "/api/sales",
            json={
                "items": [
                    {
                        "product_id": str(test_product.id),
                        "quantity": 1,
                    }
                ],
                "fees": [],
                "payment_method_id": str(test_payment_method.id),
            },
        )

        assert sale_response.status_code == 201
        sale_id = sale_response.json()["id"]

        # First reversal - should succeed
        first_reversal = await client.post(
            f"/api/sales/{sale_id}/reverse",
            json={"reason": "First reversal"},
        )

        assert first_reversal.status_code == 200

        # Second reversal attempt - should fail
        second_reversal = await client.post(
            f"/api/sales/{sale_id}/reverse",
            json={"reason": "Second reversal"},
        )

        assert second_reversal.status_code == 400
        data = second_reversal.json()
        assert data["detail"]["error"]["code"] == "ALREADY_REVERSED"
        assert "already reversed" in data["detail"]["error"]["message"].lower()

    @pytest.mark.asyncio
    async def test_stock_not_double_restored(
        self,
        client: AsyncClient,
        test_product: Product,
        test_payment_method: PaymentMethod,
        db_session: AsyncSession,
    ):
        """Test that stock is not restored twice when attempting double reversal."""
        initial_stock = test_product.stock_quantity

        # Create sale
        sale_response = await client.post(
            "/api/sales",
            json={
                "items": [
                    {
                        "product_id": str(test_product.id),
                        "quantity": 3,
                    }
                ],
                "fees": [],
                "payment_method_id": str(test_payment_method.id),
            },
        )

        sale_id = sale_response.json()["id"]

        # Reverse once
        await client.post(
            f"/api/sales/{sale_id}/reverse",
            json={"reason": "First reversal"},
        )

        # Check stock after first reversal
        product_response = await client.get(f"/api/products/{test_product.id}")
        stock_after_reversal = product_response.json()["stock_quantity"]
        assert stock_after_reversal == initial_stock

        # Try to reverse again
        await client.post(
            f"/api/sales/{sale_id}/reverse",
            json={"reason": "Second reversal"},
        )

        # Verify stock is same as after first reversal
        product_response = await client.get(f"/api/products/{test_product.id}")
        assert product_response.json()["stock_quantity"] == stock_after_reversal


class TestReversalRecordLinking:
    """Tests for reversal record linking (T093)."""

    @pytest.mark.asyncio
    async def test_reversal_record_links_to_original_sale(
        self,
        client: AsyncClient,
        test_product: Product,
        test_payment_method: PaymentMethod,
        db_session: AsyncSession,
    ):
        """Test that reversal record correctly links to original sale."""
        # Create sale
        sale_response = await client.post(
            "/api/sales",
            json={
                "items": [
                    {
                        "product_id": str(test_product.id),
                        "quantity": 1,
                    }
                ],
                "fees": [],
                "payment_method_id": str(test_payment_method.id),
            },
        )

        sale_id = sale_response.json()["id"]

        # Reverse sale
        reversal_response = await client.post(
            f"/api/sales/{sale_id}/reverse",
            json={"reason": "Test reversal"},
        )

        assert reversal_response.status_code == 200
        reversal_data = reversal_response.json()

        # Verify reversal record fields
        assert "id" in reversal_data
        assert reversal_data["original_sale_id"] == sale_id
        assert reversal_data["reason"] == "Test reversal"
        assert "created_at" in reversal_data

        # Verify reversal ID is a valid UUID
        from uuid import UUID

        try:
            UUID(reversal_data["id"])
        except ValueError:
            pytest.fail("Reversal ID is not a valid UUID")

    @pytest.mark.asyncio
    async def test_reversal_persists_reason(
        self,
        client: AsyncClient,
        test_product: Product,
        test_payment_method: PaymentMethod,
        db_session: AsyncSession,
    ):
        """Test that reversal reason is properly stored."""
        # Create sale
        sale_response = await client.post(
            "/api/sales",
            json={
                "items": [
                    {
                        "product_id": str(test_product.id),
                        "quantity": 1,
                    }
                ],
                "fees": [],
                "payment_method_id": str(test_payment_method.id),
            },
        )

        sale_id = sale_response.json()["id"]

        # Reverse with detailed reason
        detailed_reason = (
            "Customer returned items due to defect. Refund approved by manager."
        )
        reversal_response = await client.post(
            f"/api/sales/{sale_id}/reverse",
            json={"reason": detailed_reason},
        )

        assert reversal_response.status_code == 200
        data = reversal_response.json()

        assert data["reason"] == detailed_reason

    @pytest.mark.asyncio
    async def test_reversal_without_reason_fails(
        self,
        client: AsyncClient,
        test_product: Product,
        test_payment_method: PaymentMethod,
        db_session: AsyncSession,
    ):
        """Test that reversal requires a reason."""
        # Create sale
        sale_response = await client.post(
            "/api/sales",
            json={
                "items": [
                    {
                        "product_id": str(test_product.id),
                        "quantity": 1,
                    }
                ],
                "fees": [],
                "payment_method_id": str(test_payment_method.id),
            },
        )

        sale_id = sale_response.json()["id"]

        # Try to reverse without reason
        reversal_response = await client.post(
            f"/api/sales/{sale_id}/reverse",
            json={"reason": ""},
        )

        assert reversal_response.status_code == 422  # Validation error
