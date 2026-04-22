# Pydantic schemas

from app.schemas.partner import (
    PartnerWalletBalanceResponse,
    PartnerWalletTransactionResponse,
    PartnerWalletTransactionListResponse,
    ManualWalletAdjustmentRequest,
)

from app.schemas.supplier import (
    SupplierCreate,
    SupplierResponse,
    SupplierWithBalance,
    SupplierListResponse,
    SupplierSummary,
    SupplierDetailResponse,
)

from app.schemas.purchase import (
    PurchaseCreate,
    PurchaseResponse,
    PurchaseWithItems,
    PurchaseListResponse,
    PurchaseItemCreate,
    PurchaseItemResponse,
    ReturnCreate,
    ReturnResponse,
    PaymentCreate,
    PaymentResponse,
)

from app.schemas.supplier_ledger import (
    LedgerEntryResponse,
    SupplierStatementResponse,
    SupplierSummaryReportItem,
    SupplierSummaryReportResponse,
)

__all__ = [
    # Partner Wallet schemas
    "PartnerWalletBalanceResponse",
    "PartnerWalletTransactionResponse",
    "PartnerWalletTransactionListResponse",
    "ManualWalletAdjustmentRequest",
    # Supplier schemas
    "SupplierCreate",
    "SupplierResponse",
    "SupplierWithBalance",
    "SupplierListResponse",
    "SupplierSummary",
    "SupplierDetailResponse",
    # Purchase schemas
    "PurchaseCreate",
    "PurchaseResponse",
    "PurchaseWithItems",
    "PurchaseListResponse",
    "PurchaseItemCreate",
    "PurchaseItemResponse",
    "ReturnCreate",
    "ReturnResponse",
    "PaymentCreate",
    "PaymentResponse",
    # Ledger schemas
    "LedgerEntryResponse",
    "SupplierStatementResponse",
    "SupplierSummaryReportItem",
    "SupplierSummaryReportResponse",
]
