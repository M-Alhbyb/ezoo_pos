"""
Inventory Service - Business logic for inventory management.

Implements inventory tracking and stock updates.
"""

from typing import Optional, List, Tuple
from uuid import UUID
from datetime import datetime

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.product import Product
from app.models.inventory_log import InventoryLog
from app.websocket.manager import manager


class InventoryService:
    """Service class for inventory operations."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.manager = manager

    async def deduct_stock(
        self,
        product_id: UUID,
        quantity: int,
        reason: str,
        reference_id: Optional[UUID] = None,
    ) -> InventoryLog:
        """
        Deduct stock for a product and create inventory log entry.

        Must be called within a transaction.

        Args:
            product_id: Product UUID
            quantity: Quantity to deduct
            reason: Reason for deduction ('sale', 'reversal', 'adjustment')
            reference_id: Reference to sale or reversal

        Returns:
            InventoryLog instance

        Raises:
            ValueError: If insufficient stock or invalid product
        """
        # Lock product row for update
        product = await self._get_product_for_update(product_id)

        if not product:
            raise ValueError(f"Product {product_id} not found")

        if product.stock_quantity < quantity:
            raise ValueError(
                f"Insufficient stock for {product.name}: "
                f"requested {quantity}, available {product.stock_quantity}"
            )

        # Deduct stock
        product.stock_quantity -= quantity
        balance_after = product.stock_quantity

        # Create inventory log
        log = InventoryLog(
            product_id=product_id,
            delta=-quantity,  # Negative for deduction
            reason=reason,
            reference_id=reference_id,
            balance_after=balance_after,
        )

        self.db.add(log)

        # Emit WebSocket update
        await self.emit_stock_update(product_id, balance_after)

        return log

    async def restore_stock(
        self,
        product_id: UUID,
        quantity: int,
        reason: str,
        reference_id: Optional[UUID] = None,
    ) -> InventoryLog:
        """
        Restore stock for a product (e.g., for reversals) and create inventory log.

        Must be called within a transaction.

        Args:
            product_id: Product UUID
            quantity: Quantity to restore
            reason: Reason for restoration ('reversal', 'restock')
            reference_id: Reference to reversal

        Returns:
            InventoryLog instance

        Raises:
            ValueError: If invalid product
        """
        # Lock product row for update
        product = await self._get_product_for_update(product_id)

        if not product:
            raise ValueError(f"Product {product_id} not found")

        # Restore stock
        product.stock_quantity += quantity
        balance_after = product.stock_quantity

        # Create inventory log
        log = InventoryLog(
            product_id=product_id,
            delta=quantity,  # Positive for restoration
            reason=reason,
            reference_id=reference_id,
            balance_after=balance_after,
        )

        self.db.add(log)

        # Emit WebSocket update
        await self.emit_stock_update(product_id, balance_after)

        return log

    async def restock_product(
        self,
        product_id: UUID,
        quantity: int,
        user_id: Optional[UUID] = None,
    ) -> InventoryLog:
        """
        Restock product with inventory log.

        Args:
            product_id: Product UUID
            quantity: Quantity to add
            user_id: User performing restock (for audit)

        Returns:
            InventoryLog instance

        Raises:
            ValueError: If invalid product or quantity
        """
        if quantity <= 0:
            raise ValueError("Quantity must be positive")

        # Lock product row for update
        product = await self._get_product_for_update(product_id)

        if not product:
            raise ValueError(f"Product {product_id} not found")

        # Update stock
        product.stock_quantity += quantity
        balance_after = product.stock_quantity

        # Create inventory log
        log = InventoryLog(
            product_id=product_id,
            delta=quantity,
            reason="restock",
            balance_after=balance_after,
        )

        if user_id:
            log.user_id = user_id

        self.db.add(log)
        await self.db.commit()
        await self.db.refresh(log)

        # Emit WebSocket update
        await self.emit_stock_update(product_id, balance_after)

        return log

    async def adjust_stock(
        self,
        product_id: UUID,
        adjustment: int,
        reason: str,
        user_id: Optional[UUID] = None,
    ) -> InventoryLog:
        """
        Adjust stock (positive or negative) with validation.

        Args:
            product_id: Product UUID
            adjustment: Stock adjustment (+/-)
            reason: Reason for adjustment
            user_id: User performing adjustment (for audit)

        Returns:
            InventoryLog instance

        Raises:
            ValueError: If invalid product or adjustment would make stock negative
        """
        # Lock product row for update
        product = await self._get_product_for_update(product_id)

        if not product:
            raise ValueError(f"Product {product_id} not found")

        new_balance = product.stock_quantity + adjustment

        if new_balance < 0:
            raise ValueError(
                f"Adjustment would make stock negative: "
                f"current {product.stock_quantity}, adjustment {adjustment}"
            )

        # Update stock
        product.stock_quantity = new_balance

        # Create inventory log
        log = InventoryLog(
            product_id=product_id,
            delta=adjustment,
            reason="adjustment",
            balance_after=new_balance,
        )

        if user_id:
            log.user_id = user_id

        self.db.add(log)
        await self.db.commit()
        await self.db.refresh(log)

        # Emit WebSocket update
        await self.emit_stock_update(product_id, new_balance)

        return log

    async def get_inventory_log(
        self,
        product_id: UUID,
        page: int = 1,
        page_size: int = 50,
    ) -> Tuple[List[InventoryLog], int]:
        """
        Get inventory log for a product with pagination.

        Args:
            product_id: Product UUID
            page: Page number (1-indexed)
            page_size: Items per page (max100)

        Returns:
            Tuple of (logs list, total count)
        """
        page_size = min(page_size, 100)

        # Count total logs
        count_query = select(InventoryLog).where(InventoryLog.product_id == product_id)
        total_result = await self.db.execute(count_query)
        total = len(total_result.all())

        # Get paginated logs
        offset = (page - 1) * page_size
        query = (
            select(InventoryLog)
            .where(InventoryLog.product_id == product_id)
            .order_by(InventoryLog.created_at.desc())
            .offset(offset)
            .limit(page_size)
        )

        result = await self.db.execute(query)
        logs = result.scalars().all()

        return list(logs), total

    async def get_low_stock_products(
        self,
        threshold: int = 10,
    ) -> List[Product]:
        """
        Get products with stock below threshold.

        Args:
            threshold: Stock level threshold (default10)

        Returns:
            List of low-stock products
        """
        query = (
            select(Product)
            .where(
                and_(
                    Product.is_active == True,
                    Product.stock_quantity <= threshold,
                )
            )
            .order_by(Product.stock_quantity.asc())
        )

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def emit_stock_update(self, product_id: UUID, new_quantity: int) -> None:
        """
        Emit real-time stock update via WebSocket.

        Args:
            product_id: Product UUID
            new_quantity: New stock quantity
        """
        # Broadcast to all connected clients
        await self.manager.broadcast(
            {
                "event": "stock_updated",
                "data": {"product_id": str(product_id), "stock_quantity": new_quantity},
            }
        )

    async def _get_product_for_update(self, product_id: UUID) -> Optional[Product]:
        """Get product with row lock for update."""
        query = (
            select(Product)
            .where(Product.id == product_id)
            .with_for_update()  # Row-level lock
        )

        result = await self.db.execute(query)
        return result.scalar_one_or_none()
