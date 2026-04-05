"""
Pydantic schemas for Sale entity.

Defines request/response models for sale operations including calculation endpoint.
"""

from decimal import Decimal
from typing import Optional
from uuid import UUID
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field, field_validator


class FeeType(str, Enum):
    """Enum for fee types."""

    SHIPPING = "shipping"
    INSTALLATION = "installation"
    CUSTOM = "custom"


class FeeValueType(str, Enum):
    """Enum for fee value types."""

    FIXED = "fixed"
    PERCENT = "percent"


class SaleItemBase(BaseModel):
    """Base sale item fields."""

    product_id: UUID = Field(..., description="Product ID")
    quantity: int = Field(..., gt=0, description="Quantity (must be positive)")
    unit_price_override: Optional[Decimal] = Field(
        None, ge=0, description="Override price (uses selling_price if not provided)"
    )


class SaleItemCreate(SaleItemBase):
    """Schema for creating a sale item."""

    pass


class SaleFeeBase(BaseModel):
    """Base sale fee fields."""

    fee_type: FeeType = Field(..., description="Type of fee")
    fee_label: str = Field(
        ..., min_length=1, max_length=100, description="Display label"
    )
    fee_value_type: FeeValueType = Field(..., description="Fixed or percentage")
    fee_value: Decimal = Field(
        ..., ge=0, description="Fee value (amount or percentage)"
    )


class SaleFeeCreate(SaleFeeBase):
    """Schema for creating a sale fee."""

    pass


class SaleCreate(BaseModel):
    """Schema for creating a new sale."""

    items: list[SaleItemCreate] = Field(
        ..., min_length=1, description="Sale items (at least 1)"
    )
    fees: list[SaleFeeCreate] = Field(default_factory=list, description="Optional fees")
    payment_method_id: Optional[UUID] = Field(None, description="Optional Payment method ID")
    note: Optional[str] = Field(None, max_length=1000, description="Optional note")
    idempotency_key: Optional[str] = Field(None, description="Idempotency key to prevent double sales")


class SaleCalculationRequest(BaseModel):
    """Schema for sale calculation preview endpoint."""

    items: list[SaleItemCreate] = Field(
        ..., min_length=1, description="Sale items for calculation"
    )
    fees: list[SaleFeeCreate] = Field(
        default_factory=list, description="Optional fees for calculation"
    )


class SaleItemResponse(SaleItemBase):
    """Schema for sale item response."""

    product_name: str = Field(..., description="Product name snapshot")
    unit_price: Decimal = Field(..., description="Actual price charged")
    line_total: Decimal = Field(..., description="Line total (quantity × unit_price)")

    class Config:
        from_attributes = True


class SaleFeeResponse(SaleFeeBase):
    """Schema for sale fee response."""

    calculated_amount: Decimal = Field(..., description="Final calculated amount")

    class Config:
        from_attributes = True


class SaleBreakdown(BaseModel):
    """Schema for sale financial breakdown."""

    items: list[SaleItemResponse] = Field(..., description="Line items with totals")
    subtotal: Decimal = Field(..., description="Sum of line totals")
    fees: list[SaleFeeResponse] = Field(..., description="Fee breakdown")
    fees_total: Decimal = Field(..., description="Sum of all fees")
    vat_enabled: bool = Field(..., description="Whether VAT was applied")
    vat_rate: Optional[Decimal] = Field(None, description="VAT rate if enabled")
    vat_amount: Optional[Decimal] = Field(None, description="VAT amount if enabled")
    total: Decimal = Field(..., description="Grand total (subtotal + fees + VAT)")


class SaleResponse(BaseModel):
    """Schema for sale response."""

    id: UUID
    payment_method_id: UUID
    payment_method_name: str = Field(..., description="Payment method name")
    items: list[SaleItemResponse]
    subtotal: Decimal
    fees: list[SaleFeeResponse]
    fees_total: Decimal
    vat_enabled: bool
    vat_rate: Optional[Decimal]
    vat_amount: Optional[Decimal]
    total: Decimal
    note: Optional[str] = None
    reversed: bool = Field(default=False, description="Whether sale was reversed")
    reversal: Optional["SaleReversalInfo"] = Field(
        None, description="Reversal info if reversed"
    )
    created_at: datetime

    class Config:
        from_attributes = True


class SaleReversalInfo(BaseModel):
    """Minimal reversal info for sale response."""

    id: UUID
    reason: str
    created_at: datetime


class SaleReversalCreate(BaseModel):
    """Schema for creating a sale reversal."""

    reason: str = Field(
        ..., min_length=1, max_length=500, description="Reason for reversal"
    )


class SaleReversalResponse(BaseModel):
    """Schema for reversal response."""

    id: UUID
    original_sale_id: UUID
    reason: str
    created_at: datetime

    class Config:
        from_attributes = True


class SaleListResponse(BaseModel):
    """Schema for paginated sale list response."""

    items: list[SaleResponse]
    total: int = Field(..., description="Total number of sales")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Items per page")


class SaleListFilter(BaseModel):
    """Schema for sale list filtering."""

    start_date: Optional[datetime] = Field(
        None, description="Filter sales from this date"
    )
    end_date: Optional[datetime] = Field(
        None, description="Filter sales until this date"
    )
    payment_method_id: Optional[UUID] = Field(
        None, description="Filter by payment method"
    )
    page: int = Field(default=1, ge=1, description="Page number")
    page_size: int = Field(default=50, ge=1, le=100, description="Items per page")
