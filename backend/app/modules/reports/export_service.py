import asyncio
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime
from decimal import Decimal
from io import BytesIO
from typing import Optional
import uuid
import logging

from sqlalchemy.ext.asyncio import AsyncSession
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import pandas as pd

from app.core.config import settings
from app.core.arabic_pdf import prepare_cell_value, is_arabic_text
from app.schemas.export import ExportFormat, ExportMetadata, ExportResponse

logger = logging.getLogger(__name__)


# Arabic font directory
FONT_DIR = "/usr/share/fonts/truetype"  # System fonts directory on Linux


def _register_arabic_fonts():
    """Register Arabic fonts for PDF rendering, prioritizing Cairo."""
    fonts_registered = False

    try:
        import os

        # Get path to static fonts directory
        # Current file is in app/modules/reports/export_service.py
        # app/static/fonts is at ../../../static/fonts relative to this file
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        static_fonts_dir = os.path.join(base_dir, "static", "fonts")
        
        cairo_regular = os.path.join(static_fonts_dir, "Cairo-Regular.ttf")
        cairo_bold = os.path.join(static_fonts_dir, "Cairo-Bold.ttf")

        # Register Cairo if available
        if os.path.exists(cairo_regular):
            try:
                pdfmetrics.registerFont(TTFont("Cairo", cairo_regular))
                pdfmetrics.registerFont(TTFont("Cairo-Bold", cairo_bold))
                # Register alias for generic font usage
                pdfmetrics.registerFont(TTFont("ArabicFont", cairo_regular))
                fonts_registered = True
                logger.info(f"Registered Cairo fonts from: {static_fonts_dir}")
            except Exception as e:
                logger.warning(f"Failed to register Cairo font: {e}")

        # Fallback to system fonts if Cairo not found
        if not fonts_registered:
            font_paths = [
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
                "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
                "/usr/share/fonts/TTF/DejaVuSans.ttf",
            ]

            for font_path in font_paths:
                if os.path.exists(font_path):
                    try:
                        pdfmetrics.registerFont(TTFont("ArabicFont", font_path))
                        fonts_registered = True
                        logger.info(f"Registered system Arabic-capable font: {font_path}")
                        break
                    except Exception as e:
                        logger.warning(f"Failed to register font {font_path}: {e}")

        if not fonts_registered:
            logger.warning(
                "No Arabic-capable fonts found, using default Helvetica"
            )

    except Exception as e:
        logger.warning(f"Font registration failed: {e}. Using default fonts.")


_register_arabic_fonts()


class ExportService:
    """Service for generating export files in various formats."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.executor = ThreadPoolExecutor(max_workers=4)

    async def generate_csv(
        self, data: list[dict], filename_prefix: str, start_date: date, end_date: date
    ) -> BytesIO:
        """
        Generate CSV export using pandas.

        Args:
            data: List of dictionaries with export data
            filename_prefix: Prefix for filename (e.g., 'sales_report')
            start_date: Report start date
            end_date: Report end date

        Returns:
            BytesIO buffer containing CSV data
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.executor, self._generate_csv_sync, data)

    def _generate_csv_sync(self, data: list[dict]) -> BytesIO:
        """Synchronous CSV generation with UTF-8 BOM for Arabic support."""
        try:
            output = BytesIO()
            # Add UTF-8 BOM for proper Arabic display in Excel/CSV viewers
            output.write("\ufeff".encode("utf-8"))
            df = pd.DataFrame(data)
            df.to_csv(output, index=False, encoding="utf-8", float_format="%.4f")
            output.seek(0)
            return output
        except Exception as e:
            logger.error(f"CSV export generation failed: {str(e)}", exc_info=True)
            raise

    def _generate_xlsx_sync(self, data: list[dict]) -> BytesIO:
        """Synchronous XLSX generation with Arabic support."""
        try:
            output = BytesIO()
            df = pd.DataFrame(data)

            with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
                df.to_excel(
                    writer, index=False, sheet_name="Report", float_format="%.4f"
                )

                workbook = writer.book
                worksheet = writer.sheets["Report"]

                # Configure columns
                for idx, col in enumerate(df.columns):
                    max_len = max(df[col].astype(str).str.len().max(), len(col)) + 2
                    worksheet.set_column(idx, idx, max_len)

            output.seek(0)
            return output
        except Exception as e:
            logger.error(f"XLSX export generation failed: {str(e)}", exc_info=True)
            raise

    async def generate_xlsx(
        self, data: list[dict], filename_prefix: str, start_date: date, end_date: date
    ) -> BytesIO:
        """
        Generate Excel export using pandas with xlsxwriter.

        Args:
            data: List of dictionaries with export data
            filename_prefix: Prefix for filename
            start_date: Report start date
            end_date: Report end date

        Returns:
            BytesIO buffer containing XLSX data
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.executor, self._generate_xlsx_sync, data)


    async def generate_pdf(
        self,
        data: list[dict],
        title: str,
        start_date: date,
        end_date: date,
        generated_by: str,
    ) -> bytes:
        """
        Generate PDF export using ReportLab.

        Args:
            data: List of dictionaries with export data
            title: Report title
            start_date: Report start date
            end_date: Report end date
            generated_by: User who generated the report

        Returns:
            PDF bytes
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor,
            self._generate_pdf_sync,
            data,
            title,
            start_date,
            end_date,
            generated_by,
        )

    def _generate_pdf_sync(
        self,
        data: list[dict],
        title: str,
        start_date: date,
        end_date: date,
        generated_by: str,
    ) -> bytes:
        """Synchronous PDF generation with Arabic support."""
        try:
            output = BytesIO()
            doc = SimpleDocTemplate(output, pagesize=landscape(letter))
            elements = []

            styles = getSampleStyleSheet()

            # Try to use Arabic font if registered, prioritizing Cairo-Bold for headings
            try:
                title_style = styles["Heading1"]
                if "Cairo-Bold" in pdfmetrics.getRegisteredFontNames():
                    title_style.fontName = "Cairo-Bold"
                elif "ArabicFont" in pdfmetrics.getRegisteredFontNames():
                    title_style.fontName = "ArabicFont"
            except Exception:
                title_style = styles["Heading1"]

            # Prepare title for PDF (handle Arabic text)
            pdf_title = prepare_cell_value(title) if is_arabic_text(title) else title
            elements.append(Paragraph(pdf_title, title_style))

            # Prepare date range text
            date_text = f"Date Range: {start_date} to {end_date}"
            elements.append(Paragraph(date_text, styles["Normal"]))

            # Prepare generated by text
            generated_text = f"Generated by: {generated_by} on {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            elements.append(Paragraph(generated_text, styles["Normal"]))
            elements.append(Paragraph("<br/><br/>", styles["Normal"]))

            if data:
                headers = list(data[0].keys())
                table_data = [headers]

                for row in data:
                    table_row = []
                    for key in headers:
                        value = row[key]
                        # Use prepare_cell_value for proper handling of Arabic text
                        table_row.append(prepare_cell_value(value))
                    table_data.append(table_row)

                table = Table(table_data)
                table.setStyle(
                    TableStyle(
                        [
                            ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                            ("FONTSIZE", (0, 0), (-1, 0), 10),
                            ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                            ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                            ("TEXTCOLOR", (0, 1), (-1, -1), colors.black),
                            ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                            ("FONTSIZE", (0, 1), (-1, -1), 8),
                            ("GRID", (0, 0), (-1, -1), 1, colors.black),
                        ]
                    )
                )

                # Try to use Arabic font for data if available
                try:
                    registered_fonts = pdfmetrics.getRegisteredFontNames()
                    if "ArabicFont" in registered_fonts:
                        # Check if any data contains Arabic
                        has_arabic = any(
                            is_arabic_text(str(v)) for row in data for v in row.values()
                        )
                        if has_arabic:
                            # Use Cairo-Bold for headers and ArabicFont (Cairo) for body if available
                            header_font = "Cairo-Bold" if "Cairo-Bold" in registered_fonts else "ArabicFont"
                            body_font = "ArabicFont"
                            
                            table.setStyle(
                                TableStyle(
                                    [
                                        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                                        (
                                            "TEXTCOLOR",
                                            (0, 0),
                                            (-1, 0),
                                            colors.whitesmoke,
                                        ),
                                        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                                        ("FONTNAME", (0, 0), (-1, 0), header_font),
                                        ("FONTNAME", (0, 1), (-1, -1), body_font),
                                        ("FONTSIZE", (0, 0), (-1, 0), 10),
                                        ("FONTSIZE", (0, 1), (-1, -1), 8),
                                        ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                                        ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                                        ("TEXTCOLOR", (0, 1), (-1, -1), colors.black),
                                        ("GRID", (0, 0), (-1, -1), 1, colors.black),
                                    ]
                                )
                            )
                except Exception as e:
                    logger.warning(f"Arabic font styling skipped: {e}")

                elements.append(table)

            doc.build(elements)
            output.seek(0)
            return output.read()
        except Exception as e:
            logger.error(f"PDF export generation failed: {str(e)}", exc_info=True)
            raise

    async def validate_export_limits(
        self, row_count: int, format: ExportFormat
    ) -> tuple[bool, Optional[str]]:
        """
        Validate export row count against format-specific limits.

        Args:
            row_count: Number of rows in dataset
            format: Export format

        Returns:
            Tuple of (is_valid, error_message)
        """
        limits = {
            ExportFormat.CSV: settings.csv_max_rows,
            ExportFormat.XLSX: settings.xlsx_max_rows,
            ExportFormat.PDF: settings.pdf_max_rows,
        }

        max_allowed = limits.get(format)
        if max_allowed is None:
            logger.warning(f"Export validation failed: Unknown format {format}")
            return False, f"Unknown format: {format}"

        if row_count > max_allowed:
            logger.warning(
                f"Export validation failed: Row limit exceeded. "
                f"Requested: {row_count}, Maximum: {max_allowed}, Format: {format.value}"
            )
            return False, (
                f"Requested dataset exceeds maximum rows for {format.value} format. "
                f"Requested: {row_count}, Maximum: {max_allowed}"
            )

        warning_threshold = int(max_allowed * 0.8)
        if row_count >= warning_threshold:
            logger.info(
                f"Export approaching row limit: {row_count}/{max_allowed} ({format.value})"
            )
            return True, f"Warning: Approaching row limit ({row_count}/{max_allowed})"

        return True, None

    def create_export_metadata(
        self,
        format: ExportFormat,
        report_type: str,
        row_count: int,
        start_date: date,
        end_date: date,
        generated_by: str,
    ) -> ExportMetadata:
        """Create export metadata for response."""
        return ExportMetadata(
            generated_at=datetime.now(),
            format=format,
            report_type=report_type,
            row_count=row_count,
            date_range=(start_date, end_date),
            generated_by=generated_by,
        )

    async def shutdown(self):
        """Shutdown the thread pool executor."""
        self.executor.shutdown(wait=True)

    async def generate_sales_pdf_report(
        self, sales_data: list, start_date: date, end_date: date, generated_by: str
    ) -> bytes:
        """
        Generate PDF report specifically for sales data with proper formatting.

        Args:
            sales_data: List of sales records
            start_date: Report start date
            end_date: Report end date
            generated_by: User who generated the report

        Returns:
            PDF bytes
        """
        try:
            formatted_data = []
            for sale in sales_data:
                formatted_data.append(
                    {
                        "Date": sale.get("Date", ""),
                        "Payments": sale.get("Payment Methods", ""),
                        "Total": sale.get("Grand Total", Decimal("0")),
                        "Gross Profit": sale.get("Gross Profit", Decimal("0")),
                        "Partner Share": sale.get("Partner Share", Decimal("0")),
                        "Net Profit": sale.get("Net Profit", Decimal("0")),
                        "Note": sale.get("Note", ""),
                    }
                )

            logger.info(
                f"Generating modernized sales PDF report: {len(sales_data)} records, "
                f"date range: {start_date} to {end_date}"
            )
            return await self.generate_pdf(
                data=formatted_data,
                title="Sales Report",
                start_date=start_date,
                end_date=end_date,
                generated_by=generated_by,
            )
        except Exception as e:
            logger.error(f"Sales PDF report generation failed: {str(e)}", exc_info=True)
            raise

    async def generate_partners_pdf_report(
        self, partners_data: list, start_date: date, end_date: date, generated_by: str
    ) -> bytes:
        """
        Generate PDF report specifically for partners data.
        """
        try:
            formatted_data = []
            for partner in partners_data:
                formatted_data.append(
                    {
                        "Partner": partner.get("name", ""),
                        "Invested": partner.get("invested_amount", Decimal("0")),
                        "Profit %": f"{partner.get('profit_percentage', Decimal('0'))}%",
                        "Distributed": partner.get("distributed_amount", Decimal("0")),
                        "Date": partner.get("distribution_date", ""),
                    }
                )

            logger.info(f"Generating partners PDF report: {len(partners_data)} records")
            return await self.generate_pdf(
                data=formatted_data,
                title="Partners Report",
                start_date=start_date,
                end_date=end_date,
                generated_by=generated_by,
            )
        except Exception as e:
            logger.error(
                f"Partners PDF report generation failed: {str(e)}", exc_info=True
            )
            raise

    async def generate_inventory_pdf_report(
        self, inventory_data: list, start_date: date, end_date: date, generated_by: str
    ) -> bytes:
        """
        Generate PDF report specifically for inventory movements.
        """
        try:
            formatted_data = []
            for movement in inventory_data:
                formatted_data.append(
                    {
                        "Product": movement.get("product_name", ""),
                        "Type": movement.get("movement_type", ""),
                        "Quantity": movement.get("quantity_delta", 0),
                        "Reason": movement.get("reason", ""),
                        "Date": movement.get("created_at", ""),
                    }
                )

            logger.info(
                f"Generating inventory PDF report: {len(inventory_data)} records"
            )
            return await self.generate_pdf(
                data=formatted_data,
                title="Inventory Movements Report",
                start_date=start_date,
                end_date=end_date,
                generated_by=generated_by,
            )
        except Exception as e:
            logger.error(
                f"Inventory PDF report generation failed: {str(e)}", exc_info=True
            )
            raise

    async def generate_dashboard_csv(
        self, data: list[dict], filename_prefix: str
    ) -> BytesIO:
        """Generate CSV export for dashboard chart data."""
        return await self.generate_csv(
            data=data,
            filename_prefix=filename_prefix,
            start_date=date.today(),
            end_date=date.today(),
        )

    async def generate_dashboard_xlsx(
        self, data: list[dict], filename_prefix: str
    ) -> BytesIO:
        """Generate Excel export for dashboard chart data."""
        return await self.generate_xlsx(
            data=data,
            filename_prefix=filename_prefix,
            start_date=date.today(),
            end_date=date.today(),
        )

    async def generate_dashboard_pdf(
        self, data: list[dict], title: str, generated_by: str = "system"
    ) -> bytes:
        """Generate PDF export for dashboard chart data."""
        return await self.generate_pdf(
            data=data,
            title=title,
            start_date=date.today(),
            end_date=date.today(),
            generated_by=generated_by,
        )

    async def generate_customer_statement_pdf(
        self,
        customer_data: dict,
        ledger_entries: list,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        generated_by: str = "system"
    ) -> bytes:
        """
        T029: Generate PDF statement for a customer.
        """
        try:
            formatted_entries = []
            for entry in ledger_entries:
                entry_type = entry.get("type", "")
                type_label = {
                    "SALE": "بيع",
                    "PAYMENT": "دفعة",
                    "RETURN": "مرتجع",
                }.get(entry_type, entry_type)

                formatted_entries.append({
                    "التاريخ": entry.get("created_at", ""),
                    "النوع": type_label,
                    "المبلغ": entry.get("amount", 0),
                    "ملاحظة": entry.get("note", "") or "-",
                })

            customer_name = customer_data.get("name", "عميل")
            summary = customer_data.get("summary", {})

            formatted_data = [
                {"العميل": customer_name},
                {"الهاتف": customer_data.get("phone", "-")},
                {"إجمالي المبيعات": summary.get("total_sales", 0)},
                {"إجمالي المدفوعات": summary.get("total_payments", 0)},
                {"إجمالي المرتجعات": summary.get("total_returns", 0)},
                {"الرصيد": summary.get("balance", 0)},
            ]

            title = f"كشف حساب - {customer_name}"
            logger.info(f"Generating customer statement PDF: {customer_name}")

            return await self.generate_pdf(
                data=formatted_entries,
                title=title,
                start_date=start_date or date.today(),
                end_date=end_date or date.today(),
                generated_by=generated_by,
            )
        except Exception as e:
            logger.error(f"Customer statement PDF generation failed: {str(e)}", exc_info=True)
            raise
