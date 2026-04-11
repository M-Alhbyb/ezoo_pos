from decimal import Decimal
from typing import Optional, List
from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, Field, field_validator


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


class PartnerHistoryDistribution(BaseModel):
    id: UUID
    amount: Decimal
    distributed_at: datetime

    class Config:
        from_attributes = True


class PartnerDetailResponse(PartnerResponse):
    distributions: List[PartnerHistoryDistribution] = []


class DistributionRequest(BaseModel):
    profit: Decimal
    memo: Optional[str] = None


# Wallet-related schemas for partner profit tracking


class PartnerWalletBalanceResponse(BaseModel):
    """Schema for partner wallet balance."""

    partner_id: UUID
    partner_name: str
    current_balance: Decimal = Field(
        ..., description="Current wallet balance computed from latest transaction"
    )
    last_transaction_at: Optional[datetime] = Field(
        None, description="Timestamp of most recent transaction"
    )

    class Config:
        from_attributes = True
        json_encoders = {Decimal: float}


class PartnerWalletTransactionResponse(BaseModel):
    """Schema for individual wallet transaction."""

    id: UUID
    partner_id: UUID
    amount: Decimal = Field(..., description="Credit (+) or debit (-)")
    transaction_type: str = Field(
        ..., description="'sale_profit' or 'manual_adjustment'"
    )
    reference_id: Optional[UUID] = Field(
        None, description="sale_id for sale_profit, null for manual"
    )
    reference_type: Optional[str] = Field(None, description="'sale' or 'manual'")
    description: Optional[str] = Field(None, description="Human-readable description")
    balance_after: Decimal = Field(
        ..., description="Wallet balance after this transaction"
    )
    created_at: datetime

    class Config:
        from_attributes = True
        json_encoders = {Decimal: float}


class PartnerWalletTransactionListResponse(BaseModel):
    """Schema for paginated transaction history."""

    transactions: List[PartnerWalletTransactionResponse]
    total: int
    limit: int
    offset: int


class ManualWalletAdjustmentRequest(BaseModel):
    """Schema for admin manual wallet adjustment."""

    amount: Decimal = Field(..., description="Credit (+) or debit (-), cannot be 0")
    description: str = Field(
        ..., min_length=1, max_length=500, description="Reason for adjustment"
    )

    @field_validator("amount")
    @classmethod
    def validate_amount_nonzero(cls, v):
        if v == 0:
            raise ValueError("Amount cannot be zero")
        return v
