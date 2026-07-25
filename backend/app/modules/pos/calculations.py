"""
POS Calculation Helpers - Product/setting lookups and sale breakdown calculation.

Extracted from SaleService to separate calculation logic from orchestration.
"""

from decimal import Decimal
from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.product import Product
from app.models.payment_method import PaymentMethod
from app.models.settings import Settings
from app.schemas.sale import (
    SaleCalculationRequest,
    SaleBreakdown,
    SaleItemResponse,
    SaleFeeResponse,
)
from app.core.calculations import (
    calculate_line_total,
    calculate_fee_amount,
    calculate_vat,
    round_currency,
)


async def get_product(db: AsyncSession, product_id: UUID) -> Optional[Product]:
    """Get product by ID."""
    query = select(Product).where(Product.id == product_id)
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def get_payment_method(
    db: AsyncSession, payment_method_id: UUID
) -> Optional[PaymentMethod]:
    """Get payment method by ID."""
    query = select(PaymentMethod).where(PaymentMethod.id == payment_method_id)
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def get_vat_enabled(db: AsyncSession) -> bool:
    """Check if VAT is enabled in settings."""
    query = select(Settings).where(Settings.key == "vat_enabled")
    result = await db.execute(query)
    setting = result.scalar_one_or_none()

    if not setting:
        return False

    return setting.value.lower() in ("true", "1", "yes")


async def get_vat_type(db: AsyncSession) -> str:
    """Get VAT type from settings (percent or fixed)."""
    query = select(Settings).where(Settings.key == "vat_type")
    result = await db.execute(query)
    setting = result.scalar_one_or_none()

    if not setting:
        return "percent"  # Default to percentage

    return setting.value.lower()


async def get_vat_rate(db: AsyncSession) -> Decimal:
    """Get VAT rate from settings."""
    query = select(Settings).where(Settings.key == "vat_rate")
    result = await db.execute(query)
    setting = result.scalar_one_or_none()

    if not setting:
        return Decimal("16.00")  # Default 16%

    return Decimal(setting.value)


async def calculate_breakdown(
    db: AsyncSession, request: SaleCalculationRequest
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
        product = await get_product(db, item_req.product_id)
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
    vat_enabled = await get_vat_enabled(db)
    vat_type = None
    vat_value = None
    vat_rate = None
    vat_amount = None

    if vat_enabled:
        vat_type = await get_vat_type(db)
        vat_value = await get_vat_rate(db)
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
