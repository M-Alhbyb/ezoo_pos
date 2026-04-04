"""
Inventory API Routes - REST endpoints for inventory management.

Implements all endpoints for inventory tracking.
"""

from uuid import UUID
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from app.core.database import get_db
from app.modules.inventory.service import InventoryService
from app.models.inventory_log import InventoryLog


router = APIRouter(prefix="/api/inventory", tags=["inventory"])


def get_inventory_service(db: AsyncSession = Depends(get_db)) -> InventoryService:
    """Dependency injection for InventoryService."""
    return InventoryService(db)


# Request/Response schemas
class RestockRequest(BaseModel):
    """Schema for restock request."""

    product_id: UUID = Field(..., description="Product UUID")
    quantity: int = Field(..., gt=0, description="Quantity to add")


class AdjustRequest(BaseModel):
    """Schema for stock adjustment request."""

    product_id: UUID = Field(..., description="Product UUID")
    adjustment: int = Field(..., description="Stock adjustment (+/-)")
    reason: str = Field(
        ..., min_length=1, max_length=500, description="Reason for adjustment"
    )


class InventoryLogResponse(BaseModel):
    """Schema for inventory log response."""

    id: UUID
    product_id: UUID
    delta: int
    reason: str
    reference_id: Optional[UUID]
    balance_after: int
    created_at: str

    class Config:
        from_attributes = True


class InventoryLogListResponse(BaseModel):
    """Schema for paginated inventory log response."""

    items: list[InventoryLogResponse]
    total: int
    page: int
    page_size: int


class ProductStockResponse(BaseModel):
    """Schema for product stock response."""

    id: UUID
    name: str
    sku: Optional[str]
    stock_quantity: int
    is_active: bool

    class Config:
        from_attributes = True


@router.post(
    "/restock",
    response_model=InventoryLogResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Restock product",
    description="Add stock to a product",
)
async def restock_product(
    request: RestockRequest,
    service: InventoryService = Depends(get_inventory_service),
):
    """
    Restock a product.

    Args:
        request: Restock request with product_id and quantity
        service: Injected InventoryService

    Returns:
        Inventory log entry

    Raises:
        HTTPException 404: Product not found
        HTTPException 400: Invalid quantity
    """
    try:
        log = await service.restock_product(
            product_id=request.product_id,
            quantity=request.quantity,
        )

        return _prepare_log_response(log)
    except ValueError as e:
        error_msg = str(e)
        if "not found" in error_msg.lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": {
                        "code": "NOT_FOUND",
                        "message": error_msg,
                    }
                },
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": {
                        "code": "VALIDATION_ERROR",
                        "message": error_msg,
                    }
                },
            )


@router.post(
    "/adjust",
    response_model=InventoryLogResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Adjust stock",
    description="Adjust stock (positive or negative) with validation",
)
async def adjust_stock(
    request: AdjustRequest,
    service: InventoryService = Depends(get_inventory_service),
):
    """
    Adjust product stock.

    Args:
        request: Adjust request with product_id, adjustment, and reason
        service: Injected InventoryService

    Returns:
        Inventory log entry

    Raises:
        HTTPException 404: Product not found
        HTTPException 400: Adjustment would make stock negative
    """
    try:
        log = await service.adjust_stock(
            product_id=request.product_id,
            adjustment=request.adjustment,
            reason=request.reason,
        )

        return _prepare_log_response(log)
    except ValueError as e:
        error_msg = str(e)
        if "not found" in error_msg.lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": {
                        "code": "NOT_FOUND",
                        "message": error_msg,
                    }
                },
            )
        elif "negative" in error_msg.lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": {
                        "code": "INSUFFICIENT_STOCK",
                        "message": error_msg,
                    }
                },
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": {
                        "code": "VALIDATION_ERROR",
                        "message": error_msg,
                    }
                },
            )


@router.get(
    "/log/{product_id}",
    response_model=InventoryLogListResponse,
    summary="Get inventory log",
    description="Get inventory log for a product with pagination",
)
async def get_inventory_log(
    product_id: UUID,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Items per page"),
    service: InventoryService = Depends(get_inventory_service),
):
    """
    Get inventory log for a product.

    Args:
        product_id: Product UUID
        page: Page number
        page_size: Items per page
        service: Injected InventoryService

    Returns:
        Paginated list of inventory log entries
    """
    logs, total = await service.get_inventory_log(
        product_id=product_id,
        page=page,
        page_size=page_size,
    )

    items = [_prepare_log_response(log) for log in logs]

    return InventoryLogListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/low-stock",
    response_model=list[ProductStockResponse],
    summary="Get low stock products",
    description="Get products with stock below threshold",
)
async def get_low_stock_products(
    threshold: int = Query(10, ge=0, description="Stock threshold"),
    service: InventoryService = Depends(get_inventory_service),
):
    """
    Get products with low stock.

    Args:
        threshold: Stock level threshold
        service: Injected InventoryService

    Returns:
        List of low-stock products
    """
    products = await service.get_low_stock_products(threshold=threshold)

    return [
        ProductStockResponse(
            id=product.id,
            name=product.name,
            sku=product.sku,
            stock_quantity=product.stock_quantity,
            is_active=product.is_active,
        )
        for product in products
    ]


def _prepare_log_response(log: InventoryLog) -> InventoryLogResponse:
    """Convert InventoryLog to response schema."""
    return InventoryLogResponse(
        id=log.id,
        product_id=log.product_id,
        delta=log.delta,
        reason=log.reason,
        reference_id=log.reference_id,
        balance_after=log.balance_after,
        created_at=log.created_at.isoformat() if log.created_at else None,
    )
