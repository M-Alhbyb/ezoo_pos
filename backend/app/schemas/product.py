"""
Pydantic schemas for Product entity.

Defines request/response models for product CRUD operations.
"""

from decimal import Decimal
from typing import Optional
from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class ProductBase(BaseModel):
    """Base product fields shared across schemas."""

    name: str = Field(..., min_length=1, max_length=200, description="Product name")
    sku: Optional[str] = Field(
        None, max_length=50, description="Stock Keeping Unit (optional)"
    )
    category_id: Optional[UUID] = Field(None, description="Optional Category ID")
    base_price: Decimal = Field(..., ge=0, description="Cost to acquire")
    selling_price: Decimal = Field(..., ge=0, description="Price to customers")
    stock_quantity: int = Field(default=0, ge=0, description="Current stock level")
    partner_id: Optional[UUID] = Field(None, description="Optional Partner ID")

    @field_validator("selling_price")
    @classmethod
    def selling_price_gte_base_price(cls, v: Decimal, info) -> Decimal:
        """Validate that selling_price >= base_price."""
        if "base_price" in info.data and v < info.data["base_price"]:
            raise ValueError(
                "selling_price must be greater than or equal to base_price"
            )
        return v


class ProductCreate(ProductBase):
    """Schema for creating a new product."""

    pass


class ProductUpdate(BaseModel):
    """Schema for updating an existing product."""

    name: Optional[str] = Field(None, min_length=1, max_length=200)
    sku: Optional[str] = Field(None, max_length=50)
    category_id: Optional[UUID] = None
    base_price: Optional[Decimal] = Field(None, ge=0)
    selling_price: Optional[Decimal] = Field(None, ge=0)
    partner_id: Optional[UUID] = None

    @field_validator("selling_price")
    @classmethod
    def validate_price_relationship(
        cls, v: Optional[Decimal], info
    ) -> Optional[Decimal]:
        """Validate selling_price >= base_price if both are provided."""
        if (
            v is not None
            and "base_price" in info.data
            and info.data["base_price"] is not None
        ):
            if v < info.data["base_price"]:
                raise ValueError(
                    "selling_price must be greater than or equal to base_price"
                )
        return v


class ProductResponse(ProductBase):
    """Schema for product response."""

    id: UUID
    category_name: Optional[str] = Field(
        None, description="Category name (joined from categories)"
    )
    category_color: Optional[str] = Field(
        None, description="Category theme color (joined from categories)"
    )
    is_active: bool = Field(..., description="Whether product is active")
    created_at: datetime
    updated_at: datetime
    partner_name: Optional[str] = Field(None, description="Partner name (joined from partners)")

    class Config:
        from_attributes = True


class ProductListResponse(BaseModel):
    """Schema for paginated product list response."""

    items: list[ProductResponse]
    total: int = Field(..., description="Total number of products")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Items per page")


class ProductSearchRequest(BaseModel):
    """Schema for product search parameters."""

    category_id: Optional[UUID] = Field(None, description="Filter by category")
    search: Optional[str] = Field(
        None, max_length=200, description="Search by name (partial) or SKU (exact)"
    )
    active_only: bool = Field(default=True, description="Only return active products")
