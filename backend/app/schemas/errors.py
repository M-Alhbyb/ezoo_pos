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


# Assignment-specific errors for partner profit tracking


class AssignmentError(BaseModel):
    """Base error for assignment operations."""

    error_type: Literal[
        "assignment_not_found",
        "assignment_already_exists",
        "assignment_fulfilled",
        "insufficient_assigned_quantity",
        "invalid_assignment_operation",
    ]
    message: str
    assignment_id: Optional[UUID] = None
    product_id: Optional[UUID] = None
    partner_id: Optional[UUID] = None
    details: Optional[dict] = None

    class Config:
        json_encoders = {Decimal: float, UUID: str}


class AssignmentNotFoundError(BaseModel):
    """Raised when assignment does not exist."""

    error_type: Literal["assignment_not_found"] = "assignment_not_found"
    assignment_id: UUID
    message: str = "Product assignment not found"

    class Config:
        json_encoders = {UUID: str}


class AssignmentAlreadyExistsError(BaseModel):
    """Raised when trying to create duplicate active assignment for a product."""

    error_type: Literal["assignment_already_exists"] = "assignment_already_exists"
    product_id: UUID
    existing_assignment_id: UUID
    message: str = "Product already has an active assignment"

    class Config:
        json_encoders = {UUID: str}


class AssignmentFulfilledError(BaseModel):
    """Raised when trying to modify a fulfilled assignment."""

    error_type: Literal["assignment_fulfilled"] = "assignment_fulfilled"
    assignment_id: UUID
    message: str = "Cannot modify fulfilled assignment"

    class Config:
        json_encoders = {UUID: str}


class InsufficientAssignedQuantityError(BaseModel):
    """Raised when attempting to sell more than assigned quantity."""

    error_type: Literal["insufficient_assigned_quantity"] = (
        "insufficient_assigned_quantity"
    )
    product_id: UUID
    requested_quantity: int
    available_quantity: int
    message: str = "Insufficient assigned quantity for product"

    class Config:
        json_encoders = {UUID: str}


class WalletError(BaseModel):
    """Base error for wallet operations."""

    error_type: Literal[
        "wallet_adjustment_zero",
        "partner_not_found",
        "wallet_calculation_error",
    ]
    message: str
    partner_id: Optional[UUID] = None
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
    partner_id: UUID
    message: str = "Partner not found"

    class Config:
        json_encoders = {UUID: str}
