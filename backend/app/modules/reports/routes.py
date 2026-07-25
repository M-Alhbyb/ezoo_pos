from datetime import date
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from app.core.database import get_db
from app.modules.reports.service import ReportService
from app.modules.reports.export_service import ExportService
from app.schemas.report import (
    SalesReport,
    PartnerReport,
    InventoryReport,
)
from app.schemas.supplier_ledger import (
    SupplierSummaryReportResponse,
    SupplierSummaryReportItem,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/reports", tags=["reports"])


def get_report_service(db: AsyncSession = Depends(get_db)) -> ReportService:
    return ReportService(db)


def get_export_service(db: AsyncSession = Depends(get_db)) -> ExportService:
    return ExportService(db)


@router.get("/sales", response_model=SalesReport)
async def get_sales_report(
    service: ReportService = Depends(get_report_service),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
):
    return await service.get_sales_report(start_date, end_date, page, page_size)


@router.get("/partners", response_model=PartnerReport)
async def get_partners_report(
    service: ReportService = Depends(get_report_service),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
):
    return await service.get_partners_report(start_date, end_date, page, page_size)


@router.get("/inventory", response_model=InventoryReport)
async def get_inventory_report(
    service: ReportService = Depends(get_report_service),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
):
    return await service.get_inventory_report(start_date, end_date, page, page_size)


@router.get("/suppliers", response_model=SupplierSummaryReportResponse)
async def get_suppliers_summary_report(
    service: ReportService = Depends(get_report_service),
):
    try:
        data = await service.get_supplier_summary_report()
        return SupplierSummaryReportResponse(
            suppliers=[SupplierSummaryReportItem(**item) for item in data]
        )
    except Exception as e:
        logger.error(f"Supplier summary report failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/suppliers/{supplier_id}")
async def get_supplier_statement(
    supplier_id: UUID,
    start_date: Optional[date] = Query(None, description="Filter start date"),
    end_date: Optional[date] = Query(None, description="Filter end date"),
    service: ReportService = Depends(get_report_service),
):
    try:
        data = await service.get_supplier_statement(
            supplier_id=supplier_id,
            start_date=start_date,
            end_date=end_date,
        )
        return data
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Supplier statement failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Include export routes
from app.modules.reports.export_routes import router as export_router

router.include_router(export_router)
