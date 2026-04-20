"""
POS/Sales API Routes - REST endpoints for sale operations.

Implements all endpoints from contracts/sales-api.md
"""

from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.pos.service import SaleService
from app.schemas.sale import (
    SaleCreate,
    SaleCalculationRequest,
    SaleBreakdown,
    SaleResponse,
    SaleListFilter,
    SaleListResponse,
    SaleReversalCreate,
)

router = APIRouter(prefix="/api/sales", tags=["sales"])


def get_sale_service(db: AsyncSession = Depends(get_db)) -> SaleService:
    """Dependency injection for SaleService."""
    return SaleService(db)


@router.post(
    "/calculate",
    response_model=SaleBreakdown,
    summary="Calculate sale breakdown",
    description="Calculates financial breakdown without creating a sale record",
)
async def calculate_breakdown(
    request: SaleCalculationRequest,
    service: SaleService = Depends(get_sale_service),
):
    """
    Calculate financial breakdown for a proposed sale.

    Constitution II: Backend calculates all totals.

    Args:
        request: Sale calculation request
        service: Injected SaleService

    Returns:
        SaleBreakdown with calculated totals

    Raises:
        HTTPException 400: Validation error
        HTTPException 404: Product not found
    """
    try:
        breakdown = await service.calculate_breakdown(request)
        return breakdown
    except ValueError as e:
        error_msg = str(e)
        if "not found" in error_msg:
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
    "",
    response_model=SaleResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a sale",
    description="Creates a confirmed sale with atomic stock deduction",
)
async def create_sale(
    sale_data: SaleCreate,
    service: SaleService = Depends(get_sale_service),
):
    """
    Create a confirmed sale.

    Constitution IV: Sale is immediately confirmed and immutable.
    Constitution VI: Stock deducted atomically.

    Args:
        sale_data: Sale creation data
        service: Injected SaleService

    Returns:
        Created sale

    Raises:
        HTTPException 400: Validation error or insufficient stock
        HTTPException 404: Product or payment method not found
    """
    try:
        sale = await service.create_sale(sale_data)

        # Prepare response
        return await _prepare_sale_response(sale)
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
        elif "insufficient stock" in error_msg.lower():
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
    "",
    response_model=SaleListResponse,
    summary="List sales",
    description="Retrieves paginated list of sales with optional filters",
)
async def list_sales(
    start_date: str = Query(None, description="Filter from date (ISO format)"),
    end_date: str = Query(None, description="Filter until date (ISO format)"),
    payment_method_id: UUID = Query(None, description="Filter by payment method"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Items per page"),
    service: SaleService = Depends(get_sale_service),
):
    """
    List sales with optional filters.

    Args:
        start_date: Filter from date
        end_date: Filter until date
        payment_method_id: Filter by payment method
        page: Page number
        page_size: Items per page
        service: Injected SaleService

    Returns:
        Paginated list of sales
    """
    from datetime import datetime

    filters = SaleListFilter(
        start_date=datetime.fromisoformat(start_date) if start_date else None,
        end_date=datetime.fromisoformat(end_date) if end_date else None,
        payment_method_id=payment_method_id,
        page=page,
        page_size=page_size,
    )

    sales, total = await service.list_sales(filters)

    items = [await _prepare_sale_response(sale) for sale in sales]

    return SaleListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/{sale_id}",
    response_model=SaleResponse,
    summary="Get sale detail",
    description="Retrieves a single sale with full breakdown",
)
async def get_sale(
    sale_id: UUID,
    service: SaleService = Depends(get_sale_service),
):
    """
    Get sale detailby ID.

    Args:
        sale_id: Sale UUID
        service: Injected SaleService

    Returns:
        Sale detail with items and fees

    Raises:
        HTTPException 404: Sale not found
    """
    sale = await service.get_sale_detail(sale_id)

    if not sale:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": {
                    "code": "NOT_FOUND",
                    "message": f"Sale {sale_id} not found",
                }
            },
        )

    return await _prepare_sale_response(sale)


@router.post(
    "/{sale_id}/reverse",
    response_model=SaleResponse,
    status_code=status.HTTP_200_OK,
    summary="Reverse a sale",
    description="Creates a reversal record and restores stock",
)
async def reverse_sale(
    sale_id: UUID,
    reversal_data: SaleReversalCreate = SaleReversalCreate(),
    service: SaleService = Depends(get_sale_service),
) -> SaleResponse:
    """
    Reverse a sale.

    Constitution IV: Creates separate correction record, original sale unchanged.

    Args:
        sale_id: Sale UUID to reverse
        reversal_data: Reason for reversal
        service: Injected SaleService

    Returns:
        Reversal record as a Sale representing negative amounts

    Raises:
        HTTPException 404: Sale not found
        HTTPException 400: Sale already reversed
    """
    try:
        reversal = await service.reverse_sale(sale_id, reversal_data.reason)
        return await _prepare_sale_response(reversal)
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
        elif "already" in error_msg.lower() and "reversed" in error_msg.lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": {
                        "code": "ALREADY_REVERSED",
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


async def _prepare_sale_response(sale) -> dict:
    """
    Convert Sale instance to response dictionary.

    Args:
        sale: Sale instance with loaded relationships

    Returns:
        Dictionary ready for response
    """
    from app.schemas.sale import SaleItemResponse, SaleFeeResponse

    # Prepare items
    items = []
    for item in sale.items:
        items.append(
            SaleItemResponse(
                product_id=item.product_id,
                product_name=item.product_name,
                quantity=item.quantity,
                unit_price=item.unit_price,
                price=item.unit_price,  # Alias for tests
                base_cost=item.base_cost,
                vat_rate=item.vat_rate,
                line_total=item.line_total,
            )
        )

    # Prepare fees
    fees = []
    for fee in sale.fees:
        fees.append(
            SaleFeeResponse(
                fee_type=fee.fee_type,
                fee_label=fee.fee_label,
                fee_value_type=fee.fee_value_type,
                fee_value=fee.fee_value,
                calculated_amount=fee.calculated_amount,
            )
        )

    # Check for reversal
    reversed_sale = False
    reversal_info = None
    # reversal check would go here when we implement reversal functionality

    return {
        "id": str(sale.id),
        "payment_method_id": str(sale.payment_method_id),
        "payment_method_name": sale.payment_method.name,
        "items": items,
        "subtotal": sale.subtotal,
        "fees": fees,
        "fees_total": sale.fees_total,
        "vat_enabled": sale.vat_rate is not None,
        "vat_rate": sale.vat_rate,
        "vat_amount": sale.vat_amount,
        "vat_total": sale.vat_total,
        "vat_percentage": str(int(sale.vat_rate)) if sale.vat_rate is not None else None,
        "total": sale.total,
        "grand_total": sale.grand_total,
        "total_cost": sale.total_cost,
        "profit": sale.profit,
        "note": sale.note,
        "reason": sale.note,  # For test compatibility
        "is_reversal": sale.is_reversal,
        "original_sale_id": str(sale.original_sale_id) if sale.original_sale_id else None,
        "created_at": sale.created_at,
    }
