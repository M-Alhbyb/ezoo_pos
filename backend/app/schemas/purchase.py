from decimal import Decimal
from typing import Optional
from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, Field


class PurchaseItemBase(BaseModel):
    product_id: UUID = Field(..., description="Product ID")
    quantity: int = Field(..., gt=0, description="Quantity purchased")
    unit_cost: Decimal = Field(..., ge=0, description="Cost per unit")
    selling_price: Optional[Decimal] = Field(None, description="New selling price")


class PurchaseItemCreate(PurchaseItemBase):
    pass


class PurchaseItemResponse(PurchaseItemBase):
    id: UUID
    purchase_id: UUID
    total_cost: Decimal = Field(..., description="quantity * unit_cost")
    product_name: Optional[str] = Field(None, description="Product Name")
    product_sku: Optional[str] = Field(None, description="Product SKU")
    current_stock: Optional[int] = Field(None, description="Current stock quantity")

    class Config:
        from_attributes = True


class PurchaseCreate(BaseModel):
    supplier_id: UUID = Field(..., description="Supplier ID")
    items: list[PurchaseItemCreate] = Field(
        ..., min_length=1, description="Purchase line items"
    )


class PurchaseResponse(BaseModel):
    id: UUID
    supplier_id: UUID
    total_amount: Decimal
    created_at: datetime

    class Config:
        from_attributes = True


class PurchaseWithItems(PurchaseResponse):
    items: list[PurchaseItemResponse] = Field(..., description="Purchase line items")


class PurchaseListResponse(BaseModel):
    purchases: list[PurchaseResponse]
    total: int = Field(..., description="Total number of purchases")


class ReturnItemCreate(BaseModel):
    product_id: UUID = Field(..., description="Product ID to return")
    quantity: int = Field(..., gt=0, description="Quantity to return")


class ReturnCreate(BaseModel):
    items: list[ReturnItemCreate] = Field(
        ..., min_length=1, description="Items to return"
    )
    note: Optional[str] = Field(None, description="Return note")


class ReturnResponse(BaseModel):
    id: UUID
    purchase_id: UUID
    total_returned: Decimal
    created_at: datetime
    items: list[PurchaseItemResponse]

    class Config:
        from_attributes = True


class PaymentCreate(BaseModel):
    amount: Decimal = Field(..., gt=0, description="Payment amount")
    note: Optional[str] = Field(None, description="Payment note")


class PaymentResponse(BaseModel):
    id: UUID
    supplier_id: UUID
    type: str = "PAYMENT"
    amount: Decimal
    note: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
