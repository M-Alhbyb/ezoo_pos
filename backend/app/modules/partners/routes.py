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
    data: Optional[DistributionRequest] = None,
    service: PartnerService = Depends(get_partner_service),
):
    try:
        date_range = {}
        project_ids = None
        
        if data:
            project_ids = data.project_ids
            if data.start_date:
                date_range["start"] = data.start_date
            if data.end_date:
                date_range["end"] = data.end_date
            
        return await service.calculate_distribution(
            project_ids=project_ids,
            date_range=date_range if date_range else None
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
