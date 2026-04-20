from decimal import Decimal
from typing import Optional, List
from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, Field

from app.models.project import ProjectStatus
from app.schemas.expense import ExpenseResponse


class ProjectItemBase(BaseModel):
    product_id: UUID
    quantity: int = Field(..., gt=0)


class ProjectItemCreate(ProjectItemBase):
    pass


class ProjectItemResponse(ProjectItemBase):
    id: UUID
    project_id: UUID
    product_name: str
    base_cost: Optional[Decimal] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ProjectBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    selling_price: Decimal = Field(..., ge=0)
    cost: Optional[Decimal] = Field(None, description="Cost, can be sent explicitly or computed")
    status: Optional[ProjectStatus] = Field(default=ProjectStatus.DRAFT)


class ProjectCreate(ProjectBase):
    pass


class ProjectResponse(ProjectBase):
    id: UUID
    status: ProjectStatus
    total_cost: Decimal
    total_expenses: Decimal
    profit: Decimal
    items: List[ProjectItemResponse] = Field(default_factory=list)
    expenses: List[ExpenseResponse] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
