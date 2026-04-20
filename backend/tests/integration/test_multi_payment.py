"""
Integration tests for Multi-Payment support.
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
async def test_payment_methods(db_session: AsyncSession) -> list[PaymentMethod]:
    """Create test payment methods."""
    pm1 = PaymentMethod(name="Method 1", is_active=True)
    pm2 = PaymentMethod(name="Method 2", is_active=True)
    db_session.add(pm1)
    db_session.add(pm2)
    await db_session.commit()
    await db_session.refresh(pm1)
    await db_session.refresh(pm2)
    return [pm1, pm2]


@pytest.fixture
async def test_product(db_session: AsyncSession, test_category: Category) -> Product:
    """Create a test product."""
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


class TestMultiPayment:
    """Tests for split payment functionality."""

    @pytest.mark.asyncio
    async def test_create_sale_split_payment_success(
        self,
        client: AsyncClient,
        test_product: Product,
        test_payment_methods: list[PaymentMethod],
    ):
        """Test creating a sale with split payments."""
        pm1, pm2 = test_payment_methods
        
        # Total will be 150.00 * 2 = 300.00
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
                "payments": [
                    {
                        "payment_method_id": str(pm1.id),
                        "amount": 100.00,
                    },
                    {
                        "payment_method_id": str(pm2.id),
                        "amount": 200.00,
                    }
                ],
            },
        )

        assert sale_response.status_code == 201
        data = sale_response.json()
        assert len(data["payments"]) == 2
        assert data["grand_total"] == "300.00"
        
        # Verify payments
        amounts = [Decimal(p["amount"]) for p in data["payments"]]
        assert Decimal("100.00") in amounts
        assert Decimal("200.00") in amounts

    @pytest.mark.asyncio
    async def test_create_sale_mismatched_payment_fails(
        self,
        client: AsyncClient,
        test_product: Product,
        test_payment_methods: list[PaymentMethod],
    ):
        """Test that sale fails if payment sum != grand total."""
        pm1, pm2 = test_payment_methods
        
        # Total is 150.00
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
                "payments": [
                    {
                        "payment_method_id": str(pm1.id),
                        "amount": 100.00,
                    },
                    {
                        "payment_method_id": str(pm2.id),
                        "amount": 100.00,
                    }
                ],
            },
        )

        assert sale_response.status_code == 400
        data = sale_response.json()
        assert "does not match grand total" in data["detail"]["error"]["message"]

    @pytest.mark.asyncio
    async def test_create_sale_legacy_compatibility(
        self,
        client: AsyncClient,
        test_product: Product,
        test_payment_methods: list[PaymentMethod],
    ):
        """Test that sale still works with single payment_method_id."""
        pm1 = test_payment_methods[0]
        
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
                "payment_method_id": str(pm1.id),
            },
        )

        assert sale_response.status_code == 201
        data = sale_response.json()
        assert len(data["payments"]) == 1
        assert data["payments"][0]["payment_method_id"] == str(pm1.id)
        assert data["payments"][0]["amount"] == "150.00"
        assert data["payment_method_id"] == str(pm1.id)
