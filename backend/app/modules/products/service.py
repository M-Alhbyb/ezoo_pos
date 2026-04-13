"""
Product Service - Business logic for product catalog management.

Implements Constitution principles:
- VI (Data Integrity): Decimal for all monetary values
- VII (Backend Authority): All validation in backend
- IX (Extensibility): user_id, branch_id support
"""

from decimal import Decimal
from typing import Optional, Tuple
from uuid import UUID
from datetime import datetime

from sqlalchemy import select, func, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.product import Product
from app.models.category import Category
from app.schemas.product import (
    ProductCreate,
    ProductUpdate,
    ProductResponse,
    ProductListResponse,
)
from app.core.calculations import Decimal


class ProductService:
    """Service class for product CRUD operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_product(self, product_data: ProductCreate) -> Product:
        """
        Create a new product with validation.
        """
        if product_data.sku:
            existing = await self._get_by_sku(product_data.sku)
            if existing:
                raise ValueError(
                    f"Product with SKU '{product_data.sku}' already exists"
                )

        category_id = product_data.category_id
        if not category_id:
            cat_query = select(Category).limit(1)
            cat_result = await self.db.execute(cat_query)
            category = cat_result.scalars().first()
            if not category:
                category = Category(name="Uncategorized")
                self.db.add(category)
                await self.db.flush()
            category_id = category.id
        else:
            category = await self._get_category(category_id)
            if not category:
                raise ValueError(f"Category {category_id} not found")

        product = Product(
            name=product_data.name,
            sku=product_data.sku,
            category_id=category_id,
            base_price=product_data.base_price,
            selling_price=product_data.selling_price,
            stock_quantity=product_data.stock_quantity,
            partner_id=product_data.partner_id,
            is_active=True,
        )

        self.db.add(product)
        await self.db.commit()
        await self.db.refresh(product)

        return await self.get_product(product.id)

    async def list_products(
        self,
        category_id: Optional[UUID] = None,
        partner_id: Optional[UUID] = None,
        search: Optional[str] = None,
        active_only: bool = True,
        page: int = 1,
        page_size: int = 50,
    ) -> Tuple[list[Product], int]:
        """
        List products with optional filters and pagination.

        Args:
            category_id: Filter by category
            search: Search by name (partial) or SKU (exact)
            active_only: Only return active products
            page: Page number (1-indexed)
            page_size: Items per page (max100)

        Returns:
            Tuple of (products list, total count)
        """
        page_size = min(page_size, 100)

        query = (
            select(Product)
            .options(
                selectinload(Product.category),
                selectinload(Product.partner)
            )
            .order_by(Product.created_at.desc())
        )

        if active_only:
            query = query.where(Product.is_active == True)

        if category_id:
            query = query.where(Product.category_id == category_id)

        if partner_id:
            query = query.where(Product.partner_id == partner_id)

        if search:
            search_term = f"%{search}%"
            query = query.where(
                or_(
                    Product.name.ilike(search_term),
                    Product.sku == search,
                )
            )

        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()

        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)

        result = await self.db.execute(query)
        products = result.scalars().all()

        return list(products), total

    async def get_product(self, product_id: UUID) -> Optional[Product]:
        """
        Get a single product by ID.

        Args:
            product_id: Product UUID

        Returns:
            Product instance or None
        """
        query = (
            select(Product)
            .options(
                selectinload(Product.category),
                selectinload(Product.partner)
            )
            .where(Product.id == product_id)
        )

        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def update_product(
        self, product_id: UUID, product_data: ProductUpdate
    ) -> Optional[Product]:
        """
        Update product details.

        Cannot update stock_quantity directly (use inventory endpoints).

        Args:
            product_id: Product UUID
            product_data: ProductUpdate schema with fields to update

        Returns:
            Updated Product instance or None if not found

        Raises:
            ValueError: If SKU already exists or validation fails
        """
        product = await self.get_product(product_id)
        if not product:
            return None

        update_data = product_data.model_dump(exclude_unset=True)

        if "sku" in update_data and update_data["sku"] != product.sku:
            if update_data["sku"]:
                existing = await self._get_by_sku(update_data["sku"])
                if existing and existing.id != product_id:
                    raise ValueError(
                        f"Product with SKU '{update_data['sku']}' already exists"
                    )

        if "category_id" in update_data:
            category = await self._get_category(update_data["category_id"])
            if not category:
                raise ValueError(f"Category {update_data['category_id']} not found")

        if "base_price" in update_data or "selling_price" in update_data:
            base_price = update_data.get("base_price", product.base_price)
            selling_price = update_data.get("selling_price", product.selling_price)
            if selling_price < base_price:
                raise ValueError(
                    "selling_price must be greater than or equal to base_price"
                )

        for field, value in update_data.items():
            setattr(product, field, value)

        await self.db.commit()
        await self.db.refresh(product)

        return await self.get_product(product_id)

    async def soft_delete_product(self, product_id: UUID) -> bool:
        """
        Soft delete a product (set is_active = False).

        Products referenced in sales cannot be hard deleted,
        so we always soft delete for consistency.

        Args:
            product_id: Product UUID

        Returns:
            True if deleted, False if not found
        """
        product = await self.get_product(product_id)
        if not product:
            return False

        product.is_active = False
        await self.db.commit()

        return True

    async def get_by_sku(self, sku: str) -> Optional[Product]:
        """
        Get product by SKU for barcode scanning.

        Args:
            sku: SKU string

        Returns:
            Product instance or None
        """
        return await self._get_by_sku(sku)

    async def _get_by_sku(self, sku: str) -> Optional[Product]:
        """Internal method to get product by SKU."""
        if not sku:
            return None

        query = (
            select(Product)
            .options(selectinload(Product.category))
            .where(Product.sku == sku)
        )

        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def _get_category(self, category_id: UUID) -> Optional[Category]:
        """Get category by ID."""
        query = select(Category).where(Category.id == category_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    def _prepare_response(self, product: Product) -> dict:
        """
        Prepare product response with category_name.

        Args:
            product: Product instance

        Returns:
            Dictionary ready for response
        """
        return {
            "id": str(product.id),
            "name": product.name,
            "sku": product.sku,
            "category_id": str(product.category_id),
            "category_name": product.category.name if product.category else None,
            "category_color": product.category.color if product.category else None,
            "base_price": str(product.base_price),
            "selling_price": str(product.selling_price),
            "stock_quantity": product.stock_quantity,
            "partner_id": str(product.partner_id) if product.partner_id else None,
            "partner_name": product.partner.name if product.partner else None,
            "is_active": product.is_active,
            "created_at": product.created_at.isoformat(),
            "updated_at": product.updated_at.isoformat(),
        }
