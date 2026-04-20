"""
Pydantic schemas for Inventory entity.

Defines request/response models for inventory management operations.
"""

from decimal import Decimal
from typing import Optional
from uuid import UUID
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class InventoryLogReason(str, Enum):
    """Enum for inventory log reasons."""

    SALE = "sale"
    REVERSAL = "reversal"
    RESTOCK = "restock"
    ADJUSTMENT = "adjustment"


class InventoryRestock(BaseModel):
    """Schema for restocking a product."""

    product_id: UUID = Field(..., description="Product ID")
    quantity: int = Field(..., gt=0, description="Quantity to add (must be positive)")
    note: Optional[str] = Field(None, max_length=500, description="Optional note")


class InventoryAdjust(BaseModel):
    """Schema for manual stock adjustment."""

    product_id: UUID = Field(..., description="Product ID")
    delta: int = Field(..., description="Quantity change (positive or negative)")
    reason: str = Field(
        ..., min_length=1, max_length=100, description="Reason for adjustment"
    )
    note: Optional[str] = Field(None, max_length=500, description="Optional note")


class InventoryLogResponse(BaseModel):
    """Schema for inventory log entry response."""

    id: UUID
    product_id: UUID
    delta: int = Field(..., description="Quantity change (+/-)")
    reason: InventoryLogReason = Field(..., description="Reason for change")
    note: Optional[str] = Field(None, description="Optional note")
    reference_id: Optional[UUID] = Field(None, description="Reference to source record")
    balance_after: int = Field(..., description="Stock level after change")
    created_at: datetime

    class Config:
        from_attributes = True


class InventoryLogListResponse(BaseModel):
    """Schema for paginated inventory log list."""

    items: list[InventoryLogResponse]
    total: int = Field(..., description="Total number of log entries")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Items per page")


class InventoryLogFilter(BaseModel):
    """Schema for inventory log filtering."""

    product_id: UUID = Field(..., description="Product ID to filter by")
    start_date: Optional[datetime] = Field(None, description="Filter from this date")
    end_date: Optional[datetime] = Field(None, description="Filter until this date")
    page: int = Field(default=1, ge=1, description="Page number")
    page_size: int = Field(default=50, ge=1, le=100, description="Items per page")


class LowStockProductResponse(BaseModel):
    """Schema for low stock product."""

    product_id: UUID
    product_name: str
    sku: Optional[str] = Field(None, description="SKU if available")
    current_stock: int = Field(..., description="Current stock level")
    category_name: Optional[str] = Field(None, description="Category name")

    class Config:
        from_attributes = True


class LowStockListResponse(BaseModel):
    """Schema for paginated low stock products list."""

    threshold: int = Field(..., description="Stock threshold used")
    items: list[LowStockProductResponse]
    total: int = Field(..., description="Total number of low stock products")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Items per page")


class ProductStockResponse(BaseModel):
    """Schema for product stock info (for WebSocket updates)."""

    product_id: UUID
    stock_quantity: int = Field(..., description="Current stock level")

    class Config:
        from_attributes = True
