from decimal import Decimal
from typing import Optional, List
from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, Field


class PartnerBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    share_percentage: Decimal = Field(..., ge=0, le=100)
    investment_amount: Decimal = Field(default=Decimal("0.00"), ge=0)


class PartnerCreate(PartnerBase):
    pass


class PartnerResponse(PartnerBase):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


class PartnerDistributionItem(BaseModel):
    partner_id: UUID
    name: str
    share_percentage: Decimal
    amount: Decimal


class DistributionResponse(BaseModel):
    total_profit: Decimal
    distributed_total: Decimal
    distributions: List[PartnerDistributionItem]


class PartnerDistributionResponse(BaseModel):
    id: UUID
    partner_id: UUID
    payout_amount: Decimal
    snapshot_fields: dict
    created_at: datetime
    
    class Config:
        from_attributes = True


class DistributionRequest(BaseModel):
    profit: Decimal
    memo: Optional[str] = None
