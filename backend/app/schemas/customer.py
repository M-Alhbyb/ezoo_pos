from decimal import Decimal
from typing import Optional, List
from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CustomerBase(BaseModel):
    name: str = Field(..., max_length=255)
    phone: str = Field(..., max_length=50)
    address: Optional[str] = None
    notes: Optional[str] = None
    credit_limit: Decimal = Field(default=Decimal("0.00"), ge=0)


class CustomerCreate(CustomerBase):
    pass


class CustomerUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    phone: Optional[str] = Field(None, max_length=50)
    address: Optional[str] = None
    notes: Optional[str] = None
    credit_limit: Optional[Decimal] = Field(None, ge=0)


class CustomerSummary(BaseModel):
    total_sales: Decimal
    total_payments: Decimal
    total_returns: Decimal
    balance: Decimal


class CustomerResponse(CustomerBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    
    # Optional summary fields if requested
    summary: Optional[CustomerSummary] = None
    
    model_config = ConfigDict(from_attributes=True)


class CustomerListItem(BaseModel):
    id: UUID
    name: str
    phone: str
    balance: Decimal
    credit_limit: Decimal
    
    model_config = ConfigDict(from_attributes=True)


class CustomerListResponse(BaseModel):
    customers: List[CustomerListItem]
    total: int


class LedgerEntryResponse(BaseModel):
    id: UUID
    customer_id: UUID
    type: str
    amount: Decimal
    reference_id: Optional[UUID] = None
    payment_method: Optional[str] = None
    note: Optional[str] = None
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class LedgerListResponse(BaseModel):
    entries: List[LedgerEntryResponse]
    total: int


class CustomerPaymentCreate(BaseModel):
    amount: Decimal = Field(..., gt=0)
    payment_method: str = Field(..., max_length=100)
    note: Optional[str] = None
    idempotency_key: Optional[str] = Field(None, max_length=255, description="Unique key to prevent duplicate payments")
