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
from app.models.product_assignment import ProductAssignment
from app.models.partner_wallet_transaction import PartnerWalletTransaction
from app.schemas.product_assignment import (
    ProductAssignmentCreate,
    ProductAssignmentUpdate,
)

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

    # Assignment Management Methods

    async def create_assignment(
        self, data: ProductAssignmentCreate
    ) -> ProductAssignment:
        """
        Create a new product assignment.

        Business Rules:
        - Only one active assignment per product
        - share_percentage defaults to partner's default if not specified
        - Cannot delete partner or product with existing assignments

        Args:
            data: ProductAssignmentCreate schema

        Returns:
            Created ProductAssignment

        Raises:
            ValueError: If product already has an active assignment
        """
        logger.info(
            f"Creating assignment: product={data.product_id}, partner={data.partner_id}, "
            f"quantity={data.assigned_quantity}, share={data.share_percentage}"
        )

        # Check for existing active assignment for this product
        existing_query = select(ProductAssignment).where(
            ProductAssignment.product_id == data.product_id,
            ProductAssignment.status == "active",
        )
        result = await self.db.execute(existing_query)
        existing = result.scalar_one_or_none()

        if existing:
            logger.warning(
                f"Assignment creation failed: product {data.product_id} already has "
                f"active assignment {existing.id}"
            )
            raise ValueError(
                f"Product {data.product_id} already has an active assignment. "
                "Only one active assignment per product is allowed."
            )

        # Get partner to use default share_percentage if not specified
        partner_query = select(Partner).where(Partner.id == data.partner_id)
        partner_result = await self.db.execute(partner_query)
        partner = partner_result.scalar_one_or_none()

        if not partner:
            logger.error(
                f"Assignment creation failed: partner {data.partner_id} not found"
            )
            raise ValueError(f"Partner {data.partner_id} not found")

        # Use provided share_percentage or partner's default
        share_percentage = (
            data.share_percentage
            if data.share_percentage is not None
            else partner.share_percentage
        )

        # Create assignment
        assignment = ProductAssignment(
            partner_id=data.partner_id,
            product_id=data.product_id,
            assigned_quantity=data.assigned_quantity,
            remaining_quantity=data.assigned_quantity,  # Initially all quantities remain
            share_percentage=share_percentage,
            status="active",
        )

        self.db.add(assignment)
        await self.db.commit()
        await self.db.refresh(assignment)

        logger.info(
            f"Assignment created successfully: id={assignment.id}, "
            f"product={assignment.product_id}, partner={assignment.partner_id}, "
            f"quantity={assignment.assigned_quantity}, share={assignment.share_percentage}"
        )

        return assignment

    async def get_assignment(self, assignment_id: UUID) -> Optional[ProductAssignment]:
        """
        Get assignment by ID.

        Args:
            assignment_id: UUID of the assignment

        Returns:
            ProductAssignment or None if not found
        """
        query = select(ProductAssignment).where(ProductAssignment.id == assignment_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def list_assignments(
        self,
        partner_id: Optional[UUID] = None,
        product_id: Optional[UUID] = None,
        status: Optional[str] = None,
    ) -> List[ProductAssignment]:
        """
        List assignments with optional filters.

        Args:
            partner_id: Filter by partner (optional)
            product_id: Filter by product (optional)
            status: Filter by status ('active' or 'fulfilled') (optional)

        Returns:
            List of ProductAssignment objects
        """
        query = select(ProductAssignment)

        if partner_id:
            query = query.where(ProductAssignment.partner_id == partner_id)
        if product_id:
            query = query.where(ProductAssignment.product_id == product_id)
        if status:
            query = query.where(ProductAssignment.status == status)

        # Order by creation date, newest first
        query = query.order_by(ProductAssignment.created_at.desc())

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def update_assignment(
        self,
        assignment_id: UUID,
        data: ProductAssignmentUpdate,
    ) -> Optional[ProductAssignment]:
        """
        Update assignment.

        Business Rules:
        - Cannot update fulfilled assignments
        - Decreasing assigned_quantity cannot go below remaining_quantity already sold
        - Increasing assigned_quantity increases remaining_quantity by delta
        - Decreasing assigned_quantity decreases remaining_quantity by delta (must not go below 0)

        Args:
            assignment_id: UUID of the assignment
            data: ProductAssignmentUpdate schema

        Returns:
            Updated ProductAssignment or None if not found

        Raises:
            ValueError: If assignment is fulfilled or would result in negative remaining_quantity
        """
        assignment = await self.get_assignment(assignment_id)

        if not assignment:
            return None

        # Cannot update fulfilled assignments
        if assignment.status == "fulfilled":
            raise ValueError(
                "Cannot update fulfilled assignment. "
                "Assignment status is 'fulfilled' and no further changes are allowed."
            )

        # Update assigned_quantity if provided
        if data.assigned_quantity is not None:
            # Calculate delta
            delta = data.assigned_quantity - assignment.assigned_quantity
            new_remaining = assignment.remaining_quantity + delta

            if new_remaining < 0:
                raise ValueError(
                    f"Cannot decrease assigned_quantity below remaining_quantity. "
                    f"Current remaining_quantity: {assignment.remaining_quantity}, "
                    f"Attempted new remaining_quantity: {new_remaining}"
                )

            assignment.assigned_quantity = data.assigned_quantity
            assignment.remaining_quantity = new_remaining

        # Update share_percentage if provided
        if data.share_percentage is not None:
            assignment.share_percentage = data.share_percentage

        await self.db.commit()
        await self.db.refresh(assignment)

        return assignment

    async def delete_assignment(self, assignment_id: UUID) -> bool:
        """
        Delete assignment.

        Business Rules:
        - Can only delete assignments with no sales (remaining_quantity == assigned_quantity)
        - Cannot delete assignments with remaining_quantity < assigned_quantity (has sales)

        Args:
            assignment_id: UUID of the assignment

        Returns:
            True if deleted, False if not found

        Raises:
            ValueError: If assignment has sales (remaining_quantity < assigned_quantity)
        """
        assignment = await self.get_assignment(assignment_id)

        if not assignment:
            return False

        # Check if assignment has sales
        if assignment.remaining_quantity < assignment.assigned_quantity:
            raise ValueError(
                f"Cannot delete assignment with sales. "
                f"Remaining quantity ({assignment.remaining_quantity}) is less than "
                f"assigned quantity ({assignment.assigned_quantity}). "
                "Assignment must be retained for audit trail."
            )

        # Can only delete if all quantities remain (no sales)
        await self.db.delete(assignment)
        await self.db.commit()

        return True

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

    async def get_product_assignment_for_update(
        self,
        product_id: UUID,
    ) -> Optional[ProductAssignment]:
        """
        Lock active assignment for product using SELECT FOR UPDATE.

        Constitution VI: Atomic transactions with record locking.

        Args:
            product_id: UUID of the product

        Returns:
            Active ProductAssignment or None if not found
        """
        query = (
            select(ProductAssignment)
            .where(
                ProductAssignment.product_id == product_id,
                ProductAssignment.status == "active",
            )
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
        assignment: ProductAssignment,
        quantity: int,
        unit_price: Decimal,
    ) -> PartnerWalletTransaction:
        """
        Credit partner wallet and create transaction record.

        Constitution IV: Immutable Financial Records.
        Constitution I: Financial Accuracy with DECIMAL types.

        Args:
            partner: Partner object (must be locked with FOR UPDATE)
            sale_id: UUID of the sale
            assignment: ProductAssignment object
            quantity: Quantity sold from assignment
            unit_price: Unit price of the product

        Returns:
            Created PartnerWalletTransaction
        """
        profit_amount = await self.calculate_partner_profit(
            quantity, unit_price, assignment.share_percentage
        )

        previous_balance = await self.get_partner_wallet_balance(partner.id)
        new_balance = previous_balance + profit_amount

        description = (
            f"Sale profit: {quantity} × {unit_price} × {assignment.share_percentage}% "
            f"(Product: {assignment.product_id}, Assignment: {assignment.id})"
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
        assignments_to_update = []

        for product_id in product_ids:
            assignment = await self.get_product_assignment_for_update(product_id)
            if assignment:
                assignments_to_update.append(assignment)

        partner_ids = list(set(a.partner_id for a in assignments_to_update))
        partners = {}
        for partner_id in partner_ids:
            partner = await self.get_partner_for_update(partner_id)
            if partner:
                partners[partner_id] = partner

        for assignment in assignments_to_update:
            product_id = assignment.product_id
            item_info = items_by_product.get(product_id)

            if not item_info:
                continue

            quantity_to_sell = item_info["quantity"]
            unit_price = item_info["unit_price"]

            if assignment.remaining_quantity < quantity_to_sell:
                logger.error(
                    f"Insufficient assigned quantity for sale {sale_id}: "
                    f"product={product_id}, requested={quantity_to_sell}, "
                    f"available={assignment.remaining_quantity}"
                )
                raise ValueError(
                    f"Insufficient assigned quantity for product {product_id}. "
                    f"Requested: {quantity_to_sell}, Available: {assignment.remaining_quantity}"
                )

            partner = partners.get(assignment.partner_id)
            if not partner:
                logger.error(
                    f"Partner {assignment.partner_id} not found for assignment {assignment.id}"
                )
                raise ValueError(
                    f"Partner {assignment.partner_id} not found for assignment {assignment.id}"
                )

            assignment.remaining_quantity -= quantity_to_sell

            if assignment.remaining_quantity == 0:
                assignment.status = "fulfilled"
                logger.info(
                    f"Assignment {assignment.id} fulfilled: product={product_id}, "
                    f"partner={assignment.partner_id}"
                )

            transaction = await self.credit_partner_wallet(
                partner, sale_id, assignment, quantity_to_sell, unit_price
            )

            processed_count += 1
            total_partner_profit += transaction.amount

            logger.info(
                f"Processed profit for sale {sale_id}: product={product_id}, "
                f"partner={assignment.partner_id}, quantity={quantity_to_sell}, "
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
