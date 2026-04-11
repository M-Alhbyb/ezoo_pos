# Pydantic schemas

from app.schemas.product_assignment import (
    ProductAssignmentBase,
    ProductAssignmentCreate,
    ProductAssignmentUpdate,
    ProductAssignmentResponse,
    ProductAssignmentListResponse,
)
from app.schemas.partner import (
    PartnerWalletBalanceResponse,
    PartnerWalletTransactionResponse,
    PartnerWalletTransactionListResponse,
    ManualWalletAdjustmentRequest,
)

__all__ = [
    # Product Assignment schemas
    "ProductAssignmentBase",
    "ProductAssignmentCreate",
    "ProductAssignmentUpdate",
    "ProductAssignmentResponse",
    "ProductAssignmentListResponse",
    # Partner Wallet schemas
    "PartnerWalletBalanceResponse",
    "PartnerWalletTransactionResponse",
    "PartnerWalletTransactionListResponse",
    "ManualWalletAdjustmentRequest",
]
