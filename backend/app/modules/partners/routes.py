from datetime import datetime
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.partners.service import PartnerService
from app.schemas.partner import PartnerCreate, PartnerResponse, DistributionResponse, DistributionRequest

router = APIRouter(prefix="/api/partners", tags=["partners"])


def get_partner_service(db: AsyncSession = Depends(get_db)) -> PartnerService:
    return PartnerService(db)


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


@router.post("/distribute", response_model=DistributionResponse)
async def distribute_profits(
    data: DistributionRequest,
    service: PartnerService = Depends(get_partner_service),
):
    try:
        return await service.calculate_distribution(
            total_profit=data.profit
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
