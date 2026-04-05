from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.reports.service import ReportService
from app.schemas.report import SalesReport, ProjectReport, PartnerReport, InventoryReport

router = APIRouter(prefix="/api/reports", tags=["reports"])


def get_report_service(db: AsyncSession = Depends(get_db)) -> ReportService:
    return ReportService(db)


@router.get("/sales", response_model=SalesReport)
async def get_sales_report(
    service: ReportService = Depends(get_report_service),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
):
    """
    Get aggregate sales statistics with daily breakdown.
    """
    return await service.get_sales_report(start_date, end_date)


@router.get("/projects", response_model=ProjectReport)
async def get_projects_report(
    service: ReportService = Depends(get_report_service),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
):
    """
    Get aggregate project statistics including individual project status.
    """
    return await service.get_projects_report(start_date, end_date)


@router.get("/partners", response_model=PartnerReport)
async def get_partners_report(
    service: ReportService = Depends(get_report_service),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
):
    """
    Get aggregate partner payouts.
    """
    return await service.get_partners_report(start_date, end_date)


@router.get("/inventory", response_model=InventoryReport)
async def get_inventory_report(
    service: ReportService = Depends(get_report_service),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
):
    """
    Get aggregate inventory statistics based on movement logs.
    """
    return await service.get_inventory_report(start_date, end_date)
