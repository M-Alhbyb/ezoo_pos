"""
Integration tests for Product API endpoints.

Tests cover:
- POST /api/products (create product) - T047
- Product SKU uniqueness validation - T048
- Product soft delete behavior - T049
- Product search functionality - T050
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from decimal import Decimal
from uuid import uuid4

from app.models.product import Product
from app.models.category import Category


@pytest.fixture
async def test_category(db_session: AsyncSession) -> Category:
    """Create a test category for use in product tests."""
    category = Category(name="Test Category")
    db_session.add(category)
    await db_session.commit()
    await db_session.refresh(category)
    return category


@pytest.fixture
async def test_product(db_session: AsyncSession, test_category: Category) -> Product:
    """Create a test product for use in tests."""
    product = Product(
        name="Test Product",
        sku="TEST-001",
        category_id=test_category.id,
        base_price=Decimal("100.00"),
        selling_price=Decimal("150.00"),
        stock_quantity=50,
        is_active=True,
    )
    db_session.add(product)
    await db_session.commit()
    await db_session.refresh(product)
    return product


class TestCreateProduct:
    """Tests for POST /api/products endpoint (T047)."""

    @pytest.mark.asyncio
    async def test_create_product_success(
        self, client: AsyncClient, test_category: Category
    ):
        """Test successful product creation."""
        response = await client.post(
            "/api/products",
            json={
                "name": "Solar Panel X",
                "sku": "PNL-001",
                "category_id": str(test_category.id),
                "base_price": "200.00",
                "selling_price": "300.00",
                "stock_quantity": 100,
            },
        )

        assert response.status_code == 201
        data = response.json()

        assert data["name"] == "Solar Panel X"
        assert data["sku"] == "PNL-001"
        assert data["category_id"] == str(test_category.id)
        assert data["category_name"] == "Test Category"
        assert Decimal(data["base_price"]) == Decimal("200.00")
        assert Decimal(data["selling_price"]) == Decimal("300.00")
        assert data["stock_quantity"] == 100
        assert data["is_active"] is True
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data

    @pytest.mark.asyncio
    async def test_create_product_without_sku(
        self, client: AsyncClient, test_category: Category
    ):
        """Test product creation without SKU (SKU is optional)."""
        response = await client.post(
            "/api/products",
            json={
                "name": "Battery Pack Y",
                "category_id": str(test_category.id),
                "base_price": "50.00",
                "selling_price": "75.00",
                "stock_quantity": 20,
            },
        )

        assert response.status_code == 201
        data = response.json()

        assert data["name"] == "Battery Pack Y"
        assert data["sku"] is None
        assert data["stock_quantity"] == 20

    @pytest.mark.asyncio
    async def test_create_product_invalid_price_relationship(
        self, client: AsyncClient, test_category: Category
    ):
        """Test that selling_price must be >= base_price."""
        response = await client.post(
            "/api/products",
            json={
                "name": "Invalid Product",
                "sku": "INVALID-001",
                "category_id": str(test_category.id),
                "base_price": "200.00",
                "selling_price": "100.00",  # Less than base_price
                "stock_quantity": 10,
            },
        )

        assert response.status_code == 422  # Pydantic validation error

    @pytest.mark.asyncio
    async def test_create_product_missing_required_fields(
        self, client: AsyncClient, test_category: Category
    ):
        """Test product creation with missing required fields."""
        response = await client.post(
            "/api/products",
            json={
                "name": "Incomplete Product",
                # Missing category_id, base_price, selling_price
            },
        )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_product_nonexistent_category(self, client: AsyncClient):
        """Test product creation with non-existent category ID."""
        fake_category_id = str(uuid4())

        response = await client.post(
            "/api/products",
            json={
                "name": "Orphan Product",
                "sku": "ORPHAN-001",
                "category_id": fake_category_id,
                "base_price": "100.00",
                "selling_price": "150.00",
                "stock_quantity": 10,
            },
        )

        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"]["error"]["message"].lower()


class TestProductSKUUniqueness:
    """Tests for product SKU uniqueness validation (T048)."""

    @pytest.mark.asyncio
    async def test_create_product_duplicate_sku(
        self, client: AsyncClient, test_category: Category, test_product: Product
    ):
        """Test that duplicate SKU is rejected."""
        response = await client.post(
            "/api/products",
            json={
                "name": "Duplicate SKU Product",
                "sku": test_product.sku,  # Use existing SKU
                "category_id": str(test_category.id),
                "base_price": "100.00",
                "selling_price": "150.00",
                "stock_quantity": 10,
            },
        )

        assert response.status_code == 409  # Conflict
        data = response.json()
        assert data["detail"]["error"]["code"] == "CONFLICT"
        assert "already exists" in data["detail"]["error"]["message"].lower()

    @pytest.mark.asyncio
    async def test_update_product_with_duplicate_sku(
        self, client: AsyncClient, test_category: Category, db_session: AsyncSession
    ):
        """Test that updating a product to use another product's SKU fails."""
        # Create two products
        product1 = Product(
            name="Product 1",
            sku="PROD-001",
            category_id=test_category.id,
            base_price=Decimal("100.00"),
            selling_price=Decimal("150.00"),
            stock_quantity=10,
            is_active=True,
        )
        product2 = Product(
            name="Product 2",
            sku="PROD-002",
            category_id=test_category.id,
            base_price=Decimal("200.00"),
            selling_price=Decimal("250.00"),
            stock_quantity=20,
            is_active=True,
        )
        db_session.add_all([product1, product2])
        await db_session.commit()

        # Try to update product2 to use product1's SKU
        response = await client.put(
            f"/api/products/{product2.id}",
            json={"sku": "PROD-001"},  # Duplicate SKU
        )

        assert response.status_code == 409
        data = response.json()
        assert data["detail"]["error"]["code"] == "CONFLICT"

    @pytest.mark.asyncio
    async def test_update_product_same_sku_allowed(
        self, client: AsyncClient, test_product: Product
    ):
        """Test that updating a product with its own SKU is allowed."""
        response = await client.put(
            f"/api/products/{test_product.id}",
            json={
                "name": "Updated Name",
                "sku": test_product.sku,  # Same SKU
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Name"
        assert data["sku"] == test_product.sku


class TestProductSoftDelete:
    """Tests for product soft delete behavior (T049)."""

    @pytest.mark.asyncio
    async def test_soft_delete_product(
        self, client: AsyncClient, test_product: Product
    ):
        """Test that deleting a product sets is_active = False."""
        response = await client.delete(f"/api/products/{test_product.id}")

        assert response.status_code == 200
        data = response.json()
        assert "deactivated" in data["message"].lower()

        # Verify product is now inactive
        get_response = await client.get(f"/api/products/{test_product.id}")
        assert get_response.status_code == 200
        product_data = get_response.json()
        assert product_data["is_active"] is False

    @pytest.mark.asyncio
    async def test_soft_delete_nonexistent_product(self, client: AsyncClient):
        """Test deleting a non-existent product returns 404."""
        fake_id = str(uuid4())

        response = await client.delete(f"/api/products/{fake_id}")

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_list_products_excludes_inactive_by_default(
        self, client: AsyncClient, test_category: Category, db_session: AsyncSession
    ):
        """Test that inactive products are excluded from list by default."""
        # Create two products
        active_product = Product(
            name="Active Product",
            sku="ACTIVE-001",
            category_id=test_category.id,
            base_price=Decimal("100.00"),
            selling_price=Decimal("150.00"),
            stock_quantity=10,
            is_active=True,
        )
        inactive_product = Product(
            name="Inactive Product",
            sku="INACTIVE-001",
            category_id=test_category.id,
            base_price=Decimal("200.00"),
            selling_price=Decimal("250.00"),
            stock_quantity=5,
            is_active=False,
        )
        db_session.add_all([active_product, inactive_product])
        await db_session.commit()

        # List products (default: active_only=True)
        response = await client.get("/api/products")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert len(data["items"]) == 1
        assert data["items"][0]["name"] == "Active Product"

    @pytest.mark.asyncio
    async def test_list_products_includes_inactive_when_requested(
        self, client: AsyncClient, test_category: Category, db_session: AsyncSession
    ):
        """Test that inactive products are included when active_only=False."""
        # Create two products
        active_product = Product(
            name="Active Product 2",
            sku="ACTIVE-002",
            category_id=test_category.id,
            base_price=Decimal("100.00"),
            selling_price=Decimal("150.00"),
            stock_quantity=10,
            is_active=True,
        )
        inactive_product = Product(
            name="Inactive Product 2",
            sku="INACTIVE-002",
            category_id=test_category.id,
            base_price=Decimal("200.00"),
            selling_price=Decimal("250.00"),
            stock_quantity=5,
            is_active=False,
        )
        db_session.add_all([active_product, inactive_product])
        await db_session.commit()

        # List all products including inactive
        response = await client.get("/api/products?active_only=false")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        assert len(data["items"]) == 2


class TestProductSearch:
    """Tests for product search functionality (T050)."""

    @pytest.mark.asyncio
    async def test_search_by_name_partial_match(
        self, client: AsyncClient, test_category: Category, db_session: AsyncSession
    ):
        """Test searching products by name with partial match."""
        # Create products with different names
        products = [
            Product(
                name="Solar Panel Model X",
                sku=f"SPN-{i:03d}",
                category_id=test_category.id,
                base_price=Decimal("100.00"),
                selling_price=Decimal("150.00"),
                stock_quantity=10,
                is_active=True,
            )
            for i in range(3)
        ]
        # Add a product with different name
        products.append(
            Product(
                name="Battery Pack",
                sku="BAT-001",
                category_id=test_category.id,
                base_price=Decimal("200.00"),
                selling_price=Decimal("250.00"),
                stock_quantity=5,
                is_active=True,
            )
        )
        db_session.add_all(products)
        await db_session.commit()

        # Search for "Solar"
        response = await client.get("/api/products?search=Solar")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 3
        for item in data["items"]:
            assert "Solar" in item["name"]

    @pytest.mark.asyncio
    async def test_search_by_sku_exact_match(
        self, client: AsyncClient, test_category: Category, db_session: AsyncSession
    ):
        """Test searching products by SKU with exact match."""
        product = Product(
            name="Unique Product",
            sku="UNIQUE-SKU-123",
            category_id=test_category.id,
            base_price=Decimal("100.00"),
            selling_price=Decimal("150.00"),
            stock_quantity=10,
            is_active=True,
        )
        db_session.add(product)
        await db_session.commit()

        # Search by exact SKU
        response = await client.get(f"/api/products?search={product.sku}")

        assert response.status_code == 200
        data = response.json()
        # Should find the product with exact SKU match
        # (SKU is matched exactly, name is partial)
        assert any(item["sku"] == product.sku for item in data["items"])

    @pytest.mark.asyncio
    async def test_search_by_sku_endpoint(
        self, client: AsyncClient, test_category: Category, db_session: AsyncSession
    ):
        """Test the dedicated /api/products/search/by-sku endpoint."""
        product = Product(
            name="Special Product",
            sku="SPECIAL-001",
            category_id=test_category.id,
            base_price=Decimal("100.00"),
            selling_price=Decimal("150.00"),
            stock_quantity=10,
            is_active=True,
        )
        db_session.add(product)
        await db_session.commit()

        # Search by SKU using dedicated endpoint
        response = await client.get(f"/api/products/search/by-sku?sku={product.sku}")

        assert response.status_code == 200
        data = response.json()
        assert data["sku"] == product.sku
        assert data["name"] == "Special Product"

    @pytest.mark.asyncio
    async def test_search_by_sku_not_found(self, client: AsyncClient):
        """Test searching for non-existent SKU returns 404."""
        response = await client.get("/api/products/search/by-sku?sku=NONEXISTENT")

        assert response.status_code == 404
        data = response.json()
        assert data["detail"]["error"]["code"] == "NOT_FOUND"

    @pytest.mark.asyncio
    async def test_search_with_category_filter(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        """Test combining search with categoryfilter."""
        # Create two categories
        cat1 = Category(name="Category 1")
        cat2 = Category(name="Category 2")
        db_session.add_all([cat1, cat2])
        await db_session.commit()

        # Create products in different categories
        prod1 = Product(
            name="Product in Cat1",
            sku="CAT1-001",
            category_id=cat1.id,
            base_price=Decimal("100.00"),
            selling_price=Decimal("150.00"),
            stock_quantity=10,
            is_active=True,
        )
        prod2 = Product(
            name="Product in Cat2",
            sku="CAT2-001",
            category_id=cat2.id,
            base_price=Decimal("200.00"),
            selling_price=Decimal("250.00"),
            stock_quantity=5,
            is_active=True,
        )
        db_session.add_all([prod1, prod2])
        await db_session.commit()

        # Filter by category1
        response = await client.get(f"/api/products?category_id={cat1.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["category_id"] == str(cat1.id)

    @pytest.mark.asyncio
    async def test_search_pagination(
        self, client: AsyncClient, test_category: Category, db_session: AsyncSession
    ):
        """Test paginated search results."""
        # Create many products
        products = [
            Product(
                name=f"Product {i}",
                sku=f"PROD-{i:03d}",
                category_id=test_category.id,
                base_price=Decimal("100.00"),
                selling_price=Decimal("150.00"),
                stock_quantity=10,
                is_active=True,
            )
            for i in range(25)
        ]
        db_session.add_all(products)
        await db_session.commit()

        # Get first page
        response = await client.get("/api/products?page=1&page_size=10")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 25
        assert data["page"] == 1
        assert data["page_size"] == 10
        assert len(data["items"]) == 10

        # Get second page
        response = await client.get("/api/products?page=2&page_size=10")

        assert response.status_code == 200
        data = response.json()
        assert data["page"] == 2
        assert len(data["items"]) == 10


class TestProductUpdateAndGet:
    """Additional tests for product update and get operations."""

    @pytest.mark.asyncio
    async def test_get_product_by_id(
        self, client: AsyncClient, test_product: Product, test_category: Category
    ):
        """Test retrieving a product by ID."""
        response = await client.get(f"/api/products/{test_product.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(test_product.id)
        assert data["name"] == test_product.name
        assert data["category_name"] == test_category.name
        assert Decimal(data["base_price"]) == test_product.base_price

    @pytest.mark.asyncio
    async def test_get_product_not_found(self, client: AsyncClient):
        """Test retrieving a non-existent product."""
        fake_id = str(uuid4())
        response = await client.get(f"/api/products/{fake_id}")

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_update_product_all_fields(
        self, client: AsyncClient, test_product: Product, test_category: Category
    ):
        """Test updating all product fields."""
        response = await client.put(
            f"/api/products/{test_product.id}",
            json={
                "name": "Updated Product Name",
                "sku": "UPDATED-SKU",
                "base_price": "120.00",
                "selling_price": "180.00",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Product Name"
        assert data["sku"] == "UPDATED-SKU"
        assert Decimal(data["base_price"]) == Decimal("120.00")
        assert Decimal(data["selling_price"]) == Decimal("180.00")

    @pytest.mark.asyncio
    async def test_update_product_partial(
        self, client: AsyncClient, test_product: Product
    ):
        """Test updating only some product fields."""
        original_sku = test_product.sku
        response = await client.put(
            f"/api/products/{test_product.id}",
            json={"name": "New Name Only"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "New Name Only"
        assert data["sku"] == original_sku  # SKU unchanged
