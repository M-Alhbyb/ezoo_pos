from decimal import Decimal
from typing import Optional
from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, Field


class SupplierBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Supplier name")
    phone: Optional[str] = Field(None, max_length=50, description="Contact phone")
    notes: Optional[str] = Field(None, description="Additional notes")


class SupplierCreate(SupplierBase):
    pass


class SupplierResponse(SupplierBase):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


class SupplierWithBalance(SupplierResponse):
    balance: Decimal = Field(
        ..., description="Derived balance (purchases - payments - returns)"
    )


class SupplierListResponse(BaseModel):
    suppliers: list[SupplierWithBalance]
    total: int = Field(..., description="Total number of suppliers")


class SupplierSummary(BaseModel):
    total_purchases: Decimal = Field(..., description="Sum of PURCHASE ledger entries")
    total_payments: Decimal = Field(..., description="Sum of PAYMENT ledger entries")
    total_returns: Decimal = Field(..., description="Sum of RETURN ledger entries")
    balance: Decimal = Field(..., description="Derived balance")


class SupplierDetailResponse(SupplierResponse):
    summary: SupplierSummary
