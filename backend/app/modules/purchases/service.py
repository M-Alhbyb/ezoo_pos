from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.product import Product
from app.models.supplier import Supplier
from app.models.purchase import Purchase
from app.models.purchase_item import PurchaseItem
from app.models.supplier_ledger import SupplierLedger
from app.models.inventory_log import InventoryLog
from app.schemas.purchase import PurchaseCreate
from app.websocket.manager import manager


class PurchaseService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.manager = manager

    async def create_purchase(self, data: PurchaseCreate) -> Purchase:
        supplier = await self.db.get(Supplier, data.supplier_id)
        if not supplier:
            raise ValueError(f"Supplier {data.supplier_id} not found")

        if not data.items:
            raise ValueError("At least one item is required")

        total_amount = Decimal(0)
        purchase_items = []

        for item in data.items:
            product = await self.db.get(Product, item.product_id)
            if not product:
                raise ValueError(f"Product {item.product_id} not found")

            total_cost = item.quantity * item.unit_cost
            total_amount += total_cost

            purchase_items.append(
                {
                    "product_id": item.product_id,
                    "quantity": item.quantity,
                    "unit_cost": item.unit_cost,
                    "selling_price": item.selling_price,
                    "total_cost": total_cost,
                }
            )

        purchase = Purchase(
            supplier_id=data.supplier_id,
            total_amount=total_amount,
        )
        self.db.add(purchase)
        await self.db.flush()

        for item_data in purchase_items:
            purchase_item = PurchaseItem(
                purchase_id=purchase.id,
                product_id=item_data["product_id"],
                quantity=item_data["quantity"],
                unit_cost=item_data["unit_cost"],
                total_cost=item_data["total_cost"],
            )
            self.db.add(purchase_item)

            product = await self.db.get(Product, item_data["product_id"])
            product.stock_quantity += item_data["quantity"]
            product.base_price = item_data["unit_cost"]
            
            # Update selling price if provided
            if item_data.get("selling_price"):
                product.selling_price = item_data["selling_price"]
            
            # Ensure selling price is never below cost (database constraint)
            if product.selling_price < product.base_price:
                product.selling_price = product.base_price

            balance_after = product.stock_quantity

            log = InventoryLog(
                product_id=item_data["product_id"],
                delta=item_data["quantity"],
                reason="PURCHASE",
                reference_id=purchase.id,
                balance_after=balance_after,
            )
            self.db.add(log)

            await self.manager.broadcast(
                {
                    "event": "stock_updated",
                    "data": {
                        "product_id": str(item_data["product_id"]),
                        "stock_quantity": balance_after,
                    },
                }
            )

        ledger = SupplierLedger(
            supplier_id=data.supplier_id,
            type="PURCHASE",
            amount=total_amount,
            reference_id=purchase.id,
        )
        self.db.add(ledger)

        await self.db.commit()
        await self.db.refresh(purchase)

        return purchase

    async def get_purchases(
        self,
        supplier_id: Optional[UUID] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Purchase]:
        query = select(Purchase).order_by(Purchase.created_at.desc())

        if supplier_id:
            query = query.where(Purchase.supplier_id == supplier_id)

        query = query.offset(offset).limit(limit)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_purchase(self, purchase_id: UUID) -> Optional[Purchase]:
        query = (
            select(Purchase)
            .options(selectinload(Purchase.items).joinedload(PurchaseItem.product))
            .where(Purchase.id == purchase_id)
        )
        result = await self.db.execute(query)
        return result.unique().scalars().first()

    async def get_purchase_items(self, purchase_id: UUID) -> List[PurchaseItem]:
        query = (
            select(PurchaseItem)
            .options(joinedload(PurchaseItem.product))
            .where(PurchaseItem.purchase_id == purchase_id)
        )
        result = await self.db.execute(query)
        return list(result.unique().scalars().all())

    async def return_items(
        self,
        purchase_id: UUID,
        items: List[dict],
        note: Optional[str] = None,
    ) -> tuple[Purchase, List[PurchaseItem]]:
        purchase = await self.get_purchase(purchase_id)
        if not purchase:
            raise ValueError(f"Purchase {purchase_id} not found")

        existing_items = await self.get_purchase_items(purchase_id)
        existing_by_product = {item.product_id: item for item in existing_items}

        total_returned = Decimal(0)
        return_items_list = []

        for item in items:
            product_id = item["product_id"]
            quantity = item["quantity"]

            if product_id not in existing_by_product:
                raise ValueError(f"Product {product_id} was not in this purchase")

            original = existing_by_product[product_id]

            if quantity > original.quantity:
                raise ValueError(
                    f"Cannot return {quantity} of product {product_id}, "
                    f"only {original.quantity} were purchased"
                )

            quantity_returned = original.quantity - quantity
            if quantity_returned > 0:
                original.quantity = quantity
                original.total_cost = quantity * original.unit_cost

            return_amount = quantity * original.unit_cost
            total_returned += return_amount

            return_items_list.append(
                {
                    "product_id": product_id,
                    "quantity": quantity,
                    "unit_cost": original.unit_cost,
                    "total_cost": return_amount,
                    "product_name": original.product_name,
                    "product_sku": original.product_sku,
                    "current_stock": original.current_stock,
                }
            )

            product = await self.db.get(Product, product_id)
            if product.stock_quantity < quantity:
                raise ValueError(
                    f"Insufficient stock to return for product {product_id}. "
                    f"Available: {product.stock_quantity}, Requested: {quantity}"
                )

            product.stock_quantity -= quantity
            balance_after = product.stock_quantity

            log = InventoryLog(
                product_id=product_id,
                delta=-quantity,
                reason="RETURN",
                reference_id=purchase_id,
                balance_after=balance_after,
            )
            self.db.add(log)

            await self.manager.broadcast(
                {
                    "event": "stock_updated",
                    "data": {
                        "product_id": str(product_id),
                        "stock_quantity": balance_after,
                    },
                }
            )

        if total_returned > 0:
            ledger = SupplierLedger(
                supplier_id=purchase.supplier_id,
                type="RETURN",
                amount=total_returned,
                reference_id=purchase_id,
                note=note,
            )
            self.db.add(ledger)

        await self.db.commit()

        return purchase, return_items_list
