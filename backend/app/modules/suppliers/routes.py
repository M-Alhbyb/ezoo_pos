from decimal import Decimal
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.suppliers.service import SupplierService
from app.schemas.supplier import (
    SupplierCreate,
    SupplierResponse,
    SupplierWithBalance,
    SupplierListResponse,
    SupplierDetailResponse,
    SupplierSummary,
)
from app.schemas.purchase import PaymentCreate, PaymentResponse

router = APIRouter(prefix="/api/suppliers", tags=["suppliers"])


def get_supplier_service(db: AsyncSession = Depends(get_db)) -> SupplierService:
    return SupplierService(db)


@router.post("", response_model=SupplierResponse, status_code=status.HTTP_201_CREATED)
async def create_supplier(
    data: SupplierCreate,
    service: SupplierService = Depends(get_supplier_service),
):
    return await service.create_supplier(data)


@router.get("", response_model=SupplierListResponse)
async def get_suppliers(
    service: SupplierService = Depends(get_supplier_service),
):
    suppliers = await service.get_suppliers()
    supplier_list = []
    for s in suppliers:
        balance = await service.get_supplier_balance(s.id)
        supplier_list.append(
            SupplierWithBalance(
                id=s.id,
                name=s.name,
                phone=s.phone,
                notes=s.notes,
                created_at=s.created_at,
                balance=balance,
            )
        )
    return SupplierListResponse(suppliers=supplier_list, total=len(supplier_list))


@router.get("/{supplier_id}", response_model=SupplierDetailResponse)
async def get_supplier(
    supplier_id: UUID,
    service: SupplierService = Depends(get_supplier_service),
):
    supplier = await service.get_supplier(supplier_id)
    if not supplier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Supplier {supplier_id} not found",
        )

    summary = await service.get_supplier_summary(supplier_id)

    return SupplierDetailResponse(
        id=supplier.id,
        name=supplier.name,
        phone=supplier.phone,
        notes=supplier.notes,
        created_at=supplier.created_at,
        summary=summary,
    )


@router.post(
    "/{supplier_id}/payments",
    response_model=PaymentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def record_payment(
    supplier_id: UUID,
    data: PaymentCreate,
    service: SupplierService = Depends(get_supplier_service),
):
    supplier = await service.get_supplier(supplier_id)
    if not supplier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Supplier {supplier_id} not found",
        )

    if data.amount <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payment amount must be positive",
        )

    ledger = await service.record_payment(supplier_id, data.amount, data.note)

    return PaymentResponse(
        id=ledger.id,
        supplier_id=ledger.supplier_id,
        type=ledger.type,
        amount=ledger.amount,
        note=ledger.note,
        created_at=ledger.created_at,
    )
