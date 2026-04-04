"""
Inventory Service - Business logic for inventory management.

Implements inventory tracking and stock updates.
"""

from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.product import Product
from app.models.inventory_log import InventoryLog
from app.websocket.manager import manager


class InventoryService:
    """Service class for inventory operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

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

    async def emit_stock_update(self, product_id: UUID, new_quantity: int) -> None:
        """
        Emit real-time stock update via WebSocket.

        Args:
            product_id: Product UUID
            new_quantity: New stock quantity
        """
        # Broadcast to all connected clients
        await manager.broadcast(
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
