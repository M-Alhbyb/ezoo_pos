"""Pydantic schemas for ProductAssignment."""

from decimal import Decimal

from pydantic import BaseModel, Field


class ProductAssignmentCreate(BaseModel):
    partner_id: str
    product_id: str
    assigned_quantity: int = Field(ge=1)
    share_percentage: Decimal | None = Field(None, ge=0, le=100)


class ProductAssignmentUpdate(BaseModel):
    assigned_quantity: int | None = Field(None, ge=1)
    share_percentage: Decimal | None = Field(None, ge=0, le=100)
    status: str | None = None
