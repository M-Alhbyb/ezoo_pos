"""
Sale Service - Business logic for POS sales.

Implements Constitution principles:
- I (Financial Accuracy): Decimal type for all monetary values
- II (Single Source of Truth): Backend calculates all totals
- III (Explicit Over Implicit): All fee fields stored explicitly
- IV (Immutable Financial Records): Sales are immutable after creation
"""

from decimal import Decimal
from typing import Optional, List, Tuple
from uuid import UUID
from datetime import datetime

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.sale import Sale
from app.models.sale_item import SaleItem
from app.models.sale_fee import SaleFee
from app.models.product import Product
from app.models.payment_method import PaymentMethod
from app.models.settings import Settings
from app.schemas.sale import (
    SaleCreate,
    SaleCalculationRequest,
    SaleBreakdown,
    SaleItemResponse,
    SaleFeeResponse,
    SaleListFilter,
)
from app.core.calculations import (
    calculate_line_total,
    calculate_fee_amount,
    calculate_vat,
    round_currency,
)
from app.modules.inventory.service import InventoryService


class SaleService:
    """Service class for sale operations."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.inventory_service = InventoryService(db)

    async def calculate_breakdown(
        self, request: SaleCalculationRequest
    ) -> SaleBreakdown:
        """
        Calculate financial breakdown for a proposed sale.

        Constitution II: Backend is sole authority for calculations.

        Args:
            request: Sale calculation request with items and fees

        Returns:
            SaleBreakdown with all financial calculations

        Raises:
            ValueError: If product not found or inactive
        """
        items_response = []
        subtotal = Decimal("0")

        # Calculate line totals
        for item_req in request.items:
            # Get product
            product = await self._get_product(item_req.product_id)
            if not product:
                raise ValueError(f"Product {item_req.product_id} not found")
            if not product.is_active:
                raise ValueError(f"Product {item_req.product_id} is inactive")

            # Determine unit price
            unit_price = (
                item_req.unit_price_override
                if item_req.unit_price_override is not None
                else product.selling_price
            )

            # Calculate line total
            line_total = calculate_line_total(item_req.quantity, unit_price)

            items_response.append(
                SaleItemResponse(
                    product_id=item_req.product_id,
                    product_name=product.name,
                    quantity=item_req.quantity,
                    unit_price=unit_price,
                    price=unit_price,
                    base_cost=product.base_price,
                    vat_rate=None,  # Will be set after global VAT calc
                    line_total=line_total,
                )
            )

            subtotal += line_total

        # Calculate fees
        fees_response = []
        fees_total = Decimal("0")

        for fee_req in request.fees:
            calculated_amount = calculate_fee_amount(
                fee_value=fee_req.fee_value,
                fee_value_type=fee_req.fee_value_type,
                subtotal=subtotal,
            )

            fees_response.append(
                SaleFeeResponse(
                    fee_type=fee_req.fee_type,
                    fee_label=fee_req.fee_label,
                    fee_value_type=fee_req.fee_value_type,
                    fee_value=fee_req.fee_value,
                    calculated_amount=calculated_amount,
                )
            )

            fees_total += calculated_amount

        # Calculate VAT
        vat_enabled = await self._get_vat_enabled()
        vat_type = None
        vat_value = None
        vat_rate = None
        vat_amount = None

        if vat_enabled:
            vat_type = await self._get_vat_type()
            vat_value = await self._get_vat_rate()
            vat_amount, vat_rate = calculate_vat(
                subtotal, fees_total, vat_enabled, vat_type, vat_value
            )

        # Calculate total
        total = round_currency(subtotal + fees_total + (vat_amount or Decimal("0")))

        return SaleBreakdown(
            items=items_response,
            subtotal=subtotal,
            fees=fees_response,
            fees_total=fees_total,
            vat_enabled=vat_enabled,
            vat_rate=vat_rate,
            vat_amount=vat_amount,
            vat_total=vat_amount,  # Alias for consistency
            total=total,
            grand_total=total,  # Alias for consistency
            vat_percentage=str(int(vat_rate)) if vat_rate is not None else None,
        )

    async def create_sale(self, sale_data: SaleCreate) -> Sale:
        """
        Create a confirmed sale with atomic stock deduction and idempotency support.
        """
        # 1. IDEMPOTENCY CHECK
        if sale_data.idempotency_key:
            query = (
                select(Sale)
                .options(
                    selectinload(Sale.items),
                    selectinload(Sale.fees),
                    selectinload(Sale.payment_method),
                )
                .where(Sale.idempotency_key == sale_data.idempotency_key)
            )
            existing_result = await self.db.execute(query)
            existing_sale = existing_result.scalar_one_or_none()
            if existing_sale:
                return existing_sale

        # Resolve Payment Method safely
        payment_method_id = sale_data.payment_method_id
        if not payment_method_id:
            pm_query = select(PaymentMethod).where(PaymentMethod.is_active == True)
            pm_result = await self.db.execute(pm_query)
            payment_method = pm_result.scalars().first()
            if not payment_method:
                payment_method = PaymentMethod(name="Auto-Fallback", is_active=True)
                self.db.add(payment_method)
                await self.db.flush()
            payment_method_id = payment_method.id
        else:
            payment_method = await self._get_payment_method(payment_method_id)
            if not payment_method:
                raise ValueError(f"Payment method {payment_method_id} not found")
            if not payment_method.is_active:
                raise ValueError(f"Payment method {payment_method_id} is inactive")

        # ROW-LEVEL LOCKING against deadlocks
        # Sort product IDs first
        product_ids = sorted(list(set(item.product_id for item in sale_data.items)))
        
        products = {}
        for pid in product_ids:
            # Lock row with SELECT FOR UPDATE
            prod = await self.inventory_service._get_product_for_update(pid)
            if not prod:
                raise ValueError(f"Product {pid} not found")
            if not prod.is_active:
                raise ValueError(f"Product {prod.name} is inactive")
            products[pid] = prod
        
        # 4. STOCK VALIDATION
        for item in sale_data.items:
            prod = products[item.product_id]
            if prod.stock_quantity < item.quantity:
                raise ValueError(
                    f"Insufficient stock for Product {prod.name}: "
                    f"requested {item.quantity}, available {prod.stock_quantity}"
                )
        
        # Calculate breakdown safely since locks are acquired
        breakdown = await self.calculate_breakdown(
            SaleCalculationRequest(items=sale_data.items, fees=sale_data.fees)
        )

        # Calculate total cost and profit
        total_cost = Decimal("0")
        for item_data in sale_data.items:
            prod = products[item_data.product_id]
            total_cost += Decimal(item_data.quantity) * prod.base_price
        
        profit = breakdown.total - total_cost

        # Create sale
        sale = Sale(
            payment_method_id=payment_method_id,
            subtotal=breakdown.subtotal,
            fees_total=breakdown.fees_total,
            vat_rate=breakdown.vat_rate,
            vat_total=breakdown.vat_amount,
            grand_total=breakdown.total,
            total_cost=total_cost,
            profit=profit,
            note=sale_data.note,
            idempotency_key=sale_data.idempotency_key,
        )

        self.db.add(sale)
        await self.db.flush()  # Get sale ID

        # Create sale items
        for item_data, item_response in zip(sale_data.items, breakdown.items):
            prod = products[item_data.product_id]
            sale_item = SaleItem(
                sale_id=sale.id,
                product_id=item_data.product_id,
                product_name=item_response.product_name,
                quantity=item_data.quantity,
                unit_price=item_response.unit_price,
                base_cost=prod.base_price,
                vat_rate=breakdown.vat_rate,
                line_total=item_response.line_total,
            )
            self.db.add(sale_item)

        # Create sale fees
        for fee_data, fee_response in zip(sale_data.fees, breakdown.fees):
            sale_fee = SaleFee(
                sale_id=sale.id,
                fee_type=fee_data.fee_type,
                fee_label=fee_data.fee_label,
                fee_value_type=fee_data.fee_value_type,
                fee_value=fee_data.fee_value,
                calculated_amount=fee_response.calculated_amount,
            )
            self.db.add(sale_fee)

        # 5. ATOMIC STOCK DEDUCTION & LOGGING
        for item_data in sale_data.items:
            await self.inventory_service.deduct_stock(
                product_id=item_data.product_id,
                quantity=item_data.quantity,
                reason="sale",
                reference_id=sale.id,
            )

        await self.db.commit()

        # Fetch eagerly avoiding context errors
        sale = await self.get_sale_detail(sale.id)
        if not sale:
            raise ValueError(f"Sale {sale.id} not found after creation")

        return sale

    async def validate_stock_availability(
        self, items: List[Tuple[UUID, int]]
    ) -> List[str]:
        """
        Validate that sufficient stock exists for all items.

        Args:
            items: List of (product_id, quantity) tuples

        Returns:
            List of error messages (empty if all valid)
        """
        issues = []

        for product_id, quantity in items:
            product = await self._get_product(product_id)
            if not product:
                issues.append(f"Product {product_id} not found")
                continue

            if not product.is_active:
                issues.append(f"Product {product.name} is inactive")
                continue

            if product.stock_quantity < quantity:
                issues.append(
                    f"Product {product.name}: requested {quantity}, available {product.stock_quantity}"
                )

        return issues

    async def list_sales(self, filters: SaleListFilter) -> Tuple[List[Sale], int]:
        """
        List sales with optional filters.

        Args:
            filters: Sale list filters

        Returns:
            Tuple of (sales list, total count)
        """
        page_size = min(filters.page_size, 100)

        query = (
            select(Sale)
            .options(
                selectinload(Sale.items),
                selectinload(Sale.fees),
                selectinload(Sale.payment_method),
            )
            .order_by(Sale.created_at.desc())
        )

        # Applyfilters
        conditions = []

        if filters.start_date:
            conditions.append(Sale.created_at >= filters.start_date)

        if filters.end_date:
            conditions.append(Sale.created_at <= filters.end_date)

        if filters.payment_method_id:
            conditions.append(Sale.payment_method_id == filters.payment_method_id)

        if conditions:
            query = query.where(and_(*conditions))

        # Count total
        count_query = (
            select(Sale).where(and_(*conditions)) if conditions else select(Sale)
        )
        count_query = select(Sale.id).select_from(count_query.subquery())
        total_result = await self.db.execute(count_query)
        total = len(total_result.all())

        # Paginate
        offset = (filters.page - 1) * page_size
        query = query.offset(offset).limit(page_size)

        result = await self.db.execute(query)
        sales = result.scalars().all()

        return list(sales), total

    async def get_sale_detail(self, sale_id: UUID) -> Optional[Sale]:
        """
        Get sale detail with full breakdown.

        Args:
            sale_id: Sale UUID

        Returns:
            Sale instance with items and fees loaded
        """
        query = (
            select(Sale)
            .options(
                selectinload(Sale.items),
                selectinload(Sale.fees),
                selectinload(Sale.payment_method),
            )
            .where(Sale.id == sale_id)
        )

        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def _get_product(self, product_id: UUID) -> Optional[Product]:
        """Get product by ID."""
        query = select(Product).where(Product.id == product_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def _get_payment_method(
        self, payment_method_id: UUID
    ) -> Optional[PaymentMethod]:
        """Get payment method by ID."""
        query = select(PaymentMethod).where(PaymentMethod.id == payment_method_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def _get_vat_enabled(self) -> bool:
        """Check if VAT is enabled in settings."""
        query = select(Settings).where(Settings.key == "vat_enabled")
        result = await self.db.execute(query)
        setting = result.scalar_one_or_none()

        if not setting:
            return False

        return setting.value.lower() in ("true", "1", "yes")

    async def _get_vat_type(self) -> str:
        """Get VAT type from settings (percent or fixed)."""
        query = select(Settings).where(Settings.key == "vat_type")
        result = await self.db.execute(query)
        setting = result.scalar_one_or_none()

        if not setting:
            return "percent"  # Default to percentage

        return setting.value.lower()

    async def _get_vat_rate(self) -> Decimal:
        """Get VAT rate from settings."""
        query = select(Settings).where(Settings.key == "vat_rate")
        result = await self.db.execute(query)
        setting = result.scalar_one_or_none()

        if not setting:
            return Decimal("16.00")  # Default 16%

        return Decimal(setting.value)

    async def reverse_sale(self, sale_id: UUID, reason: str) -> Sale:
        """
        Reverse a sale and restore stock.

        Constitution IV (Immutable Financial Records):
        - Original sale remains unchanged
        - Reversal creates separate correction record
        - Stock restored with inventory log

        Args:
            sale_id: UUID of sale to reverse
            reason: Reason for reversal (required)

        Returns:
            Sale instance representing the reversal

        Raises:
            ValueError: If sale not found or already reversed
        """
        # Get sale with items
        original_sale = await self.get_sale_detail(sale_id)
        if not original_sale:
            raise ValueError(f"Sale {sale_id} not found")

        # Check if already reversed
        existing_reversa1 = await self._get_reversal_by_sale_id(sale_id)
        if existing_reversa1:
            raise ValueError(f"Sale {sale_id} is already reversed")

        # Create reversal record
        reversal = Sale(
            payment_method_id=original_sale.payment_method_id,
            subtotal=-original_sale.subtotal,
            fees_total=-original_sale.fees_total,
            vat_rate=original_sale.vat_rate,
            vat_total=-original_sale.vat_total if original_sale.vat_total else None,
            grand_total=-original_sale.grand_total,
            total_cost=-original_sale.total_cost,
            profit=-original_sale.profit,
            note=reason,
            is_reversal=True,
            original_sale_id=original_sale.id,
        )

        self.db.add(reversal)
        await self.db.flush()  # Get reversal ID

        # Create reversed sale items
        for item in original_sale.items:
            reversal_item = SaleItem(
                sale_id=reversal.id,
                product_id=item.product_id,
                product_name=item.product_name,
                quantity=-item.quantity,
                unit_price=item.unit_price,  # Base and unit remain positive
                base_cost=item.base_cost,
                vat_rate=item.vat_rate,
                line_total=-item.line_total,
            )
            self.db.add(reversal_item)
            
        # Create reversed sale fees
        for fee in original_sale.fees:
            reversal_fee = SaleFee(
                sale_id=reversal.id,
                fee_type=fee.fee_type,
                fee_label=fee.fee_label,
                fee_value_type=fee.fee_value_type,
                fee_value=fee.fee_value,  # Retain original config values
                calculated_amount=-fee.calculated_amount,
            )
            self.db.add(reversal_fee)

        # Restore stock for each item using the original positive quantity
        for item in original_sale.items:
            await self.inventory_service.restore_stock(
                product_id=item.product_id,
                quantity=item.quantity,
                reason="reversal",
                reference_id=reversal.id,
            )

        await self.db.commit()
        
        # Fetch eagerly avoiding context errors
        reversal_detail = await self.get_sale_detail(reversal.id)
        if not reversal_detail:
            raise ValueError(f"Sale {reversal.id} not found after creation")

        return reversal_detail

    async def _get_reversal_by_sale_id(self, sale_id: UUID) -> Optional[Sale]:
        """Check if sale has been reversed."""
        query = select(Sale).where(Sale.original_sale_id == sale_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
