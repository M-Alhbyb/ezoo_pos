from datetime import datetime, date
from decimal import Decimal
from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from io import BytesIO
import logging

from app.core.database import get_db
from app.modules.reports.service import ReportService
from app.modules.reports.export_service import ExportService
from app.schemas.report import (
    SalesReport,
    ProjectReport,
    PartnerReport,
    InventoryReport,
)
from app.schemas.export import ExportFormat
from app.websocket.manager import manager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/reports", tags=["reports"])


def get_report_service(db: AsyncSession = Depends(get_db)) -> ReportService:
    return ReportService(db)


def get_export_service(db: AsyncSession = Depends(get_db)) -> ExportService:
    return ExportService(db)


@router.get("/sales", response_model=SalesReport)
async def get_sales_report(
    service: ReportService = Depends(get_report_service),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
):
    """
    Get aggregate sales statistics with daily breakdown.
    """
    return await service.get_sales_report(start_date, end_date, page, page_size)


@router.get("/projects", response_model=ProjectReport)
async def get_projects_report(
    service: ReportService = Depends(get_report_service),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
):
    """
    Get aggregate project statistics including individual project status.
    """
    return await service.get_projects_report(start_date, end_date, page, page_size)


@router.get("/partners", response_model=PartnerReport)
async def get_partners_report(
    service: ReportService = Depends(get_report_service),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
):
    """
    Get aggregate partner payouts.
    """
    return await service.get_partners_report(start_date, end_date, page, page_size)


@router.get("/inventory", response_model=InventoryReport)
async def get_inventory_report(
    service: ReportService = Depends(get_report_service),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
):
    """
    Get aggregate inventory statistics based on movement logs.
    """
    return await service.get_inventory_report(start_date, end_date, page, page_size)


@router.get("/sales/export")
async def export_sales_report(
    format: ExportFormat = Query(..., description="Export format: csv, xlsx, or pdf"),
    start_date: date = Query(..., description="Start date for the report"),
    end_date: date = Query(..., description="End date for the report"),
    websocket_id: Optional[str] = Query(
        None, description="WebSocket connection ID for progress updates"
    ),
    service: ReportService = Depends(get_report_service),
    export_service: ExportService = Depends(get_export_service),
):
    """
    Export sales report in CSV, XLSX, or PDF format.
    """
    try:
        if websocket_id:
            await manager.send_progress(
                websocket_id,
                {
                    "export_id": "sales_export",
                    "status": "started",
                    "progress": 0,
                    "stage": "validating",
                },
            )

        row_count = await service.get_sales_count(start_date, end_date)

        is_valid, error_msg = await export_service.validate_export_limits(
            row_count, format
        )
        if not is_valid:
            logger.warning(
                f"Sales export rejected: {error_msg} (row_count={row_count}, format={format.value})"
            )
            if websocket_id:
                await manager.send_progress(
                    websocket_id,
                    {
                        "export_id": "sales_export",
                        "status": "failed",
                        "progress": 0,
                        "error_message": error_msg,
                    },
                )
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "row_limit_exceeded",
                    "message": error_msg,
                    "format": format.value,
                    "requested_rows": row_count,
                    "suggestion": f"Try a narrower date range or use {format.value.upper()} format which supports up to {row_count} rows".format(
                        CSV="100,000"
                        if format == ExportFormat.CSV
                        else "50,000"
                        if format == ExportFormat.XLSX
                        else "10,000"
                    )
                    if "CSV" in error_msg or "XLSX" in error_msg or "PDF" in error_msg
                    else "Try a narrower date range",
                },
            )

        if websocket_id:
            await manager.send_progress(
                websocket_id,
                {
                    "export_id": "sales_export",
                    "status": "processing",
                    "progress": 50,
                    "stage": "generating",
                },
            )

        sales_data = []
        sales = await service.get_sales_report(start_date, end_date)
        for group in sales.daily_breakdown:
            sales_data.append(
                {
                    "date": str(group.date),
                    "subtotal": group.revenue,
                    "fees_total": Decimal("0"),
                    "vat_amount": group.revenue * Decimal("0.15") / Decimal("1.15"),
                    "grand_total": group.revenue,
                    "profit": group.profit,
                }
            )

        filename_prefix = f"sales_report_{start_date}_{end_date}"

        if format == ExportFormat.CSV:
            output = await export_service.generate_csv(
                sales_data, filename_prefix, start_date, end_date
            )
            media_type = "text/csv"
        elif format == ExportFormat.XLSX:
            output = await export_service.generate_xlsx(
                sales_data, filename_prefix, start_date, end_date
            )
            media_type = (
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            output = await export_service.generate_sales_pdf_report(
                sales_data, start_date, end_date, "system"
            )
            return StreamingResponse(
                BytesIO(output),
                media_type="application/pdf",
                headers={
                    "Content-Disposition": f'attachment; filename="{filename_prefix}.pdf"'
                },
            )

        if websocket_id:
            await manager.send_progress(
                websocket_id,
                {"export_id": "sales_export", "status": "completed", "progress": 100},
            )

        logger.info(
            f"Sales export completed: {format.value}, {row_count} rows, {start_date} to {end_date}"
        )
        return StreamingResponse(
            output,
            media_type=media_type,
            headers={
                "Content-Disposition": f'attachment; filename="{filename_prefix}.{format.value}"'
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Sales export failed: {str(e)}", exc_info=True)
        if websocket_id:
            await manager.send_progress(
                websocket_id,
                {
                    "export_id": "sales_export",
                    "status": "failed",
                    "progress": 0,
                    "error_message": str(e),
                },
            )
        raise HTTPException(
            status_code=500,
            detail={
                "error": "generation_failed",
                "message": "Failed to generate export. Please try again later.",
                "suggestion": "If the problem persists, try with a smaller date range.",
            },
        )


@router.get("/projects/export")
async def export_projects_report(
    format: ExportFormat = Query(..., description="Export format: csv, xlsx, or pdf"),
    start_date: date = Query(..., description="Start date for the report"),
    end_date: date = Query(..., description="End date for the report"),
    service: ReportService = Depends(get_report_service),
    export_service: ExportService = Depends(get_export_service),
):
    """
    Export projects report in CSV, XLSX, or PDF format.
    """
    try:
        row_count = await service.get_projects_count(start_date, end_date)

        is_valid, error_msg = await export_service.validate_export_limits(
            row_count, format
        )
        if not is_valid:
            logger.warning(
                f"Projects export rejected: {error_msg} (row_count={row_count}, format={format.value})"
            )
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "row_limit_exceeded",
                    "message": error_msg,
                    "format": format.value,
                    "requested_rows": row_count,
                    "suggestion": "Try a narrower date range.",
                },
            )

        projects_data = []
        projects = await service.get_projects_report(start_date, end_date)
        for project in projects.projects:
            projects_data.append(
                {
                    "name": project.name,
                    "status": project.status.value
                    if hasattr(project.status, "value")
                    else str(project.status),
                    "start_date": str(project.start_date),
                    "total_cost": project.total_cost,
                    "selling_price": project.selling_price,
                    "profit": project.profit,
                }
            )

        filename_prefix = f"projects_report_{start_date}_{end_date}"

        if format == ExportFormat.CSV:
            output = await export_service.generate_csv(
                projects_data, filename_prefix, start_date, end_date
            )
            media_type = "text/csv"
        elif format == ExportFormat.XLSX:
            output = await export_service.generate_xlsx(
                projects_data, filename_prefix, start_date, end_date
            )
            media_type = (
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            output = await export_service.generate_projects_pdf_report(
                projects_data, start_date, end_date, "system"
            )
            return StreamingResponse(
                BytesIO(output),
                media_type="application/pdf",
                headers={
                    "Content-Disposition": f'attachment; filename="{filename_prefix}.pdf"'
                },
            )

        logger.info(f"Projects export completed: {format.value}, {row_count} rows")
        return StreamingResponse(
            output,
            media_type=media_type,
            headers={
                "Content-Disposition": f'attachment; filename="{filename_prefix}.{format.value}"'
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Projects export failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "error": "generation_failed",
                "message": "Failed to generate export. Please try again later.",
                "suggestion": "If the problem persists, try with a smaller date range.",
            },
        )


@router.get("/partners/export")
async def export_partners_report(
    format: ExportFormat = Query(..., description="Export format: csv, xlsx, or pdf"),
    start_date: date = Query(..., description="Start date for the report"),
    end_date: date = Query(..., description="End date for the report"),
    service: ReportService = Depends(get_report_service),
    export_service: ExportService = Depends(get_export_service),
):
    """
    Export partners report in CSV, XLSX, or PDF format.
    """
    try:
        row_count = await service.get_partners_count(start_date, end_date)

        is_valid, error_msg = await export_service.validate_export_limits(
            row_count, format
        )
        if not is_valid:
            logger.warning(
                f"Partners export rejected: {error_msg} (row_count={row_count}, format={format.value})"
            )
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "row_limit_exceeded",
                    "message": error_msg,
                    "format": format.value,
                    "requested_rows": row_count,
                    "suggestion": "Try a narrower date range.",
                },
            )

        partners_data = []
        partners = await service.get_partners_report(start_date, end_date)
        for payout in partners.payouts:
            partners_data.append(
                {
                    "name": payout.partner_name,
                    "invested_amount": payout.invested_amount,
                    "profit_percentage": payout.profit_percentage,
                    "distributed_amount": payout.distributed_amount,
                    "distribution_date": str(payout.distribution_date),
                }
            )

        filename_prefix = f"partners_report_{start_date}_{end_date}"

        if format == ExportFormat.CSV:
            output = await export_service.generate_csv(
                partners_data, filename_prefix, start_date, end_date
            )
            media_type = "text/csv"
        elif format == ExportFormat.XLSX:
            output = await export_service.generate_xlsx(
                partners_data, filename_prefix, start_date, end_date
            )
            media_type = (
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            output = await export_service.generate_partners_pdf_report(
                partners_data, start_date, end_date, "system"
            )
            return StreamingResponse(
                BytesIO(output),
                media_type="application/pdf",
                headers={
                    "Content-Disposition": f'attachment; filename="{filename_prefix}.pdf"'
                },
            )

        logger.info(f"Partners export completed: {format.value}, {row_count} rows")
        return StreamingResponse(
            output,
            media_type=media_type,
            headers={
                "Content-Disposition": f'attachment; filename="{filename_prefix}.{format.value}"'
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Partners export failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "error": "generation_failed",
                "message": "Failed to generate export. Please try again later.",
                "suggestion": "If the problem persists, try with a smaller date range.",
            },
        )


@router.get("/inventory/export")
async def export_inventory_report(
    format: ExportFormat = Query(..., description="Export format: csv, xlsx, or pdf"),
    start_date: date = Query(..., description="Start date for the report"),
    end_date: date = Query(..., description="End date for the report"),
    service: ReportService = Depends(get_report_service),
    export_service: ExportService = Depends(get_export_service),
):
    """
    Export inventory report in CSV, XLSX, or PDF format.
    """
    try:
        row_count = await service.get_inventory_count(start_date, end_date)

        is_valid, error_msg = await export_service.validate_export_limits(
            row_count, format
        )
        if not is_valid:
            logger.warning(
                f"Inventory export rejected: {error_msg} (row_count={row_count}, format={format.value})"
            )
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "row_limit_exceeded",
                    "message": error_msg,
                    "format": format.value,
                    "requested_rows": row_count,
                    "suggestion": "Try a narrower date range.",
                },
            )

        inventory_data = []
        inventory = await service.get_inventory_report(start_date, end_date)
        for movement in inventory.movements:
            inventory_data.append(
                {
                    "product_name": movement.product_name,
                    "movement_type": movement.movement_type,
                    "quantity_delta": movement.quantity_delta,
                    "reason": movement.reason,
                    "created_at": str(movement.timestamp),
                }
            )

        filename_prefix = f"inventory_report_{start_date}_{end_date}"

        if format == ExportFormat.CSV:
            output = await export_service.generate_csv(
                inventory_data, filename_prefix, start_date, end_date
            )
            media_type = "text/csv"
        elif format == ExportFormat.XLSX:
            output = await export_service.generate_xlsx(
                inventory_data, filename_prefix, start_date, end_date
            )
            media_type = (
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            output = await export_service.generate_inventory_pdf_report(
                inventory_data, start_date, end_date, "system"
            )
            return StreamingResponse(
                BytesIO(output),
                media_type="application/pdf",
                headers={
                    "Content-Disposition": f'attachment; filename="{filename_prefix}.pdf"'
                },
            )

        logger.info(f"Inventory export completed: {format.value}, {row_count} rows")
        return StreamingResponse(
            output,
            media_type=media_type,
            headers={
                "Content-Disposition": f'attachment; filename="{filename_prefix}.{format.value}"'
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Inventory export failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "error": "generation_failed",
                "message": "Failed to generate export. Please try again later.",
                "suggestion": "If the problem persists, try with a smaller date range.",
            },
        )
