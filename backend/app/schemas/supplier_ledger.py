from decimal import Decimal
from typing import Optional
from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, Field


class LedgerEntryBase(BaseModel):
    type: str = Field(..., description="PURCHASE, PAYMENT, or RETURN")
    amount: Decimal = Field(..., gt=0, description="Always positive")
    reference_id: Optional[UUID] = Field(
        None, description="Links to Purchase for PURCHASE/RETURN"
    )
    note: Optional[str] = Field(None, description="Transaction note")


class LedgerEntryResponse(LedgerEntryBase):
    id: UUID
    supplier_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


class SupplierStatementResponse(BaseModel):
    supplier: dict
    summary: dict
    ledger: list[LedgerEntryResponse]


class SupplierSummaryReportItem(BaseModel):
    id: UUID
    name: str
    total_purchases: Decimal
    total_payments: Decimal
    total_returns: Decimal
    balance: Decimal


class SupplierSummaryReportResponse(BaseModel):
    suppliers: list[SupplierSummaryReportItem]
