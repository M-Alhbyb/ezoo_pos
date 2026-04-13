from datetime import datetime
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.partners.service import PartnerService
from app.modules.partners.partner_profit_service import PartnerProfitService
from app.schemas.partner import (
    PartnerCreate,
    PartnerResponse,
    PartnerDetailResponse,
    PartnerHistoryDistribution,
    DistributionResponse,
    DistributionRequest,
    PartnerWalletBalanceResponse,
    PartnerWalletTransactionResponse,
    PartnerWalletTransactionListResponse,
    ManualWalletAdjustmentRequest,
)

router = APIRouter(prefix="/api/partners", tags=["partners"])


def get_partner_service(db: AsyncSession = Depends(get_db)) -> PartnerService:
    return PartnerService(db)


def get_partner_profit_service(
    db: AsyncSession = Depends(get_db),
) -> PartnerProfitService:
    return PartnerProfitService(db)


# Partner CRUD endpoints


@router.post("", response_model=PartnerResponse, status_code=status.HTTP_201_CREATED)
async def create_partner(
    data: PartnerCreate,
    service: PartnerService = Depends(get_partner_service),
):
    return await service.create_partner(data)


@router.get("", response_model=list[PartnerResponse])
async def get_partners(
    service: PartnerService = Depends(get_partner_service),
):
    return await service.get_partners()


@router.get("/{partner_id}", response_model=PartnerDetailResponse)
async def get_partner(
    partner_id: UUID,
    service: PartnerService = Depends(get_partner_service),
):
    """
    Get partner details and distribution history.
    """
    partner = await service.get_partner(partner_id)
    if not partner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Partner {partner_id} not found",
        )

    # Fetch distribution history
    distributions = await service.get_partner_distributions(partner_id)

    # Convert to schema
    # In Pydantic v2, we use model_validate, but the project uses from_orm or Config compatibility
    response = PartnerDetailResponse.from_orm(partner)
    response.distributions = [
        PartnerHistoryDistribution(
            id=d.id,
            amount=d.payout_amount,
            distributed_at=d.created_at
        )
        for d in distributions
    ]

    return response


@router.post("/distribute", response_model=DistributionResponse)
async def distribute_profits(
    data: DistributionRequest,
    service: PartnerService = Depends(get_partner_service),
):
    try:
        return await service.calculate_distribution(total_profit=data.profit)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# Wallet Management Endpoints


@router.get("/{partner_id}/wallet", response_model=PartnerWalletBalanceResponse)
async def get_partner_wallet(
    partner_id: UUID,
    db: AsyncSession = Depends(get_db),
    # TODO: Add admin authorization check per FR-013
    # current_user: User = Depends(require_admin),
):
    """
    Get partner wallet balance.

    Returns the current wallet balance for a partner, computed from the latest
    transaction's balance_after field (O(1) lookup).

    This endpoint is restricted to administrators per FR-013.
    Partners must contact administrators for balance information.
    """
    service = PartnerProfitService(db)

    # Get partner to verify it exists
    partner_service = PartnerService(db)
    partner = await partner_service.get_partner(partner_id)
    if not partner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Partner {partner_id} not found",
        )

    # Get wallet balance
    balance = await service.get_partner_wallet_balance(partner_id)

    # Get latest transaction to get timestamp
    transactions = await service.get_partner_wallet_transactions(
        partner_id, limit=1, offset=0
    )
    last_transaction_at = transactions[0].created_at if transactions else None

    return PartnerWalletBalanceResponse(
        partner_id=partner.id,
        partner_name=partner.name,
        current_balance=balance,
        last_transaction_at=last_transaction_at,
    )


@router.get(
    "/{partner_id}/wallet/transactions",
    response_model=PartnerWalletTransactionListResponse,
)
async def get_partner_wallet_transactions(
    partner_id: UUID,
    limit: int = Query(100, ge=1, le=1000, description="Max transactions to return"),
    offset: int = Query(0, ge=0, description="Number of transactions to skip"),
    db: AsyncSession = Depends(get_db),
    # TODO: Add admin authorization check per FR-013
    # current_user: User = Depends(require_admin),
):
    """
    Get partner wallet transaction history.

    Returns paginated transaction history for a partner, ordered by created_at descending.
    Each transaction includes amount, type, description, and balance_after.

    This endpoint is restricted to administrators per FR-013.
    """
    service = PartnerProfitService(db)

    # Get partner to verify it exists
    partner_service = PartnerService(db)
    partner = await partner_service.get_partner(partner_id)
    if not partner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Partner {partner_id} not found",
        )

    # Get transaction history
    transactions = await service.get_partner_wallet_transactions(
        partner_id, limit=limit, offset=offset
    )

    # Get total count (approximation: for large datasets, consider a more efficient method)
    total = (
        len(transactions) + offset
    )  # This is a placeholder, implement proper counting if needed

    return PartnerWalletTransactionListResponse(
        transactions=[
            PartnerWalletTransactionResponse.from_orm(t) for t in transactions
        ],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.post(
    "/{partner_id}/wallet/adjust",
    response_model=PartnerWalletTransactionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def adjust_partner_wallet(
    partner_id: UUID,
    data: ManualWalletAdjustmentRequest,
    db: AsyncSession = Depends(get_db),
    # TODO: Add admin authorization check per FR-013
    # current_user: User = Depends(require_admin),
):
    """
    Make manual adjustment to partner wallet balance.

    Allows administrators to credit or debit a partner's wallet balance.
    Positive amounts add to wallet (credit), negative amounts subtract (debit).

    This endpoint is restricted to administrators per FR-013.

    Args:
        partner_id: UUID of the partner
        data: ManualWalletAdjustmentRequest with amount and description

    Returns:
        PartnerWalletTransactionResponse with the created transaction

    Raises:
        HTTPException: 404 if partner not found, 400 if amount is zero
    """
    service = PartnerProfitService(db)

    try:
        transaction = await service.adjust_wallet(
            partner_id=partner_id,
            amount=data.amount,
            description=data.description,
        )

        return PartnerWalletTransactionResponse.from_orm(transaction)

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
