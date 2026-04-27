from datetime import datetime, date
from decimal import Decimal
from typing import Optional
from uuid import UUID
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
    PartnerReport,
    InventoryReport,
)
from app.schemas.export import ExportFormat
from app.schemas.supplier_ledger import (
    SupplierSummaryReportResponse,
    SupplierSummaryReportItem,
    SupplierStatementResponse,
)
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
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
):
    """
    Get aggregate sales statistics with daily breakdown.
    """
    return await service.get_sales_report(start_date, end_date, page, page_size)


@router.get("/partners", response_model=PartnerReport)
async def get_partners_report(
    service: ReportService = Depends(get_report_service),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
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
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
):
    """
    Get aggregate inventory statistics based on movement logs.
    """
    return await service.get_inventory_report(start_date, end_date, page, page_size)


@router.get("/export/sales")
async def export_sales_report(
    format: ExportFormat = Query(..., description="Export format: xlsx or pdf"),
    start_date: date = Query(..., description="Start date for the report"),
    end_date: date = Query(..., description="End date for the report"),
    websocket_id: Optional[str] = Query(
        None, description="WebSocket connection ID for progress updates"
    ),
    service: ReportService = Depends(get_report_service),
    export_service: ExportService = Depends(get_export_service),
):
    """
    Export sales report in XLSX or PDF format.
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
                        XLSX="50,000"
                        if format == ExportFormat.XLSX
                        else "10,000"
                    )
                    if "XLSX" in error_msg or "PDF" in error_msg
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

        sales_data = await service.get_sales_export_data(start_date, end_date)

        filename_prefix = f"sales_report_{start_date}_{end_date}"

        if format == ExportFormat.XLSX:
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


@router.get("/export/partners")
async def export_partners_report(
    format: ExportFormat = Query(..., description="Export format: xlsx or pdf"),
    start_date: date = Query(..., description="Start date for the report"),
    end_date: date = Query(..., description="End date for the report"),
    service: ReportService = Depends(get_report_service),
    export_service: ExportService = Depends(get_export_service),
):
    """
    Export partners report in XLSX or PDF format.
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

        partners_data = await service.get_partners_export_data(start_date, end_date)

        filename_prefix = f"partners_report_{start_date}_{end_date}"

        if format == ExportFormat.XLSX:
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


@router.get("/export/inventory")
async def export_inventory_report(
    format: ExportFormat = Query(..., description="Export format: xlsx or pdf"),
    start_date: date = Query(..., description="Start date for the report"),
    end_date: date = Query(..., description="End date for the report"),
    service: ReportService = Depends(get_report_service),
    export_service: ExportService = Depends(get_export_service),
):
    """
    Export inventory report in XLSX or PDF format.
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

        inventory_data = await service.get_inventory_export_data(start_date, end_date)

        filename_prefix = f"inventory_report_{start_date}_{end_date}"

        if format == ExportFormat.XLSX:
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


@router.get("/suppliers", response_model=SupplierSummaryReportResponse)
async def get_suppliers_summary_report(
    service: ReportService = Depends(get_report_service),
):
    """
    Get summary report for all suppliers.
    """
    try:
        data = await service.get_supplier_summary_report()
        return SupplierSummaryReportResponse(
            suppliers=[SupplierSummaryReportItem(**item) for item in data]
        )
    except Exception as e:
        logger.error(f"Supplier summary report failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))




@router.get("/export/customers/{customer_id}")
async def export_customer_statement(
    customer_id: UUID,
    format: ExportFormat = Query(..., description="Export format: xlsx or pdf"),
    start_date: Optional[date] = Query(None, description="Start date for the report"),
    end_date: Optional[date] = Query(None, description="End date for the report"),
    service: ReportService = Depends(get_report_service),
    export_service: ExportService = Depends(get_export_service),
):
    """
    Export customer statement in XLSX or PDF format.
    """
    try:
        from urllib.parse import quote
        from app.modules.customers.service import CustomerService
        
        # Using a context manager for the session
        from app.core.database import AsyncSessionLocal
        
        async def get_customer_data(db_session):
            cust_service = CustomerService(db_session)
            customer = await cust_service.get_customer(customer_id)
            if not customer:
                raise ValueError("Customer not found")
            summary = await cust_service.get_customer_summary(customer_id)
            entries, _ = await cust_service.list_ledger_entries(
                customer_id, page_size=2000, start_date=start_date, end_date=end_date
            )
            
            customer_data = {
                "name": customer.name,
                "phone": customer.phone,
                "summary": {
                    "total_sales": float(summary.total_sales),
                    "total_payments": float(summary.total_payments),
                    "total_returns": float(summary.total_returns),
                    "balance": float(summary.balance),
                }
            }
            
            ledger_entries = [
                {
                    "type": entry.type,
                    "amount": float(entry.amount),
                    "created_at": entry.created_at,
                    "note": entry.note,
                }
                for entry in entries
            ]
            return customer_data, ledger_entries

        async with AsyncSessionLocal() as db:
            customer_data, ledger_entries = await get_customer_data(db)

        customer_name = customer_data.get("name", "customer")
        filename_prefix = f"customer_statement_{customer_name}_{start_date or 'all'}_{end_date or 'all'}"
        encoded_filename = quote(f"{filename_prefix}.{format.value}")

        if format == ExportFormat.XLSX:
            output = await export_service.generate_customer_statement_xlsx(
                customer_data, ledger_entries, start_date, end_date
            )
            media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            return StreamingResponse(
                output,
                media_type=media_type,
                headers={
                    "Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"
                },
            )
        else:
            output = await export_service.generate_customer_statement_pdf(
                customer_data, ledger_entries, start_date, end_date, "system"
            )
            encoded_pdf_filename = quote(f"{filename_prefix}.pdf")
            return StreamingResponse(
                BytesIO(output),
                media_type="application/pdf",
                headers={
                    "Content-Disposition": f"attachment; filename*=UTF-8''{encoded_pdf_filename}"
                },
            )

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Customer export failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to generate customer export")


@router.get("/export/suppliers/{supplier_id}")
async def export_supplier_statement(
    supplier_id: UUID,
    format: ExportFormat = Query(..., description="Export format: xlsx or pdf"),
    start_date: Optional[date] = Query(None, description="Start date for the report"),
    end_date: Optional[date] = Query(None, description="End date for the report"),
    service: ReportService = Depends(get_report_service),
    export_service: ExportService = Depends(get_export_service),
):
    """
    Export supplier statement in XLSX or PDF format.
    """
    try:
        from urllib.parse import quote
        data = await service.get_supplier_statement(
            supplier_id=supplier_id,
            start_date=start_date,
            end_date=end_date,
        )

        supplier_name = data.get("supplier", {}).get("name", "supplier")
        filename_prefix = f"supplier_statement_{supplier_name}_{start_date or 'all'}_{end_date or 'all'}"
        # URL encode filename for Content-Disposition header to avoid latin-1 errors
        encoded_filename = quote(f"{filename_prefix}.{format.value}")

        if format == ExportFormat.XLSX:
            output = await export_service.generate_supplier_statement_xlsx(
                data, data.get("ledger", []), start_date, end_date
            )
            media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            return StreamingResponse(
                output,
                media_type=media_type,
                headers={
                    "Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"
                },
            )
        else:
            output = await export_service.generate_supplier_statement_pdf(
                data, data.get("ledger", []), start_date, end_date, "system"
            )
            encoded_pdf_filename = quote(f"{filename_prefix}.pdf")
            return StreamingResponse(
                BytesIO(output),
                media_type="application/pdf",
                headers={
                    "Content-Disposition": f"attachment; filename*=UTF-8''{encoded_pdf_filename}"
                },
            )

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Supplier export failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to generate supplier export")


@router.get("/suppliers/{supplier_id}")
async def get_supplier_statement(
    supplier_id: UUID,
    start_date: Optional[date] = Query(None, description="Filter start date"),
    end_date: Optional[date] = Query(None, description="Filter end date"),
    service: ReportService = Depends(get_report_service),
):
    """
    Get supplier statement with ledger entries and date filtering.
    """
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
