"""
Product Assignment Schemas - Pydantic models for API validation.

Constitution compliance:
- VIII (Input Validation): All endpoints validate against schemas
- I (Financial Accuracy): DECIMAL serialized to float for JSON compatibility
"""

from decimal import Decimal
from typing import Optional, List
from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class ProductAssignmentBase(BaseModel):
    """Base schema for product assignment."""

    partner_id: UUID = Field(..., description="Partner receiving profit share")
    product_id: UUID = Field(..., description="Product assigned to partner")
    assigned_quantity: int = Field(..., ge=1, description="Quantity assigned")
    share_percentage: Optional[Decimal] = Field(
        None,
        ge=0,
        le=100,
        description="Profit share override (uses partner default if None)",
    )

    @field_validator("assigned_quantity")
    @classmethod
    def validate_assigned_quantity(cls, v):
        if v < 1:
            raise ValueError("Assigned quantity must be >= 1")
        return v

    @field_validator("share_percentage")
    @classmethod
    def validate_share_percentage(cls, v):
        if v is not None:
            if v < 0:
                raise ValueError("Share percentage must be >= 0")
            if v > 100:
                raise ValueError("Share percentage must be <= 100")
        return v


class ProductAssignmentCreate(ProductAssignmentBase):
    """Schema for creating a new product assignment."""

    pass


class ProductAssignmentUpdate(BaseModel):
    """Schema for updating an existing product assignment."""

    assigned_quantity: Optional[int] = Field(None, ge=1)
    share_percentage: Optional[Decimal] = Field(None, ge=0, le=100)

    @field_validator("assigned_quantity")
    @classmethod
    def validate_assigned_quantity(cls, v):
        if v is not None and v < 1:
            raise ValueError("Assigned quantity must be >= 1")
        return v

    @field_validator("share_percentage")
    @classmethod
    def validate_share_percentage(cls, v):
        if v is not None:
            if v < 0:
                raise ValueError("Share percentage must be >= 0")
            if v > 100:
                raise ValueError("Share percentage must be <= 100")
        return v


class ProductAssignmentResponse(BaseModel):
    """Schema for product assignment API responses."""

    id: UUID
    partner_id: UUID
    partner_name: str = Field(..., description="Partner name for display")
    product_id: UUID
    product_name: str = Field(..., description="Product name for display")
    assigned_quantity: int
    remaining_quantity: int
    share_percentage: Decimal
    status: str = Field(..., description="'active' or 'fulfilled'")
    created_at: datetime
    updated_at: datetime
    fulfilled_at: Optional[datetime] = None

    class Config:
        from_attributes = True
        json_encoders = {
            Decimal: float  # Ensure proper JSON serialization
        }


class ProductAssignmentListResponse(BaseModel):
    """Schema for paginated assignment list."""

    assignments: List[ProductAssignmentResponse]
    total: int
    limit: int
    offset: int
