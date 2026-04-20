"""
Financial calculation engine for EZOO POS.

This module contains all financial calculation functions following Constitution I:
- All calculations use Decimal type (never float)
- All calculations are deterministic and reproducible
- All values are rounded to 2 decimal places using ROUND_HALF_UP
"""

from decimal import Decimal, ROUND_HALF_UP
from typing import List, Dict, Any, Optional


TWOPLACES = Decimal(10) ** -2  # 0.01 for rounding to 2 decimal places


def round_currency(value: Decimal) -> Decimal:
    """
    Round a Decimal value to 2 decimal places using ROUND_HALF_UP (standard commercial rounding).

    Args:
        value: The decimal value to round

    Returns:
        The rounded value to 2 decimal places

    Examples:
        >>> round_currency(Decimal('3.335'))
        Decimal('3.34')
        >>> round_currency(Decimal('3.334'))
        Decimal('3.33')
    """
    return value.quantize(TWOPLACES, rounding=ROUND_HALF_UP)


def calculate_line_total(quantity: int, unit_price: Decimal) -> Decimal:
    """
    Calculate the total for a sale line item.

    Args:
        quantity: Number of units (must be positive integer)
        unit_price: Price per unit (must be non-negative Decimal)

    Returns:
        Line total rounded to 2 decimal places

    Raises:
        ValueError: If quantity is not positive or unit_price is negative

    Examples:
        >>> calculate_line_total(2, Decimal('150.00'))
        Decimal('300.00')
        >>> calculate_line_total(5, Decimal('33.33'))
        Decimal('166.65')
    """
    if quantity <= 0:
        raise ValueError(f"Quantity must be positive, got {quantity}")
    if unit_price < 0:
        raise ValueError(f"Unit price cannot be negative, got {unit_price}")

    return round_currency(Decimal(quantity) * unit_price)


def calculate_fee_amount(
    fee_value: Decimal, fee_value_type: str, subtotal: Decimal
) -> Decimal:
    """
    Calculate fee amount based on fee type (fixed or percentage).

    Args:
        fee_value: The fee value (amount for fixed, percentage for percent)
        fee_value_type: Either 'fixed' or 'percent'
        subtotal: The sale subtotal (used for percentage calculation)

    Returns:
        The calculated fee amount rounded to 2 decimal places

    Raises:
        ValueError: If fee_value_type is not 'fixed' or 'percent'
        ValueError: If fee_value or subtotal is negative

    Examples:
        >>> calculate_fee_amount(Decimal('30.00'), 'fixed', Decimal('500.00'))
        Decimal('30.00')
        >>> calculate_fee_amount(Decimal('5.00'), 'percent', Decimal('1000.00'))
        Decimal('50.00')
    """
    if fee_value < 0:
        raise ValueError(f"Fee value cannot be negative, got {fee_value}")
    if subtotal < 0:
        raise ValueError(f"Subtotal cannot be negative, got {subtotal}")

    if fee_value_type == "fixed":
        return round_currency(fee_value)
    elif fee_value_type == "percent":
        return round_currency(subtotal * (fee_value / Decimal(100)))
    else:
        raise ValueError(
            f"Fee value type must be 'fixed' or 'percent', got '{fee_value_type}'"
        )


def calculate_vat(
    subtotal: Decimal,
    fees_total: Decimal,
    vat_enabled: bool,
    vat_type: str,
    vat_value: Decimal,
) -> tuple[Decimal, Optional[Decimal]]:
    """
    Calculate VAT amount based on settings.

    Args:
        subtotal: Sum of all line item totals
        fees_total: Sum of all fee amounts
        vat_enabled: Whether VAT is enabled in settings
        vat_type: Either 'fixed' or 'percent'
        vat_value: VAT rate/amount from settings

    Returns:
        Tuple of (vat_amount, vat_rate)
        - vat_amount: The calculated VAT (0 if disabled)
        - vat_rate: The VAT rate from settings (None if disabled)

    Raises:
        ValueError: If vat_type is invalid or values are negative

    Examples:
        >>> calculate_vat(Decimal('500.00'), Decimal('30.00'), True, 'percent', Decimal('16.00'))
        (Decimal('84.80'), Decimal('16.00'))
        >>> calculate_vat(Decimal('500.00'), Decimal('30.00'), False, 'percent', Decimal('16.00'))
        (Decimal('0'), None)
    """
    if subtotal < 0:
        raise ValueError(f"Subtotal cannot be negative, got {subtotal}")
    if fees_total < 0:
        raise ValueError(f"Fees total cannot be negative, got {fees_total}")
    if vat_enabled and vat_value < 0:
        raise ValueError(f"VAT value cannot be negative, got {vat_value}")

    if not vat_enabled:
        return Decimal("0"), None

    taxable_amount = subtotal + fees_total

    if vat_type == "fixed":
        vat_amount = round_currency(vat_value)
    elif vat_type == "percent":
        vat_amount = round_currency(taxable_amount * (vat_value / Decimal(100)))
    else:
        raise ValueError(f"VAT type must be 'fixed' or 'percent', got '{vat_type}'")

    return vat_amount, vat_value


def calculate_sale_total(
    items: List[Dict[str, Any]],
    fees: List[Dict[str, Any]],
    vat_enabled: bool,
    vat_type: str,
    vat_value: Decimal,
) -> Dict[str, Decimal]:
    """
    Calculate the full financial breakdown for a sale.

    Args:
        items: List of line items, each with 'quantity' and 'unit_price'
        fees: List of fees, each with 'fee_value', 'fee_value_type'
        vat_enabled: Whether VAT is enabled
        vat_type: Either 'fixed' or 'percent'
        vat_value: VAT rate/amount from settings

    Returns:
        Dictionary with:
        - 'subtotal': Sum of all line totals
        - 'fees_total': Sum of all calculated fee amounts
        - 'vat_amount': Calculated VAT (0 if disabled)
        - 'vat_rate': VAT rate from settings (None if disabled)
        - 'total': subtotal + fees_total + vat_amount

    Raises:
        ValueError: If any input is invalid

    Examples:
        >>> items = [{'quantity': 2, 'unit_price': Decimal('150.00')}]
        >>> fees = [{'fee_value': Decimal('30.00'), 'fee_value_type': 'fixed'}]
        >>> calculate_sale_total(items, fees, True, 'percent', Decimal('16.00'))
        {
            'subtotal': Decimal('300.00'),
            'fees_total': Decimal('30.00'),
            'vat_amount': Decimal('52.80'),
            'vat_rate': Decimal('16.00'),
            'total': Decimal('382.80')
        }
    """
    # Calculate subtotal from line items
    subtotal = sum(
        calculate_line_total(item["quantity"], item["unit_price"]) for item in items
    )

    # Calculate fees total
    fees_total = sum(
        calculate_fee_amount(fee["fee_value"], fee["fee_value_type"], subtotal)
        for fee in fees
    )

    # Calculate VAT
    vat_amount, vat_rate = calculate_vat(
        subtotal, fees_total, vat_enabled, vat_type, vat_value
    )

    # Calculate total
    total = round_currency(subtotal + fees_total + vat_amount)

    return {
        "subtotal": round_currency(subtotal),
        "fees_total": round_currency(fees_total),
        "vat_amount": vat_amount,
        "vat_rate": vat_rate,
        "total": total,
    }
