from decimal import Decimal
from typing import Optional
from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, Field

from app.models.expense import ExpenseType


class ExpenseBase(BaseModel):
    project_id: Optional[UUID] = None
    name: Optional[str] = None
    type: ExpenseType
    value: Decimal = Field(..., ge=0)


class ExpenseCreate(ExpenseBase):
    pass


class ExpenseResponse(ExpenseBase):
    id: UUID
    calculated_amount: Optional[Decimal] = None
    created_at: datetime

    class Config:
        from_attributes = True
