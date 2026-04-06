from pydantic import BaseModel
from typing import Literal, Optional
from decimal import Decimal


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
