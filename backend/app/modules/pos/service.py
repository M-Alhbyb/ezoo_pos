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

from sqlalchemy import select, and_, cast, Date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.sale import Sale
from app.models.sale_item import SaleItem
from app.models.sale_fee import SaleFee
from app.models.sale_payment import SalePayment
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
from app.modules.partners.partner_profit_service import PartnerProfitService
from app.modules.customers.service import CustomerService
from app.core.constants import LedgerTransactionType


class SaleService:
    """Service class for sale operations."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.inventory_service = InventoryService(db)
        self.partner_profit_service = PartnerProfitService(db)

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

        # 2. VALIDATE PAYMENTS
        if not sale_data.payments and sale_data.payment_method_id:
            # Backward compatibility: Create a single payment from payment_method_id
            # This is handled later during breakdown calculation if payments is empty
            pass
        elif not sale_data.payments:
            raise ValueError("At least one payment method is required")

        # Resolve primary Payment Method for legacy support
        if sale_data.payments:
            payment_method_id = sale_data.payments[0].payment_method_id
        else:
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

        breakdown = await self.calculate_breakdown(
            SaleCalculationRequest(items=sale_data.items, fees=sale_data.fees)
        )

        # 4.5 VALIDATE PAYMENT TOTAL
        if not sale_data.payments:
            if sale_data.customer_id:
                # For customers, an empty payment list means full debt (0 payment)
                payments_to_create = []
                payment_total = Decimal("0")
            else:
                # For walk-in customers, default to full amount for the single payment method
                payments_to_create = [{"payment_method_id": payment_method_id, "amount": breakdown.total}]
                payment_total = breakdown.total
        else:
            payment_total = sum(p.amount for p in sale_data.payments)
            payments_to_create = [p.model_dump() for p in sale_data.payments]

        # Validation logic for payment total
        if not sale_data.customer_id:
            # For walk-in customers, payment must be exactly equal to total
            if payment_total != breakdown.total:
                raise ValueError(
                    f"Payment total ({payment_total}) does not match grand total ({breakdown.total}). "
                    "For walk-in customers, full payment is required."
                )
        else:
            # For registered customers, payment can be less than total (debt/loan)
            if payment_total > breakdown.total:
                # Still don't allow overpayment in the POS for now unless specifically handled
                raise ValueError(
                    f"Payment total ({payment_total}) exceeds grand total ({breakdown.total})."
                )
            # payment_total < breakdown.total is allowed for customers (recorded as loan)

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
            customer_id=sale_data.customer_id,
        )

        self.db.add(sale)
        await self.db.flush()  # Get sale ID

        # Create sale payments
        for p_data in payments_to_create:
            sale_payment = SalePayment(
                sale_id=sale.id,
                payment_method_id=p_data["payment_method_id"],
                amount=p_data["amount"],
            )
            self.db.add(sale_payment)

        # Create sale items
        created_items = []
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
            created_items.append(sale_item)

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

        # 6. PROCESS PARTNER PROFITS (if any products are assigned)
        # Constitution VI: Atomic transaction - if profit calculation fails, entire sale rolls back
        await self.partner_profit_service.process_sale_partner_profits(
            sale.id, created_items
        )

        # 7. CUSTOMER CREDIT SALE PROCESSING (T013, T015, T015.5)
        if sale_data.customer_id:
            customer_service = CustomerService(self.db)
            customer = await customer_service.get_customer(sale_data.customer_id)
            if not customer:
                raise ValueError(f"Customer {sale_data.customer_id} not found")

            # T013: Check credit limit before creating ledger entry
            # Only check the portion that will actually be added to the debt (unpaid amount)
            paid_amount = payment_total
            credit_amount = breakdown.total - paid_amount
            
            is_exceeded, current_balance, credit_limit = await customer_service.check_credit_limit(
                sale_data.customer_id, credit_amount
            )
            if is_exceeded:
                raise ValueError(
                    f"Credit limit exceeded. Current balance: {current_balance}, "
                    f"Credit limit: {credit_limit}, Unpaid portion: {credit_amount}"
                )
 
            # T015: Always create a SALE ledger entry for the full amount
            # This ensures "Total Sales" in the summary is accurate
            await customer_service.record_ledger_entry(
                customer_id=sale_data.customer_id,
                type=LedgerTransactionType.SALE,
                amount=breakdown.total,
                reference_id=sale.id,
                note=f"بيع - فاتورة #{sale.id.hex[:8].upper()}",
            )
 
            # T015.5: Create PAYMENT ledger entry for paid_amount (if any)
            if paid_amount > 0:
                payment_method_name = payment_method.name if payment_method else "نقدي"
                await customer_service.record_ledger_entry(
                    customer_id=sale_data.customer_id,
                    type=LedgerTransactionType.PAYMENT,
                    amount=paid_amount,
                    reference_id=sale.id,
                    payment_method=payment_method_name,
                    note=f"دفعة مقابل الفاتورة #{sale.id.hex[:8].upper()}",
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
                selectinload(Sale.payments).joinedload(SalePayment.payment_method),
            )
            .order_by(Sale.created_at.desc())
        )

        # Applyfilters
        conditions = []

        if filters.start_date:
            conditions.append(cast(Sale.created_at, Date) >= filters.start_date)

        if filters.end_date:
            conditions.append(cast(Sale.created_at, Date) <= filters.end_date)

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
                selectinload(Sale.customer),
                selectinload(Sale.payments).joinedload(SalePayment.payment_method),
            )
            .where(Sale.id == sale_id)
        )

        result = await self.db.execute(query)
        sale = result.scalar_one_or_none()
        
        if sale and not sale.is_reversal:
            # Calculate remaining quantities by looking at reversals
            rev_query = select(Sale).options(selectinload(Sale.items)).where(
                and_(Sale.original_sale_id == sale_id, Sale.is_reversal == True)
            )
            rev_result = await self.db.execute(rev_query)
            reversals = rev_result.scalars().all()
            
            reversed_qtys = {}
            for rev in reversals:
                for item in rev.items:
                    reversed_qtys[item.product_id] = reversed_qtys.get(item.product_id, 0) + abs(item.quantity)
            
            for item in sale.items:
                item.remaining_quantity = item.quantity - reversed_qtys.get(item.product_id, 0)
        
        return sale

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

    async def reverse_sale(self, sale_id: UUID, reversal_data: "SaleReversalCreate") -> Sale:
        """
        Reverse a sale (full or partial) and restore stock.

        Constitution IV (Immutable Financial Records):
        - Original sale remains unchanged
        - Reversal creates separate correction record
        - Stock restored with inventory log

        Args:
            sale_id: UUID of sale to reverse
            reversal_data: Contains reason and optional items to reverse

        Returns:
            Sale instance representing the reversal
        """
        from app.schemas.sale import SaleReversalCreate
        
        # Get sale with items
        original_sale = await self.get_sale_detail(sale_id)
        if not original_sale:
            raise ValueError(f"Sale {sale_id} not found")

        # Get all existing reversals for this sale to calculate remaining quantities
        existing_reversals_query = select(Sale).options(selectinload(Sale.items)).where(
            and_(Sale.original_sale_id == sale_id, Sale.is_reversal == True)
        )
        existing_reversals_result = await self.db.execute(existing_reversals_query)
        existing_reversals = existing_reversals_result.scalars().all()

        # Calculate already reversed quantities per product
        reversed_quantities = {}
        for rev in existing_reversals:
            for item in rev.items:
                reversed_quantities[item.product_id] = reversed_quantities.get(item.product_id, 0) + abs(item.quantity)

        # Determine what to reverse
        items_to_process = []
        if reversal_data.items:
            # Partial reversal
            for rev_item in reversal_data.items:
                # Find original item
                orig_item = next((i for i in original_sale.items if i.product_id == rev_item.product_id), None)
                if not orig_item:
                    raise ValueError(f"Product {rev_item.product_id} was not part of original sale {sale_id}")
                
                already_reversed = reversed_quantities.get(rev_item.product_id, 0)
                remaining = orig_item.quantity - already_reversed
                
                if rev_item.quantity > remaining:
                    raise ValueError(
                        f"Cannot reverse {rev_item.quantity} of {orig_item.product_name}. "
                        f"Only {remaining} remaining (Sold: {orig_item.quantity}, Already Reversed: {already_reversed})"
                    )
                
                items_to_process.append({
                    "orig_item": orig_item,
                    "quantity": rev_item.quantity
                })
        else:
            # Full reversal (of remaining items)
            has_remaining = False
            for orig_item in original_sale.items:
                already_reversed = reversed_quantities.get(orig_item.product_id, 0)
                remaining = orig_item.quantity - already_reversed
                if remaining > 0:
                    items_to_process.append({
                        "orig_item": orig_item,
                        "quantity": remaining
                    })
                    has_remaining = True
            
            if not has_remaining:
                raise ValueError(f"Sale {sale_id} has already been fully reversed")

        # Calculate financial values for the reversal
        rev_subtotal = Decimal("0")
        rev_total_cost = Decimal("0")
        
        for proc in items_to_process:
            orig_item = proc["orig_item"]
            qty = proc["quantity"]
            
            # Use original unit price ("taking price")
            line_total = calculate_line_total(qty, orig_item.unit_price)
            rev_subtotal += line_total
            rev_total_cost += Decimal(qty) * (orig_item.base_cost or Decimal("0"))

        # VAT calculation for the reversed portion
        rev_vat_total = Decimal("0")
        if original_sale.vat_rate:
            # Simple proportional VAT calculation
            # In a more complex system, we might recalculate fees first
            rev_vat_total = round_currency(rev_subtotal * (original_sale.vat_rate / Decimal("100")))

        # Fees calculation
        # Only reverse fees if it's a full reversal AND no previous reversals exist
        # This is a simplification. Usually fees are non-refundable for partials.
        rev_fees_total = Decimal("0")
        is_full_reversal = len(items_to_process) == len(original_sale.items) and \
                          all(proc["quantity"] == original_sale.items[i].quantity for i, proc in enumerate(items_to_process))
        
        if is_full_reversal and not existing_reversals:
            rev_fees_total = original_sale.fees_total

        rev_grand_total = rev_subtotal + rev_fees_total + rev_vat_total
        rev_profit = rev_grand_total - rev_total_cost

        # Create reversal record
        reversal = Sale(
            payment_method_id=original_sale.payment_method_id,
            subtotal=-rev_subtotal,
            fees_total=-rev_fees_total,
            vat_rate=original_sale.vat_rate,
            vat_total=-rev_vat_total if rev_vat_total > 0 else None,
            grand_total=-rev_grand_total,
            total_cost=-rev_total_cost,
            profit=-rev_profit,
            note=reversal_data.reason,
            is_reversal=True,
            original_sale_id=original_sale.id,
            customer_id=original_sale.customer_id
        )

        self.db.add(reversal)
        await self.db.flush()  # Get reversal ID

        # Create reversed sale items
        for proc in items_to_process:
            orig_item = proc["orig_item"]
            qty = proc["quantity"]
            
            reversal_item = SaleItem(
                sale_id=reversal.id,
                product_id=orig_item.product_id,
                product_name=orig_item.product_name,
                quantity=-qty,
                unit_price=orig_item.unit_price,
                base_cost=orig_item.base_cost,
                vat_rate=orig_item.vat_rate,
                line_total=-calculate_line_total(qty, orig_item.unit_price),
            )
            self.db.add(reversal_item)

        # Create reversed sale fees if any
        if rev_fees_total > 0:
            for fee in original_sale.fees:
                reversal_fee = SaleFee(
                    sale_id=reversal.id,
                    fee_type=fee.fee_type,
                    fee_label=fee.fee_label,
                    fee_value_type=fee.fee_value_type,
                    fee_value=fee.fee_value,
                    calculated_amount=-fee.calculated_amount,
                )
                self.db.add(reversal_fee)

        # Restore stock
        for proc in items_to_process:
            await self.inventory_service.restore_stock(
                product_id=proc["orig_item"].product_id,
                quantity=proc["quantity"],
                reason="reversal",
                reference_id=reversal.id,
            )

        # Update customer ledger if applicable
        if original_sale.customer_id:
            customer_service = CustomerService(self.db)
            await customer_service.record_ledger_entry(
                customer_id=original_sale.customer_id,
                type=LedgerTransactionType.RETURN,
                amount=rev_grand_total,
                reference_id=reversal.id,
                note=f"إرجاع منتجات - فاتورة #{original_sale.id.hex[:8].upper()}",
            )

        await self.db.commit()

        # Fetch eagerly avoiding context errors
        reversal_detail = await self.get_sale_detail(reversal.id)
        return reversal_detail

    async def _get_reversal_by_sale_id(self, sale_id: UUID) -> Optional[Sale]:
        """Check if sale has been reversed."""
        query = select(Sale).where(Sale.original_sale_id == sale_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
