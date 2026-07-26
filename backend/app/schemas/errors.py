from pydantic import BaseModel
from typing import Literal, Optional
from decimal import Decimal
from uuid import UUID


class ExportError(BaseModel):
    error_type: Literal[
        "row_limit_exceeded",
        "rate_limit_exceeded",
        "invalid_date_range",
        "no_data_available",
        "generation_failed",
    ]
    message: str
    details: Optional[dict] = None

    class Config:
        json_encoders = {Decimal: float}


class RowLimitExceededError(BaseModel):
    error_type: Literal["row_limit_exceeded"] = "row_limit_exceeded"
    format: str
    requested_rows: int
    max_allowed: int
    message: str

    class Config:
        json_encoders = {Decimal: float}


class RateLimitExceededError(BaseModel):
    error_type: Literal["rate_limit_exceeded"] = "rate_limit_exceeded"
    message: str
    retry_after: int

    class Config:
        json_encoders = {Decimal: float}


class WalletError(BaseModel):
    """Base error for wallet operations."""

    error_type: Literal[
        "wallet_adjustment_zero",
        "partner_not_found",
        "wallet_calculation_error",
    ]
    message: str
    partner_id: Optional[int] = None
    details: Optional[dict] = None

    class Config:
        json_encoders = {Decimal: float, UUID: str}


class WalletAdjustmentZeroError(BaseModel):
    """Raised when wallet adjustment amount is zero."""

    error_type: Literal["wallet_adjustment_zero"] = "wallet_adjustment_zero"
    message: str = "Wallet adjustment amount cannot be zero"

    class Config:
        pass


class PartnerNotFoundError(BaseModel):
    """Raised when partner does not exist."""

    error_type: Literal["partner_not_found"] = "partner_not_found"
    partner_id: int
    message: str = "Partner not found"

    class Config:
        json_encoders = {UUID: str}
