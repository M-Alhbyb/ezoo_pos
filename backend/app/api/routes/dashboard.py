from datetime import date, datetime
from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from io import BytesIO
import logging

from app.core.database import get_db
from app.modules.reports.dashboard_service import DashboardService
from app.modules.reports.export_service import ExportService
from app.schemas.dashboard import (
    SalesDashboardFilter,
    PartnersDashboardFilter,
    InventoryDashboardFilter,
    DashboardResponse,
    SalesChartData,
    PartnerChartData,
    InventoryChartData,
)
from app.schemas.export import ExportFormat

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/dashboard", tags=["dashboards"])


def get_dashboard_service(db: AsyncSession = Depends(get_db)) -> DashboardService:
    return DashboardService(db)


def get_export_service(db: AsyncSession = Depends(get_db)) -> ExportService:
    return ExportService(db)


@router.get("/sales", response_model=DashboardResponse)
async def get_sales_dashboard(
    service: DashboardService = Depends(get_dashboard_service),
    export_service: ExportService = Depends(get_export_service),
    start_date: date = Query(..., description="Start date of the range"),
    end_date: date = Query(..., description="End date of the range"),
    export: Optional[ExportFormat] = Query(
        None, description="Export format: csv, xlsx, or pdf"
    ),
):
    """
    Get aggregated sales data for line chart visualization or export.
    Displays daily revenue, profit, and VAT trends.
    """
    try:
        filter_applied = SalesDashboardFilter(start_date=start_date, end_date=end_date)
        data = await service.get_sales_dashboard_data(start_date, end_date)

        if export:
            chart_data = []
            for i, date_val in enumerate(data.dates):
                chart_data.append(
                    {
                        "date": str(date_val),
                        "revenue": float(data.revenue[i]),
                        "profit": float(data.profit[i]),
                        "vat": float(data.vat[i]),
                    }
                )

            filename_prefix = f"sales_dashboard_{start_date}_{end_date}"

            if export == ExportFormat.CSV:
                output = await export_service.generate_dashboard_csv(
                    chart_data, filename_prefix
                )
                media_type = "text/csv"
            elif export == ExportFormat.XLSX:
                output = await export_service.generate_dashboard_xlsx(
                    chart_data, filename_prefix
                )
                media_type = (
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            else:
                output_bytes = await export_service.generate_dashboard_pdf(
                    chart_data, "Sales Dashboard Report"
                )
                return StreamingResponse(
                    BytesIO(output_bytes),
                    media_type="application/pdf",
                    headers={
                        "Content-Disposition": f'attachment; filename="{filename_prefix}.pdf"'
                    },
                )

            return StreamingResponse(
                output,
                media_type=media_type,
                headers={
                    "Content-Disposition": f'attachment; filename="{filename_prefix}.{export.value}"'
                },
            )

        return DashboardResponse(
            success=True,
            data=data,
            total_points=len(data.dates),
            filter_applied=filter_applied,
        )
    except ValueError as e:
        error_msg = str(e)
        logger.warning(f"Sales dashboard error: {error_msg}")
        return DashboardResponse(
            success=False,
            data=None,
            error=error_msg,
            total_points=None,
            filter_applied=None,
        )
    except Exception as e:
        logger.error(f"Sales dashboard failed: {str(e)}", exc_info=True)
        return DashboardResponse(
            success=False,
            data=None,
            error="Failed to load dashboard data. Please try again later.",
            total_points=None,
            filter_applied=None,
        )




@router.get("/partners", response_model=DashboardResponse)
async def get_partners_dashboard(
    service: DashboardService = Depends(get_dashboard_service),
    start_date: date = Query(..., description="Start date of the range"),
    end_date: date = Query(..., description="End date of the range"),
    partner_id: Optional[int] = Query(
        None, description="Filter by specific partner ID"
    ),
):
    """
    Get aggregated partner dividend data for pie chart visualization.
    Displays partner names, dividend amounts, and percentages.
    """
    try:
        filter_applied = PartnersDashboardFilter(
            start_date=start_date, end_date=end_date, partner_id=partner_id
        )
        data = await service.get_partners_dashboard_data(
            start_date, end_date, partner_id
        )

        return DashboardResponse(
            success=True,
            data=data,
            total_points=len(data.partner_names),
            filter_applied=filter_applied,
        )
    except ValueError as e:
        error_msg = str(e)
        logger.warning(f"Partners dashboard error: {error_msg}")
        return DashboardResponse(
            success=False,
            data=None,
            error=error_msg,
            total_points=None,
            filter_applied=None,
        )
    except Exception as e:
        logger.error(f"Partners dashboard failed: {str(e)}", exc_info=True)
        return DashboardResponse(
            success=False,
            data=None,
            error="Failed to load dashboard data. Please try again later.",
            total_points=None,
            filter_applied=None,
        )


@router.get("/inventory", response_model=DashboardResponse)
async def get_inventory_dashboard(
    service: DashboardService = Depends(get_dashboard_service),
    start_date: date = Query(..., description="Start date of the range"),
    end_date: date = Query(..., description="End date of the range"),
):
    """
    Get aggregated inventory movement data for stacked bar chart visualization.
    Displays daily sales, restocks, and reversals by quantity.
    """
    try:
        filter_applied = InventoryDashboardFilter(
            start_date=start_date, end_date=end_date
        )
        data = await service.get_inventory_dashboard_data(start_date, end_date)

        return DashboardResponse(
            success=True,
            data=data,
            total_points=len(data.dates),
            filter_applied=filter_applied,
        )
    except ValueError as e:
        error_msg = str(e)
        logger.warning(f"Inventory dashboard error: {error_msg}")
        return DashboardResponse(
            success=False,
            data=None,
            error=error_msg,
            total_points=None,
            filter_applied=None,
        )
    except Exception as e:
        logger.error(f"Inventory dashboard failed: {str(e)}", exc_info=True)
        return DashboardResponse(
            success=False,
            data=None,
            error="Failed to load dashboard data. Please try again later.",
            total_points=None,
            filter_applied=None,
        )
