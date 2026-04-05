"""
Pydantic schemas for Settings and PaymentMethod entities.

Defines request/response models for system configuration and payment options.
"""

from typing import Optional
from uuid import UUID
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field, field_validator


class PaymentMethodBase(BaseModel):
    """Base payment method fields."""

    name: str = Field(
        ..., min_length=1, max_length=50, description="Payment method name"
    )
    is_active: bool = Field(default=True, description="Whether method is active")


class PaymentMethodCreate(PaymentMethodBase):
    """Schema for creating a new payment method."""

    pass


class PaymentMethodUpdate(BaseModel):
    """Schema for updating a payment method."""

    name: Optional[str] = Field(None, min_length=1, max_length=50)
    is_active: Optional[bool] = None


class PaymentMethodResponse(PaymentMethodBase):
    """Schema for payment method response."""

    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PaymentMethodListResponse(BaseModel):
    """Schema for payment method list response."""

    items: list[PaymentMethodResponse]


class SettingUpdate(BaseModel):
    """Schema for updating a system setting."""

    value: str = Field(..., description="Setting value as string")


class SettingResponse(BaseModel):
    """Schema for setting response."""

    id: UUID
    key: str
    value: str
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SettingListResponse(BaseModel):
    """Schema for settings list response."""

    items: list[SettingResponse]


class FeePresetsUpdate(BaseModel):
    """Schema for updating fee presets for a location and fee type."""

    location_id: int = Field(..., description="Store location ID")
    fee_type: str = Field(
        ..., description="Type of fee: shipping, installation, or custom"
    )
    presets: list[Decimal] = Field(
        ..., max_length=8, description="Preset amounts (max 8 values)"
    )

    @field_validator("fee_type")
    @classmethod
    def validate_fee_type(cls, v: str) -> str:
        """Validate fee_type is one of the allowed values."""
        allowed = ["shipping", "installation", "custom"]
        if v not in allowed:
            raise ValueError(f"fee_type must be one of {allowed}")
        return v

    @field_validator("presets")
    @classmethod
    def validate_presets(cls, v: list[Decimal]) -> list[Decimal]:
        """Validate no negative values, deduplicate and sort."""
        if any(p < 0 for p in v):
            raise ValueError("Preset amounts must be non-negative")
        unique_sorted = sorted(set(v))
        return unique_sorted


class FeePresetsResponse(BaseModel):
    """Schema for fee presets response."""

    fee_type: str = Field(..., description="Type of fee")
    presets: list[Decimal] = Field(..., description="Preset amounts")

    class Config:
        from_attributes = True
        json_encoders = {Decimal: float}


class FeePresetsListResponse(BaseModel):
    """Schema for all fee presets for a location."""

    presets_by_fee_type: dict[str, list[Decimal]] = Field(
        ..., description="Presets grouped by fee type"
    )

    class Config:
        from_attributes = True
        json_encoders = {Decimal: float}


class VATSettingsUpdate(BaseModel):
    """Schema for updating VAT settings."""

    enabled: bool
    type: str = Field(..., description="VAT type (fixed or percent)")
    value: Decimal = Field(..., description="VAT value")
