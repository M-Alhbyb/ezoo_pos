"""
Category Service - Business logic for category management.

Implements Constitution principles:
- VI (Data Integrity): Foreign key constraint protection
- VII (Backend Authority): All validation in backend
"""

from typing import Optional, List
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.category import Category
from app.models.product import Product
from app.schemas.category import CategoryCreate, CategoryUpdate


class CategoryService:
    """Service class for category CRUD operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_category(self, category_data: CategoryCreate) -> Category:
        """
        Create a new category.

        Args:
            category_data: CategoryCreate schema with validated fields

        Returns:
            Created Category instance

        Raises:
            ValueError: If category name already exists
        """
        existing = await self._get_by_name(category_data.name)
        if existing:
            raise ValueError(f"Category '{category_data.name}' already exists")

        category = Category(name=category_data.name)

        self.db.add(category)
        await self.db.commit()
        await self.db.refresh(category)

        return category

    async def list_categories(self) -> List[tuple[Category, int]]:
        """
        List all categories with product counts.

        Returns:
            List of tuples: (Category instance, product_count)
        """
        query = (
            select(
                Category,
                func.count(Product.id)
                .filter(Product.is_active == True)
                .label("product_count"),
            )
            .outerjoin(Product, Category.id == Product.category_id)
            .group_by(Category.id)
            .order_by(Category.name)
        )

        result = await self.db.execute(query)
        return result.all()

    async def get_category(self, category_id: UUID) -> Optional[Category]:
        """
        Get a single category by ID.

        Args:
            category_id: Category UUID

        Returns:
            Category instance or None
        """
        query = select(Category).where(Category.id == category_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def update_category(
        self, category_id: UUID, category_data: CategoryUpdate
    ) -> Optional[Category]:
        """
        Update category name.

        Args:
            category_id: Category UUID
            category_data: CategoryUpdate schema with name to update

        Returns:
            Updated Category instance or None if not found

        Raises:
            ValueError: If new name already exists
        """
        category = await self.get_category(category_id)
        if not category:
            return None

        if category_data.name and category_data.name != category.name:
            existing = await self._get_by_name(category_data.name)
            if existing:
                raise ValueError(f"Category '{category_data.name}' already exists")

        category.name = category_data.name
        await self.db.commit()
        await self.db.refresh(category)

        return category

    async def delete_category(self, category_id: UUID) -> bool:
        """
        Delete a category.

        Only allowed if no active products reference it.

        Args:
            category_id: Category UUID

        Returns:
            True if deleted, False if not found

        Raises:
            ValueError: If category has active products
        """
        category = await self.get_category(category_id)
        if not category:
            return False

        product_count = await self._count_active_products(category_id)
        if product_count > 0:
            raise ValueError(
                f"Cannot delete category with {product_count} active products"
            )

        await self.db.delete(category)
        await self.db.commit()

        return True

    async def _get_by_name(self, name: str) -> Optional[Category]:
        """Get category by name."""
        query = select(Category).where(Category.name == name)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def _count_active_products(self, category_id: UUID) -> int:
        """Count active products in a category."""
        query = (
            select(func.count())
            .select_from(Product)
            .where(Product.category_id == category_id, Product.is_active == True)
        )
        result = await self.db.execute(query)
        return result.scalar()
