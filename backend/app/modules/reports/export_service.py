from concurrent.futures import ThreadPoolExecutor
from datetime import date
from io import BytesIO
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.export import ExportFormat, ExportMetadata


class ExportService:
    """Service for generating export files in various formats."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.executor = ThreadPoolExecutor(max_workers=4)

    # ── Core generators ─────────────────────────────────────────────

    async def generate_xlsx(
        self,
        data: list[dict],
        filename_prefix: str,
        start_date: date,
        end_date: date,
        title: str = "Report",
        meta_data: Optional[dict] = None,
    ) -> BytesIO:
        from app.modules.reports.export_generators import generate_xlsx
        return await generate_xlsx(data, filename_prefix, start_date, end_date, title, meta_data)

    async def generate_pdf(
        self,
        data: list[dict],
        title: str,
        start_date: date,
        end_date: date,
        generated_by: str,
        meta_data: Optional[dict] = None,
    ) -> bytes:
        from app.modules.reports.export_generators import generate_pdf
        return await generate_pdf(data, title, start_date, end_date, generated_by, meta_data)

    # ── Validation & Metadata ───────────────────────────────────────

    async def validate_export_limits(
        self, row_count: int, format: ExportFormat
    ) -> tuple[bool, Optional[str]]:
        from app.modules.reports.export_generators import validate_export_limits
        return await validate_export_limits(row_count, format)

    def create_export_metadata(
        self,
        format: ExportFormat,
        report_type: str,
        row_count: int,
        start_date: date,
        end_date: date,
        generated_by: str,
    ) -> ExportMetadata:
        from app.modules.reports.export_generators import create_export_metadata
        return create_export_metadata(format, report_type, row_count, start_date, end_date, generated_by)

    # ── Report-specific methods ─────────────────────────────────────

    async def generate_sales_pdf_report(
        self, sales_data: list, start_date: date, end_date: date, generated_by: str
    ) -> bytes:
        from app.modules.reports.export_reports import generate_sales_pdf_report
        return await generate_sales_pdf_report(self.db, sales_data, start_date, end_date, generated_by)

    async def generate_partners_pdf_report(
        self, partners_data: list, start_date: date, end_date: date, generated_by: str
    ) -> bytes:
        from app.modules.reports.export_reports import generate_partners_pdf_report
        return await generate_partners_pdf_report(self.db, partners_data, start_date, end_date, generated_by)

    async def generate_inventory_pdf_report(
        self, inventory_data: list, start_date: date, end_date: date, generated_by: str
    ) -> bytes:
        from app.modules.reports.export_reports import generate_inventory_pdf_report
        return await generate_inventory_pdf_report(self.db, inventory_data, start_date, end_date, generated_by)

    async def generate_dashboard_csv(
        self, data: list[dict], filename_prefix: str
    ) -> BytesIO:
        from app.modules.reports.export_reports import generate_dashboard_csv
        return await generate_dashboard_csv(self.db, data, filename_prefix)

    async def generate_dashboard_xlsx(
        self, data: list[dict], filename_prefix: str
    ) -> BytesIO:
        from app.modules.reports.export_reports import generate_dashboard_xlsx
        return await generate_dashboard_xlsx(self.db, data, filename_prefix)

    async def generate_dashboard_pdf(
        self, data: list[dict], title: str, generated_by: str = "system"
    ) -> bytes:
        from app.modules.reports.export_reports import generate_dashboard_pdf
        return await generate_dashboard_pdf(self.db, data, title, generated_by)

    async def generate_customer_statement_pdf(
        self,
        customer_data: dict,
        ledger_entries: list,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        generated_by: str = "system",
    ) -> bytes:
        from app.modules.reports.export_reports import generate_customer_statement_pdf
        return await generate_customer_statement_pdf(self.db, customer_data, ledger_entries, start_date, end_date, generated_by)

    async def generate_customer_statement_xlsx(
        self,
        customer_data: dict,
        ledger_entries: list,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> BytesIO:
        from app.modules.reports.export_reports import generate_customer_statement_xlsx
        return await generate_customer_statement_xlsx(self.db, customer_data, ledger_entries, start_date, end_date)

    async def generate_supplier_statement_pdf(
        self,
        supplier_data: dict,
        ledger_entries: list,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        generated_by: str = "system",
    ) -> bytes:
        from app.modules.reports.export_reports import generate_supplier_statement_pdf
        return await generate_supplier_statement_pdf(self.db, supplier_data, ledger_entries, start_date, end_date, generated_by)

    async def generate_supplier_statement_xlsx(
        self,
        supplier_data: dict,
        ledger_entries: list,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> BytesIO:
        from app.modules.reports.export_reports import generate_supplier_statement_xlsx
        return await generate_supplier_statement_xlsx(self.db, supplier_data, ledger_entries, start_date, end_date)

    async def generate_sale_invoice_pdf(
        self,
        sale_data: dict,
        generated_by: str = "system",
    ) -> bytes:
        from app.modules.reports.export_reports import generate_sale_invoice_pdf
        return await generate_sale_invoice_pdf(self.db, sale_data, generated_by)

    # ── Lifecycle ───────────────────────────────────────────────────

    async def shutdown(self):
        """Shutdown the thread pool executor."""
        self.executor.shutdown(wait=True)
