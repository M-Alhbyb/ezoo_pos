"""
POS Validators - Input and stock validation helpers.

Extracted from SaleService to separate validation from orchestration.
"""

from typing import List, Tuple
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from .calculations import get_product


async def validate_stock_availability(
    db: AsyncSession, items: List[Tuple[UUID, int]]
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
        product = await get_product(db, product_id)
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
