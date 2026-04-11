# Pydantic Schemas: Partner Profit Tracking

**Feature**: 005-partner-profit-tracking
**Date**: 2026-04-08

## Overview

Pydantic schema definitions for partner profit tracking APIs, following existing patterns from `app/schemas/partner.py`.

---

## Product Assignment Schemas

### ProductAssignmentBase

```python
from decimal import Decimal
from typing import Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field, field_validator

class ProductAssignmentBase(BaseModel):
    partner_id: UUID = Field(..., description="Partner receiving profit share")
    product_id: UUID = Field(..., description="Product assigned to partner")
    assigned_quantity: int = Field(..., ge=1, description="Quantity assigned")
    share_percentage: Optional[Decimal] = Field(
        None, 
        ge=0, 
        le=100,
        description="Profit share override (uses partner default if None)"
    )
```

### ProductAssignmentCreate

```python
class ProductAssignmentCreate(ProductAssignmentBase):
    """Schema for creating a new product assignment."""
    
    @field_validator('share_percentage')
    @classmethod
    def validate_share_percentage(cls, v):
        if v is not None and v < 0:
            raise ValueError('Share percentage must be >= 0')
        if v is not None and v > 100:
            raise ValueError('Share percentage must be <= 100')
        return v
```

### ProductAssignmentUpdate

```python
class ProductAssignmentUpdate(BaseModel):
    """Schema for updating an existing product assignment."""
    
    assigned_quantity: Optional[int] = Field(None, ge=1)
    share_percentage: Optional[Decimal] = Field(None, ge=0, le=100)
    
    @field_validator('assigned_quantity')
    @classmethod
    def validate_assigned_quantity(cls, v):
        if v is not None and v < 1:
            raise ValueError('Assigned quantity must be >= 1')
        return v
```

### ProductAssignmentResponse

```python
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
```

### ProductAssignmentListResponse

```python
class ProductAssignmentListResponse(BaseModel):
    """Schema for paginated assignment list."""
    
    assignments: list[ProductAssignmentResponse]
    total: int
    limit: int
    offset: int
```

---

## Partner Wallet Schemas

### PartnerWalletBalanceResponse

```python
class PartnerWalletBalanceResponse(BaseModel):
    """Schema for partner wallet balance."""
    
    partner_id: UUID
    partner_name: str
    current_balance: Decimal = Field(
        ...,
        description="Current wallet balance computed from latest transaction"
    )
    last_transaction_at: Optional[datetime] = Field(
        None,
        description="Timestamp of most recent transaction"
    )
    
    class Config:
        from_attributes = True
        json_encoders = {
            Decimal: float
        }
```

### PartnerWalletTransactionResponse

```python
class PartnerWalletTransactionResponse(BaseModel):
    """Schema for individual wallet transaction."""
    
    id: UUID
    partner_id: UUID
    amount: Decimal = Field(..., description="Credit (+) or debit (-)")
    transaction_type: str = Field(
        ...,
        description="'sale_profit' or 'manual_adjustment'"
    )
    reference_id: Optional[UUID] = Field(
        None,
        description="sale_id for sale_profit, null for manual"
    )
    reference_type: Optional[str] = Field(
        None,
        description="'sale' or 'manual'"
    )
    description: Optional[str] = Field(
        None,
        description="Human-readable description"
    )
    balance_after: Decimal = Field(
        ...,
        description="Wallet balance after this transaction"
    )
    created_at: datetime
    
    class Config:
        from_attributes = True
        json_encoders = {
            Decimal: float
        }
```

### PartnerWalletTransactionListResponse

```python
class PartnerWalletTransactionListResponse(BaseModel):
    """Schema for paginated transaction history."""
    
    transactions: list[PartnerWalletTransactionResponse]
    total: int
    limit: int
    offset: int
```

### ManualWalletAdjustmentRequest

```python
class ManualWalletAdjustmentRequest(BaseModel):
    """Schema for admin manual wallet adjustment."""
    
    amount: Decimal = Field(
        ...,
        description="Credit (+) or debit (-), cannot be 0"
    )
    description: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="Reason for adjustment"
    )
    
    @field_validator('amount')
    @classmethod
    def validate_amount_nonzero(cls, v):
        if v == 0:
            raise ValueError('Amount cannot be zero')
        return v
```

---

## Extended Product Schema

### ProductResponse (Extended)

```python
class ProductResponse(BaseModel):
    """Extended product response with assignment information."""
    
    id: UUID
    name: str
    sku: Optional[str]
    category_id: UUID
    base_price: Decimal
    selling_price: Decimal
    stock_quantity: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    # NEW: Assignment information
    assignment: Optional[ProductAssignmentResponse] = Field(
        None,
        description="Active assignment for this product, null if unassigned"
    )
    
    class Config:
        from_attributes = True
        json_encoders = {
            Decimal: float
        }
```

---

## Error Schemas

These follow the existing error response pattern in `app/schemas/errors.py`.

### ValidationError

```python
from typing import Optional

class FieldError(BaseModel):
    field: str
    message: str

class ErrorResponse(BaseModel):
    detail: str
    errors: Optional[list[FieldError]] = None
```

---

## Schema Usage Examples

### Creating an Assignment

**Request**:
```python
assignment_data = ProductAssignmentCreate(
    partner_id=UUID("123e4567-e89b-12d3-a456-426614174000"),
    product_id=UUID("987e6543-e21b-43d3-b456-426614174111"),
    assigned_quantity=10,
    share_percentage=Decimal("15.00")
)
```

**Response**:
```python
response = ProductAssignmentResponse(
    id=UUID("abc123..."),
    partner_id=UUID("123e4567..."),
    partner_name="Solar Partner Inc",
    product_id=UUID("987e6543..."),
    product_name="Solar Panel 100W",
    assigned_quantity=10,
    remaining_quantity=10,
    share_percentage=Decimal("15.00"),
    status="active",
    created_at=datetime.now(timezone.utc),
    updated_at=datetime.now(timezone.utc),
    fulfilled_at=None
)
```

### Adjusting Wallet

**Request**:
```python
adjustment = ManualWalletAdjustmentRequest(
    amount=Decimal("-50.00"),
    description="Payout for March 2026"
)
```

**Response**:
```python
response = PartnerWalletTransactionResponse(
    id=UUID("txn123..."),
    partner_id=UUID("123e4567..."),
    amount=Decimal("-50.00"),
    transaction_type="manual_adjustment",
    reference_id=None,
    reference_type=None,
    description="Payout for March 2026",
    balance_after=Decimal("1473.45"),
    created_at=datetime.now(timezone.utc)
)
```

---

## Constitution Compliance

| Principle | Schema Implementation |
|-----------|----------------------|
| **I. Financial Accuracy** | All monetary values as Decimal, serialized to float |
| **VI. Data Integrity** | Field validators enforce non-negative quantities |
| **VII. Backend Authority** | All validation in Pydantic + service layer |
| **VIII. Input Validation** | Schema validators for all inputs |

---

## Decimal Serialization Pattern

Following the pattern from AGENTS.md (lesson learned from 002-quick-fee-buttons):

```python
class Config:
    from_attributes = True
    json_encoders = {
        Decimal: float  # Ensures proper JSON serialization
    }
```

This ensures:
- Backend stores as DECIMAL (exact)
- API sends as float (JSON-compatible)
- Frontend receives as number (not string)
- No precision loss for monetary values