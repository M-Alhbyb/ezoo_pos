"""
Pydantic schemas for Category entity.

Defines request/response models for category CRUD operations.
"""

from typing import Optional
from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, Field


class CategoryBase(BaseModel):
    """Base category fields shared across schemas."""

    name: str = Field(..., min_length=1, max_length=100, description="Category name")


class CategoryCreate(CategoryBase):
    """Schema for creating a new category."""

    pass


class CategoryUpdate(BaseModel):
    """Schema for updating an existing category."""

    name: Optional[str] = Field(
        None, min_length=1, max_length=100, description="Category name"
    )


class CategoryResponse(CategoryBase):
    """Schema for category response."""

    id: UUID
    product_count: Optional[int] = Field(
        None, description="Number of active products in this category"
    )
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CategoryListResponse(BaseModel):
    """Schema for category list response."""

    items: list[CategoryResponse]
