from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.purchases.service import PurchaseService
from app.schemas.purchase import (
    PurchaseCreate,
    PurchaseResponse,
    PurchaseWithItems,
    PurchaseItemResponse,
    PurchaseListResponse,
    ReturnCreate,
    ReturnResponse,
    PaymentCreate,
    PaymentResponse,
)

router = APIRouter(prefix="/api/purchases", tags=["purchases"])


def get_purchase_service(db: AsyncSession = Depends(get_db)) -> PurchaseService:
    return PurchaseService(db)


@router.post("", response_model=PurchaseResponse, status_code=status.HTTP_201_CREATED)
async def create_purchase(
    data: PurchaseCreate,
    service: PurchaseService = Depends(get_purchase_service),
):
    try:
        return await service.create_purchase(data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("", response_model=PurchaseListResponse)
async def get_purchases(
    supplier_id: Optional[UUID] = Query(None, description="Filter by supplier"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    service: PurchaseService = Depends(get_purchase_service),
):
    purchases = await service.get_purchases(
        supplier_id=supplier_id, limit=limit, offset=offset
    )
    return PurchaseListResponse(purchases=purchases, total=len(purchases))


@router.get("/{purchase_id}", response_model=PurchaseWithItems)
async def get_purchase(
    purchase_id: UUID,
    service: PurchaseService = Depends(get_purchase_service),
):
    purchase = await service.get_purchase(purchase_id)
    if not purchase:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Purchase {purchase_id} not found",
        )

    items = await service.get_purchase_items(purchase_id)

    return PurchaseWithItems(
        id=purchase.id,
        supplier_id=purchase.supplier_id,
        total_amount=purchase.total_amount,
        created_at=purchase.created_at,
        items=[
            PurchaseItemResponse(
                id=item.id,
                purchase_id=item.purchase_id,
                product_id=item.product_id,
                quantity=item.quantity,
                unit_cost=item.unit_cost,
                total_cost=item.total_cost,
                product_name=item.product_name,
                product_sku=item.product_sku,
                current_stock=item.current_stock,
            )
            for item in items
        ],
    )


@router.post(
    "/{purchase_id}/return",
    response_model=ReturnResponse,
    status_code=status.HTTP_201_CREATED,
)
async def return_items(
    purchase_id: UUID,
    data: ReturnCreate,
    service: PurchaseService = Depends(get_purchase_service),
):
    purchase = await service.get_purchase(purchase_id)
    if not purchase:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Purchase {purchase_id} not found",
        )

    items_data = [
        {"product_id": item.product_id, "quantity": item.quantity}
        for item in data.items
    ]

    try:
        purchase, return_items_list = await service.return_items(
            purchase_id=purchase_id,
            items=items_data,
            note=data.note,
        )

        total_returned = sum(item["total_cost"] for item in return_items_list)

        return ReturnResponse(
            id=purchase.id,
            purchase_id=purchase.id,
            total_returned=total_returned,
            created_at=purchase.created_at,
            items=[
                PurchaseItemResponse(
                    id=UUID("00000000-0000-0000-0000-000000000000"),
                    purchase_id=purchase.id,
                    product_id=item["product_id"],
                    quantity=item["quantity"],
                    unit_cost=item["unit_cost"],
                    total_cost=item["total_cost"],
                    product_name=item.get("product_name"),
                    product_sku=item.get("product_sku"),
                    current_stock=item.get("current_stock"),
                )
                for item in return_items_list
            ],
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e)
        )
