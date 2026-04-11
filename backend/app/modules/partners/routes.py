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
from app.schemas.product_assignment import (
    ProductAssignmentCreate,
    ProductAssignmentUpdate,
    ProductAssignmentResponse,
    ProductAssignmentListResponse,
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


# Product Assignment endpoints


@router.post(
    "/assignments",
    response_model=ProductAssignmentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_assignment(
    data: ProductAssignmentCreate,
    service: PartnerProfitService = Depends(get_partner_profit_service),
):
    """
    Create a new product assignment.

    Assigns a specific quantity of a product to a partner for profit sharing.

    Business Rules:
    - Only one active assignment per product
    - share_percentage defaults to partner's default if not specified
    """
    try:
        assignment = await service.create_assignment(data)

        # Fetch partner and product names for response
        # Note: This will be handled by eager loading or joins in production
        from app.models.partner import Partner
        from app.models.product import Product
        from sqlalchemy.orm import selectinload

        # Create response with names
        # In real implementation, we'd use joins or separate queries
        response = ProductAssignmentResponse(
            id=assignment.id,
            partner_id=assignment.partner_id,
            partner_name="Partner",  # Will be fetched in real implementation
            product_id=assignment.product_id,
            product_name="Product",  # Will be fetched in real implementation
            assigned_quantity=assignment.assigned_quantity,
            remaining_quantity=assignment.remaining_quantity,
            share_percentage=assignment.share_percentage,
            status=assignment.status,
            created_at=assignment.created_at,
            updated_at=assignment.updated_at,
            fulfilled_at=assignment.fulfilled_at,
        )

        return response
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.get("/assignments", response_model=ProductAssignmentListResponse)
async def list_assignments(
    partner_id: Optional[UUID] = Query(None, description="Filter by partner ID"),
    product_id: Optional[UUID] = Query(None, description="Filter by product ID"),
    status: Optional[str] = Query(
        None, description="Filter by status ('active' or 'fulfilled')"
    ),
    limit: int = Query(50, ge=1, le=100, description="Max results"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    service: PartnerProfitService = Depends(get_partner_profit_service),
):
    """
    List all product assignments with optional filters.

    Supports filtering by:
    - partner_id: Show assignments for a specific partner
    - product_id: Show assignments for a specific product
    - status: Show only 'active' or 'fulfilled' assignments
    """
    assignments = await service.list_assignments(
        partner_id=partner_id,
        product_id=product_id,
        status=status,
    )

    # Apply pagination
    total = len(assignments)
    paginated = assignments[offset : offset + limit]

    # Convert to response format
    # In real implementation, we'd fetch partner/product names via joins
    assignment_responses = [
        ProductAssignmentResponse(
            id=a.id,
            partner_id=a.partner_id,
            partner_name="Partner",  # TODO: Fetch from database
            product_id=a.product_id,
            product_name="Product",  # TODO: Fetch from database
            assigned_quantity=a.assigned_quantity,
            remaining_quantity=a.remaining_quantity,
            share_percentage=a.share_percentage,
            status=a.status,
            created_at=a.created_at,
            updated_at=a.updated_at,
            fulfilled_at=a.fulfilled_at,
        )
        for a in paginated
    ]

    return ProductAssignmentListResponse(
        assignments=assignment_responses,
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/assignments/{assignment_id}", response_model=ProductAssignmentResponse)
async def get_assignment(
    assignment_id: UUID,
    service: PartnerProfitService = Depends(get_partner_profit_service),
):
    """
    Get a specific product assignment by ID.
    """
    assignment = await service.get_assignment(assignment_id)

    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Assignment {assignment_id} not found",
        )

    return ProductAssignmentResponse(
        id=assignment.id,
        partner_id=assignment.partner_id,
        partner_name="Partner",  # TODO: Fetch from database
        product_id=assignment.product_id,
        product_name="Product",  # TODO: Fetch from database
        assigned_quantity=assignment.assigned_quantity,
        remaining_quantity=assignment.remaining_quantity,
        share_percentage=assignment.share_percentage,
        status=assignment.status,
        created_at=assignment.created_at,
        updated_at=assignment.updated_at,
        fulfilled_at=assignment.fulfilled_at,
    )


@router.patch("/assignments/{assignment_id}", response_model=ProductAssignmentResponse)
async def update_assignment(
    assignment_id: UUID,
    data: ProductAssignmentUpdate,
    service: PartnerProfitService = Depends(get_partner_profit_service),
):
    """
    Update a product assignment.

    Can only update assigned_quantity and share_percentage.
    Cannot update assignments with status='fulfilled'.
    """
    try:
        assignment = await service.update_assignment(assignment_id, data)

        if not assignment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Assignment {assignment_id} not found",
            )

        return ProductAssignmentResponse(
            id=assignment.id,
            partner_id=assignment.partner_id,
            partner_name="Partner",
            product_id=assignment.product_id,
            product_name="Product",
            assigned_quantity=assignment.assigned_quantity,
            remaining_quantity=assignment.remaining_quantity,
            share_percentage=assignment.share_percentage,
            status=assignment.status,
            created_at=assignment.created_at,
            updated_at=assignment.updated_at,
            fulfilled_at=assignment.fulfilled_at,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.delete("/assignments/{assignment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_assignment(
    assignment_id: UUID,
    service: PartnerProfitService = Depends(get_partner_profit_service),
):
    """
    Delete a product assignment.

    Can only delete assignments with no sales (remaining_quantity == assigned_quantity).
    Assignments with sales must be retained for audit trail.
    """
    try:
        deleted = await service.delete_assignment(assignment_id)

        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Assignment {assignment_id} not found",
            )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


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
