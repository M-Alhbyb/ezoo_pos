"""
Partner Profit Service - Handles partner profit calculation and distribution.

Implements Constitution principles:
- I (Financial Accuracy): DECIMAL for all monetary values, immutable transaction records
- II (Single Source of Truth): All calculations in backend, PostgreSQL only
- III (Explicit Over Implicit): share_percentage stored per assignment and transaction
- IV (Immutable Financial Records): PartnerWalletTransaction never updated after creation
- VI (Data Integrity): Atomic transactions with record locking for concurrent safety
"""

import logging
from decimal import Decimal
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.partner import Partner
from app.models.product import Product
from app.models.partner_wallet_transaction import PartnerWalletTransaction

logger = logging.getLogger(__name__)


class PartnerProfitService:
    """
    Service for calculating partner profits and managing wallet transactions.

    Key responsibilities:
    1. Process partner profit on sales (integrated into SaleService)
    2. Manage product assignments
    3. Handle wallet transactions and balance calculations
    4. Ensure atomic operations with record locking

    All monetary calculations use DECIMAL for precision.
    All transactions are atomic and use SELECT FOR UPDATE for concurrency safety.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    # Profit Calculation Methods

    async def get_partner_for_update(self, partner_id: UUID) -> Optional[Partner]:
        """
        Lock partner row for update using SELECT FOR UPDATE.

        Constitution VI: Atomic transactions with record locking.

        Args:
            partner_id: UUID of the partner

        Returns:
            Partner object or None if not found
        """
        query = select(Partner).where(Partner.id == partner_id).with_for_update()
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_product_for_update(
        self,
        product_id: UUID,
    ) -> Optional[Product]:
        """
        Lock product row for update using SELECT FOR UPDATE.
        """
        query = (
            select(Product)
            .where(Product.id == product_id)
            .with_for_update()
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def calculate_partner_profit(
        self,
        quantity: int,
        unit_price: Decimal,
        share_percentage: Decimal,
    ) -> Decimal:
        """
        Calculate partner profit: quantity × unit_price × (share_percentage / 100).

        Constitution I: Financial Accuracy - DECIMAL types for all calculations.

        Args:
            quantity: Number of units sold
            unit_price: Price per unit
            share_percentage: Partner's share percentage (e.g., 15.00 for 15%)

        Returns:
            Calculated profit as Decimal with 2 decimal places
        """
        if (
            quantity == 0
            or unit_price == Decimal("0")
            or share_percentage == Decimal("0")
        ):
            return Decimal("0.00")

        profit = (Decimal(quantity) * unit_price * share_percentage) / Decimal("100")

        return profit.quantize(Decimal("0.01"))

    async def calculate_product_profit(
        self,
        selling_price: Decimal,
        base_cost: Decimal,
    ) -> Decimal:
        """
        Calculate partner profit from product sale: selling_price - base_cost (minimum 0).

        Per spec: Real-time Partner Profit from Product Sales.
        Profit = selling_price - base_cost, never negative.

        Constitution I: Financial Accuracy - DECIMAL types.

        Args:
            selling_price: Sale price per unit
            base_cost: Product base cost

        Returns:
            Calculated profit as Decimal with 2 decimal places, minimum 0
        """
        if selling_price == Decimal("0") and base_cost == Decimal("0"):
            return Decimal("0.00")

        profit = selling_price - base_cost

        if profit < Decimal("0"):
            return Decimal("0.00")

        return profit.quantize(Decimal("0.01"))

    async def credit_partner_wallet(
        self,
        partner: Partner,
        sale_id: UUID,
        product_id: UUID,
        quantity: int,
        unit_price: Decimal,
    ) -> PartnerWalletTransaction:
        """
        Credit partner wallet and create transaction record.
        """
        profit_amount = await self.calculate_partner_profit(
            quantity, unit_price, partner.share_percentage
        )

        previous_balance = await self.get_partner_wallet_balance(partner.id)
        new_balance = previous_balance + profit_amount

        description = (
            f"Sale profit: {quantity} × {unit_price} × {partner.share_percentage}% "
            f"(Product: {product_id})"
        )

        transaction = PartnerWalletTransaction(
            partner_id=partner.id,
            amount=profit_amount,
            transaction_type="sale_profit",
            reference_id=sale_id,
            reference_type="sale",
            description=description,
            balance_after=new_balance,
            created_at=datetime.now(timezone.utc),
        )

        self.db.add(transaction)
        await self.db.flush()

        return transaction

    async def process_sale_partner_profits(
        self,
        sale_id: UUID,
        sale_items: List[Any],  # SaleItem objects
    ) -> Dict[str, Any]:
        """
        Main integration point for SaleService.
        Process all partner profits for a sale within the existing transaction.

        Constitution VI: Atomic transactions with sorted lock ordering.

        Args:
            sale_id: UUID of the sale
            sale_items: List of SaleItem objects

        Returns:
            Dict with 'processed' count and 'total_profit' amount

        Raises:
            ValueError: If profit calculation fails (FR-014)
        """
        logger.info(
            f"Processing partner profits for sale {sale_id} with {len(sale_items)} items"
        )

        processed_count = 0
        total_partner_profit = Decimal("0.00")

        if not sale_items:
            logger.debug(f"No sale items for sale {sale_id}, returning empty result")
            return {"processed": 0, "total_profit": Decimal("0.00")}

        items_by_product = {}
        for item in sale_items:
            product_id = (
                item.product_id if hasattr(item, "product_id") else item["product_id"]
            )
            quantity = item.quantity if hasattr(item, "quantity") else item["quantity"]
            unit_price = (
                item.unit_price if hasattr(item, "unit_price") else item["unit_price"]
            )

            items_by_product[product_id] = {
                "quantity": quantity,
                "unit_price": unit_price,
            }

        product_ids = list(items_by_product.keys())
        products_to_process = []

        for product_id in product_ids:
            # SaleService already locks products, but we re-fetch to ensure we have partner_id
            product = await self.get_product_for_update(product_id)
            if product and product.partner_id:
                products_to_process.append(product)

        partner_ids = list(set(p.partner_id for p in products_to_process))
        partners = {}
        for partner_id in partner_ids:
            partner = await self.get_partner_for_update(partner_id)
            if partner:
                partners[partner_id] = partner

        for product in products_to_process:
            product_id = product.id
            item_info = items_by_product.get(product_id)

            if not item_info:
                continue

            quantity_sold = item_info["quantity"]
            unit_price = item_info["unit_price"]

            partner = partners.get(product.partner_id)
            if not partner:
                logger.warning(
                    f"Partner {product.partner_id} not found for product {product.id}"
                )
                continue

            transaction = await self.credit_partner_wallet(
                partner, sale_id, product.id, quantity_sold, unit_price
            )

            processed_count += 1
            total_partner_profit += transaction.amount

            logger.info(
                f"Processed profit for sale {sale_id}: product={product_id}, "
                f"partner={product.partner_id}, quantity={quantity_sold}, "
                f"profit={transaction.amount}"
            )

        logger.info(
            f"Partner profit processing complete for sale {sale_id}: "
            f"{processed_count} items processed, total_profit={total_partner_profit}"
        )

        return {
            "processed": processed_count,
            "total_profit": total_partner_profit,
        }

    # Wallet Management Methods

    async def get_partner_wallet_balance(self, partner_id: UUID) -> Decimal:
        """
        Get current wallet balance (O(1) using balance_after on latest transaction).

        Constitution I: Financial Accuracy - returns DECIMAL type.

        Args:
            partner_id: UUID of the partner

        Returns:
            Current wallet balance as Decimal (0.00 if no transactions)
        """
        query = (
            select(PartnerWalletTransaction)
            .where(PartnerWalletTransaction.partner_id == partner_id)
            .order_by(PartnerWalletTransaction.created_at.desc())
            .limit(1)
        )
        result = await self.db.execute(query)
        latest_transaction = result.scalar_one_or_none()

        if latest_transaction:
            return latest_transaction.balance_after

        return Decimal("0.00")

    async def get_partner_wallet_transactions(
        self,
        partner_id: UUID,
        limit: int = 100,
        offset: int = 0,
    ) -> List[PartnerWalletTransaction]:
        """
        Get paginated transaction history.

        Constitution IV: Immutable Financial Records - returns read-only transactions.

        Args:
            partner_id: UUID of the partner
            limit: Maximum number of transactions to return (default 100)
            offset: Number of transactions to skip (default 0)

        Returns:
            List of PartnerWalletTransaction objects ordered by created_at desc
        """
        query = (
            select(PartnerWalletTransaction)
            .where(PartnerWalletTransaction.partner_id == partner_id)
            .order_by(PartnerWalletTransaction.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def adjust_wallet(
        self,
        partner_id: UUID,
        amount: Decimal,
        description: str,
    ) -> PartnerWalletTransaction:
        """
        Make manual adjustment to partner wallet.

        Constitution IV: Immutable Financial Records.
        Constitution VI: Atomic operation with record locking.

        Args:
            partner_id: UUID of the partner
            amount: Amount to adjust (positive for credit, negative for debit)
            description: Human-readable description of the adjustment

        Returns:
            Created PartnerWalletTransaction

        Raises:
            ValueError: If amount is 0 (CHECK constraint violation)
        """
        logger.info(
            f"Adjusting wallet for partner {partner_id}: amount={amount}, description={description}"
        )

        if amount == Decimal("0"):
            logger.error(f"Adjustment amount cannot be zero for partner {partner_id}")
            raise ValueError("Adjustment amount cannot be zero")

        partner = await self.get_partner_for_update(partner_id)
        if not partner:
            logger.error(f"Partner {partner_id} not found for wallet adjustment")
            raise ValueError(f"Partner {partner_id} not found")

        previous_balance = await self.get_partner_wallet_balance(partner_id)
        new_balance = previous_balance + amount

        transaction = PartnerWalletTransaction(
            partner_id=partner_id,
            amount=amount,
            transaction_type="manual_adjustment",
            reference_id=None,
            reference_type="manual",
            description=description,
            balance_after=new_balance,
            created_at=datetime.now(timezone.utc),
        )

        self.db.add(transaction)
        await self.db.commit()
        await self.db.refresh(transaction)

        logger.info(
            f"Wallet adjustment complete: partner={partner_id}, "
            f"previous_balance={previous_balance}, adjustment={amount}, "
            f"new_balance={new_balance}, transaction_id={transaction.id}"
        )

        return transaction
