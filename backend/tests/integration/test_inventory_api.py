"""
Integration tests for Inventory API endpoints.

Tests cover:
- Restock with log creation - T105
- Adjustment with stock validation - T106
- Inventory log retrieval - T107
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from decimal import Decimal

from app.models.product import Product
from app.models.category import Category


@pytest.fixture
async def test_category(db_session: AsyncSession) -> Category:
    """Create a test category."""
    category = Category(name="Test Category")
    db_session.add(category)
    await db_session.commit()
    await db_session.refresh(category)
    return category


@pytest.fixture
async def test_product(db_session: AsyncSession, test_category: Category) -> Product:
    """Create a test product with initial stock."""
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


class TestRestock:
    """Tests for restock functionality (T105)."""

    @pytest.mark.asyncio
    async def test_restock_success(
        self, client: AsyncClient, test_product: Product, db_session: AsyncSession
    ):
        """Test successful restock with inventory log creation."""
        initial_stock = test_product.stock_quantity
        restock_quantity = 20

        response = await client.post(
            "/api/inventory/restock",
            json={
                "product_id": str(test_product.id),
                "quantity": restock_quantity,
            },
        )

        assert response.status_code == 201
        data = response.json()

        # Verify log entry
        assert "id" in data
        assert data["product_id"] == str(test_product.id)
        assert data["delta"] == restock_quantity
        assert data["reason"] == "restock"
        assert data["balance_after"] == initial_stock + restock_quantity

        # Verify stock updated in database
        await db_session.refresh(test_product)
        assert test_product.stock_quantity == initial_stock + restock_quantity

    @pytest.mark.asyncio
    async def test_restock_creates_inventory_log(
        self, client: AsyncClient, test_product: Product, db_session: AsyncSession
    ):
        """Test that restock creates an inventory log entry."""
        restock_quantity = 5

        response = await client.post(
            "/api/inventory/restock",
            json={
                "product_id": str(test_product.id),
                "quantity": restock_quantity,
            },
        )

        assert response.status_code == 201

        # Fetch inventory log
        log_response = await client.get(f"/api/inventory/log/{test_product.id}")
        assert log_response.status_code == 200

        logs = log_response.json()["items"]
        assert len(logs) > 0

        # Verify the latest log entry
        latest_log = logs[0]
        assert latest_log["delta"] == restock_quantity
        assert latest_log["reason"] == "restock"

    @pytest.mark.asyncio
    async def test_restock_invalid_product(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        """Test restock with non-existent product."""
        from uuid import uuid4

        fake_id = str(uuid4())

        response = await client.post(
            "/api/inventory/restock",
            json={
                "product_id": fake_id,
                "quantity": 10,
            },
        )

        assert response.status_code == 404
        data = response.json()
        assert data["detail"]["error"]["code"] == "NOT_FOUND"

    @pytest.mark.asyncio
    async def test_restock_negative_quantity(
        self, client: AsyncClient, test_product: Product
    ):
        """Test restock with negative quantity."""
        response = await client.post(
            "/api/inventory/restock",
            json={
                "product_id": str(test_product.id),
                "quantity": -5,
            },
        )

        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_restock_zero_quantity(
        self, client: AsyncClient, test_product: Product
    ):
        """Test restock with zero quantity."""
        response = await client.post(
            "/api/inventory/restock",
            json={
                "product_id": str(test_product.id),
                "quantity": 0,
            },
        )

        assert response.status_code == 422  # Validation error


class TestAdjustment:
    """Tests for stock adjustment functionality (T106)."""

    @pytest.mark.asyncio
    async def test_adjust_positive(
        self, client: AsyncClient, test_product: Product, db_session: AsyncSession
    ):
        """Test positive stock adjustment."""
        initial_stock = test_product.stock_quantity
        adjustment = 5

        response = await client.post(
            "/api/inventory/adjust",
            json={
                "product_id": str(test_product.id),
                "adjustment": adjustment,
                "reason": "Found additional stock",
            },
        )

        assert response.status_code == 201
        data = response.json()

        assert data["delta"] == adjustment
        assert data["reason"] == "adjustment"
        assert data["balance_after"] == initial_stock + adjustment

        # Verify database
        await db_session.refresh(test_product)
        assert test_product.stock_quantity == initial_stock + adjustment

    @pytest.mark.asyncio
    async def test_adjust_negative(
        self, client: AsyncClient, test_product: Product, db_session: AsyncSession
    ):
        """Test negative stock adjustment (reduction)."""
        initial_stock = test_product.stock_quantity
        adjustment = -3

        response = await client.post(
            "/api/inventory/adjust",
            json={
                "product_id": str(test_product.id),
                "adjustment": adjustment,
                "reason": "Damaged items",
            },
        )

        assert response.status_code == 201
        data = response.json()

        assert data["delta"] == adjustment
        assert data["balance_after"] == initial_stock + adjustment

        # Verify database
        await db_session.refresh(test_product)
        assert test_product.stock_quantity == initial_stock + adjustment

    @pytest.mark.asyncio
    async def test_adjust_would_make_stock_negative(
        self, client: AsyncClient, test_product: Product
    ):
        """Test adjustment that would make stock negative fails."""
        # Try to reduce stock below zero
        response = await client.post(
            "/api/inventory/adjust",
            json={
                "product_id": str(test_product.id),
                "adjustment": -100,  # More than available
                "reason": "Trying to reduce too much",
            },
        )

        assert response.status_code == 400
        data = response.json()
        assert data["detail"]["error"]["code"] == "INSUFFICIENT_STOCK"
        assert "negative" in data["detail"]["error"]["message"].lower()

    @pytest.mark.asyncio
    async def test_adjust_zero_stock(
        self, client: AsyncClient, test_product: Product, db_session: AsyncSession
    ):
        """Test adjustment to exactly zero stock."""
        initial_stock = test_product.stock_quantity

        response = await client.post(
            "/api/inventory/adjust",
            json={
                "product_id": str(test_product.id),
                "adjustment": -initial_stock,  # Reduce to zero
                "reason": "Complete stock depletion",
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["balance_after"] == 0

        # Verify database
        await db_session.refresh(test_product)
        assert test_product.stock_quantity == 0

    @pytest.mark.asyncio
    async def test_adjust_missing_reason(
        self, client: AsyncClient, test_product: Product
    ):
        """Test adjustment without reason fails."""
        response = await client.post(
            "/api/inventory/adjust",
            json={
                "product_id": str(test_product.id),
                "adjustment": 5,
                "reason": "",  # Empty reason
            },
        )

        assert response.status_code == 422  # Validation error


class TestInventoryLog:
    """Tests for inventory log retrieval (T107)."""

    @pytest.mark.asyncio
    async def test_get_inventory_log_empty(
        self, client: AsyncClient, test_product: Product
    ):
        """Test getting inventory log when no entries exist."""
        response = await client.get(f"/api/inventory/log/{test_product.id}")

        assert response.status_code == 200
        data = response.json()

        assert data["total"] == 0
        assert len(data["items"]) == 0

    @pytest.mark.asyncio
    async def test_get_inventory_log_with_entries(
        self, client: AsyncClient, test_product: Product
    ):
        """Test getting inventory log with multiple entries."""
        # Perform several stock operations
        await client.post(
            "/api/inventory/restock",
            json={"product_id": str(test_product.id), "quantity": 10},
        )

        await client.post(
            "/api/inventory/adjust",
            json={
                "product_id": str(test_product.id),
                "adjustment": -5,
                "reason": "Test adjustment 1",
            },
        )

        await client.post(
            "/api/inventory/restock",
            json={"product_id": str(test_product.id), "quantity": 3},
        )

        # Get log
        response = await client.get(f"/api/inventory/log/{test_product.id}")

        assert response.status_code == 200
        data = response.json()

        assert data["total"] == 3
        assert len(data["items"]) == 3

        # Verify chronological order (most recent first)
        assert data["items"][0]["delta"] == 3
        assert data["items"][1]["delta"] == -5
        assert data["items"][2]["delta"] == 10

    @pytest.mark.asyncio
    async def test_get_inventory_log_pagination(
        self, client: AsyncClient, test_product: Product
    ):
        """Test inventory log pagination."""
        # Create multiple log entries
        for i in range(25):
            await client.post(
                "/api/inventory/restock",
                json={"product_id": str(test_product.id), "quantity": 1},
            )

        # Get first page
        response1 = await client.get(
            f"/api/inventory/log/{test_product.id}?page=1&page_size=10"
        )

        assert response1.status_code == 200
        data1 = response1.json()

        assert data1["total"] == 25
        assert data1["page"] == 1
        assert data1["page_size"] == 10
        assert len(data1["items"]) == 10

        # Get second page
        response2 = await client.get(
            f"/api/inventory/log/{test_product.id}?page=2&page_size=10"
        )

        assert response2.status_code == 200
        data2 = response2.json()

        assert data2["page"] == 2
        assert len(data2["items"]) == 10

    @pytest.mark.asyncio
    async def test_get_inventory_log_nonexistent_product(self, client: AsyncClient):
        """Test getting inventory log for non-existent product."""
        from uuid import uuid4

        fake_id = str(uuid4())

        response = await client.get(f"/api/inventory/log/{fake_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert len(data["items"]) == 0

    @pytest.mark.asyncio
    async def test_log_entry_format(self, client: AsyncClient, test_product: Product):
        """Test that log entries have correct format."""
        # Perform restock
        await client.post(
            "/api/inventory/restock",
            json={"product_id": str(test_product.id), "quantity": 5},
        )

        # Get log
        response = await client.get(f"/api/inventory/log/{test_product.id}")

        assert response.status_code == 200
        data = response.json()
        log = data["items"][0]

        # Verify all fields present
        assert "id" in log
        assert "product_id" in log
        assert "delta" in log
        assert "reason" in log
        assert "reference_id" in log
        assert "balance_after" in log
        assert "created_at" in log

        # Verify types
        assert isinstance(log["delta"], int)
        assert isinstance(log["balance_after"], int)
        assert isinstance(log["reason"], str)


class TestLowStockProducts:
    """Tests for low stock products endpoint."""

    @pytest.mark.asyncio
    async def test_get_low_stock_products(
        self, client: AsyncClient, test_category: Category, db_session: AsyncSession
    ):
        """Test getting low stock products."""
        # Create products with different stock levels
        low_stock = Product(
            name="Low Stock",
            sku="LOW-001",
            category_id=test_category.id,
            base_price=Decimal("100.00"),
            selling_price=Decimal("150.00"),
            stock_quantity=5,
            is_active=True,
        )
        zero_stock = Product(
            name="Zero Stock",
            sku="ZERO-001",
            category_id=test_category.id,
            base_price=Decimal("100.00"),
            selling_price=Decimal("150.00"),
            stock_quantity=0,
            is_active=True,
        )
        high_stock = Product(
            name="High Stock",
            sku="HIGH-001",
            category_id=test_category.id,
            base_price=Decimal("100.00"),
            selling_price=Decimal("150.00"),
            stock_quantity=50,
            is_active=True,
        )

        db_session.add_all([low_stock, zero_stock, high_stock])
        await db_session.commit()

        # Get low stock (threshold 10)
        response = await client.get("/api/inventory/low-stock?threshold=10")

        assert response.status_code == 200
        data = response.json()

        # Should only return low and zero stock products
        stock_levels = [p["stock_quantity"] for p in data]
        assert all(stock <= 10 for stock in stock_levels)
        assert len(data) >= 2  # At least low_stock and zero_stock

    @pytest.mark.asyncio
    async def test_get_low_stock_with_custom_threshold(
        self, client: AsyncClient, test_category: Category, db_session: AsyncSession
    ):
        """Test low stock with custom threshold."""
        # Create product with stock of 15
        product = Product(
            name="Medium Stock",
            sku="MED-001",
            category_id=test_category.id,
            base_price=Decimal("100.00"),
            selling_price=Decimal("150.00"),
            stock_quantity=15,
            is_active=True,
        )

        db_session.add(product)
        await db_session.commit()

        # Get with threshold 20 (should include product with15)
        response = await client.get("/api/inventory/low-stock?threshold=20")

        assert response.status_code == 200
        data = response.json()

        # Should include products with stock <= 20
        stock_levels = [p["stock_quantity"] for p in data]
        assert all(stock <= 20 for stock in stock_levels)
