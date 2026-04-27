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
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Image, Spacer
from reportlab.pdfgen import canvas
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
    """Register Arabic fonts for PDF rendering, prioritizing compatibility."""
    import os
    fonts_registered = False

    try:
        # Get path to static fonts directory
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        static_fonts_dir = os.path.join(base_dir, "static", "fonts")
        
        cairo_regular = os.path.join(static_fonts_dir, "Cairo-Regular.ttf")
        cairo_bold = os.path.join(static_fonts_dir, "Cairo-Bold.ttf")

        # 1. Use system Arial/DejaVu as they are extremely reliable for Arabic PDF glyphs
        font_paths = [
            "/usr/share/fonts/msttcore/arial.ttf",
            "/usr/share/fonts/dejavu-sans-fonts/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/dejavu/DejaVuSans.ttf",
        ]

        bold_paths = [
            "/usr/share/fonts/msttcore/arialbd.ttf",
            "/usr/share/fonts/dejavu-sans-fonts/DejaVuSans-Bold.ttf",
        ]

        for font_path in font_paths:
            if os.path.exists(font_path):
                try:
                    # Register the reliable font as "Cairo" to satisfy style requirements
                    pdfmetrics.registerFont(TTFont("Cairo", font_path))
                    pdfmetrics.registerFont(TTFont("ArabicFont", font_path))
                    
                    # Register bold version
                    registered_bold = False
                    for b_path in bold_paths:
                        if os.path.exists(b_path):
                            pdfmetrics.registerFont(TTFont("Cairo-Bold", b_path))
                            registered_bold = True
                            break
                    
                    if not registered_bold:
                        pdfmetrics.registerFont(TTFont("Cairo-Bold", font_path))
                        
                    fonts_registered = True
                    logger.info(f"Registered high-compatibility font as Cairo: {font_path}")
                    break
                except Exception as e:
                    logger.error(f"Failed to register compatible font: {e}")

        # 2. Fallback to embedded Cairo only if system fonts failed (Cairo often has CMAP issues)
        if not fonts_registered and os.path.exists(cairo_regular):
            try:
                pdfmetrics.registerFont(TTFont("Cairo", cairo_regular))
                pdfmetrics.registerFont(TTFont("ArabicFont", cairo_regular))
                if os.path.exists(cairo_bold):
                    pdfmetrics.registerFont(TTFont("Cairo-Bold", cairo_bold))
                else:
                    pdfmetrics.registerFont(TTFont("Cairo-Bold", cairo_regular))
                fonts_registered = True
            except Exception as e:
                logger.error(f"Failed to register embedded Cairo: {e}")

    except Exception as e:
        logger.error(f"Font registration system error: {e}")


_register_arabic_fonts()
 
 
# Standard Report Aesthetics (Blue Theme)
BORDER_COLOR = colors.HexColor("#2F5597")  # Dark Blue
HEADER_BG_COLOR = colors.HexColor("#2F5597")  # Dark Blue
HEADER_TEXT_COLOR = colors.white
STRIPE_COLOR = colors.HexColor("#D9E1F2")  # Light Blue
 
 
def get_asset_path(filename: str) -> str:
    """Get absolute path to a static image asset."""
    import os
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    return os.path.join(base_dir, "static", "images", filename)
 
 
def draw_report_header(canvas, doc, title: str, meta_data: dict = None):
    """Draw the standardized branded header with dual logos and dynamic fields."""
    import os
    canvas.saveState()
    width, height = landscape(letter)
 
    # 1. Dual Logos
    new_civ_logo = get_asset_path("new_civilization.png")
    rayon_logo = get_asset_path("rayon_energy.png")
 
    if os.path.exists(new_civ_logo):
        canvas.drawImage(new_civ_logo, 40, height - 70, width=120, height=50, preserveAspectRatio=True, mask='auto')
 
    if os.path.exists(rayon_logo):
        canvas.drawImage(rayon_logo, width - 160, height - 70, width=120, height=50, preserveAspectRatio=True, mask='auto')
 
    # 2. Centered Title
    registered_fonts = pdfmetrics.getRegisteredFontNames()
    title_font = "Cairo-Bold" if "Cairo-Bold" in registered_fonts else "Helvetica-Bold"
    canvas.setFont(title_font, 18)
    
    pdf_title = prepare_cell_value(title) if is_arabic_text(title) else title
    canvas.drawCentredString(width / 2, height - 40, pdf_title)
 
    # 3. Metadata Section (Dynamic Fields)
    meta_font = "Cairo" if "Cairo" in registered_fonts else "Helvetica"
    canvas.setFont(meta_font, 9)
    
    # Date and Page
    date_str = datetime.now().strftime("%Y-%m-%d")
    canvas.drawString(40, height - 90, prepare_cell_value(f"التاريخ: {date_str}"))
    canvas.drawRightString(width - 40, height - 90, prepare_cell_value(f"الصفحة: {doc.page}"))
 
    # Dynamic fields row (RTL flow)
    if meta_data:
        y_pos = height - 105
        # Start from the right margin
        x_pos = width - 40
        for label, value in meta_data.items():
            if value:
                field_text = f"{label}: {value}"
                # Use drawRightString for RTL alignment
                canvas.drawRightString(x_pos, y_pos, prepare_cell_value(field_text))
                x_pos -= 180  # Horizontal spacing to the left
 
    # 4. Blue line separator
    canvas.setStrokeColor(BORDER_COLOR)
    canvas.setLineWidth(1.5)
    canvas.line(40, height - 115, width - 40, height - 115)
 
    canvas.restoreState()
 
 
def draw_report_footer(canvas, doc):
    """Draw the standardized footer with signature labels."""
    canvas.saveState()
    width, height = landscape(letter)
    
    registered_fonts = pdfmetrics.getRegisteredFontNames()
    footer_font = "Cairo-Bold" if "Cairo-Bold" in registered_fonts else "Helvetica-Bold"
    canvas.setFont(footer_font, 10)
 
    # Fixed Arabic labels
    canvas.drawRightString(width - 50, 60, prepare_cell_value("مدير المبيعات:"))
    canvas.drawRightString(width - 50, 40, prepare_cell_value("التوقيع:"))
 
    canvas.restoreState()
 
 
class ExportService:
    """Service for generating export files in various formats."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.executor = ThreadPoolExecutor(max_workers=4)



    def _generate_xlsx_sync(self, data: list[dict], title: str = "Report", meta_data: dict = None) -> BytesIO:
        """Synchronous XLSX generation with branded header and Arabic support."""
        try:
            import os
            output = BytesIO()
            df = pd.DataFrame(data)
 
            with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
                # Start data table at row 7 (index 6) to leave space for branded header (T013)
                df.to_excel(
                    writer, index=False, sheet_name="Report", float_format="%.4f", startrow=6
                )
 
                workbook = writer.book
                worksheet = writer.sheets["Report"]
                
                # Set sheet to Right-to-Left (T032)
                worksheet.right_to_left() 
                # 1. Logos (T011)
                new_civ_logo = get_asset_path("new_civilization.png")
                rayon_logo = get_asset_path("rayon_energy.png")
 
                if os.path.exists(new_civ_logo):
                    worksheet.insert_image("A1", new_civ_logo, {"x_scale": 0.4, "y_scale": 0.4})
                
                if os.path.exists(rayon_logo):
                    # Insert right logo around column F/G
                    worksheet.insert_image("F1", rayon_logo, {"x_scale": 0.4, "y_scale": 0.4})
 
                # 2. Header Info (T012)
                title_format = workbook.add_format({"bold": True, "font_size": 16, "align": "center"})
                meta_format = workbook.add_format({"font_size": 10})
                
                # Center title across columns
                num_cols = len(df.columns)
                end_col = chr(ord('A') + max(0, num_cols - 1))
                worksheet.merge_range(f"A3:{end_col}3", title, title_format)
                
                # Date and dynamic metadata
                date_str = datetime.now().strftime("%Y-%m-%d")
                worksheet.write("A5", prepare_cell_value(f"التاريخ: {date_str}", for_pdf=False), meta_format)                
                if meta_data:
                    row_idx = 5
                    col_idx = 0
                    for label, value in meta_data.items():
                        if value:
                            worksheet.write(row_idx, col_idx, prepare_cell_value(f"{label}: {value}", for_pdf=False), meta_format)
                            col_idx += 2
                            if col_idx >= num_cols:
                                col_idx = 0
                                row_idx += 1
 
                # 3. Table Formatting (T009/T013)
                header_format = workbook.add_format({
                    "bold": True,
                    "bg_color": "#2F5597",
                    "font_color": "white",
                    "border": 1,
                    "align": "center"
                })
 
                # Re-apply headers with formatting
                for col_num, value in enumerate(df.columns.values):
                    worksheet.write(6, col_num, prepare_cell_value(value, for_pdf=False), header_format)
 
                # Configure columns and apply number formats
                num_format = workbook.add_format({'num_format': '#,##0.00', 'align': 'center', 'border': 1})
                if not df.empty:
                    for idx, col in enumerate(df.columns):
                        # Apply number format if column is numeric
                        is_numeric = pd.api.types.is_numeric_dtype(df[col])
                        if is_numeric:
                            # Rewrite column data with number format
                            for row_idx, value in enumerate(df[col]):
                                worksheet.write(row_idx + 7, idx, value, num_format)
                        
                        col_data_max = df[col].astype(str).str.len().max()
                        if pd.isna(col_data_max):
                            col_data_max = 0
                        max_len = max(col_data_max, len(str(col))) + 4
                        worksheet.set_column(idx, idx, max_len)
 
            output.seek(0)
            return output
        except Exception as e:
            logger.error(f"XLSX export generation failed: {str(e)}", exc_info=True)
            raise
 
    async def generate_xlsx(
        self, 
        data: list[dict], 
        filename_prefix: str, 
        start_date: date, 
        end_date: date,
        title: str = "Report",
        meta_data: Optional[dict] = None
    ) -> BytesIO:
        """
        Generate Excel export using pandas with xlsxwriter.
 
        Args:
            data: List of dictionaries with export data
            filename_prefix: Prefix for filename
            start_date: Report start date
            end_date: Report end date
            title: Report title
            meta_data: Optional dictionary for header fields
 
        Returns:
            BytesIO buffer containing XLSX data
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.executor, self._generate_xlsx_sync, data, title, meta_data)


    async def generate_pdf(
        self,
        data: list[dict],
        title: str,
        start_date: date,
        end_date: date,
        generated_by: str,
        meta_data: Optional[dict] = None,
    ) -> bytes:
        """
        Generate PDF export using ReportLab.
 
        Args:
            data: List of dictionaries with export data
            title: Report title
            start_date: Report start date
            end_date: Report end date
            generated_by: User who generated the report
            meta_data: Optional dictionary for dynamic header fields
 
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
            meta_data,
        )
 
    def _generate_pdf_sync(
        self,
        data: list[dict],
        title: str,
        start_date: date,
        end_date: date,
        generated_by: str,
        meta_data: Optional[dict] = None,
    ) -> bytes:
        """Synchronous PDF generation with branded template and Arabic support."""
        try:
            import os
            output = BytesIO()
            # Standard margins for branded template
            doc = SimpleDocTemplate(
                output, 
                pagesize=landscape(letter),
                topMargin=135,    # Space for header
                bottomMargin=90,  # Space for footer
                leftMargin=40,
                rightMargin=40
            )
            elements = []
 
            if data:
                # Reverse columns for RTL support in PDF (T033)
                headers = list(data[0].keys())
                headers.reverse()
                
                # Reshape headers for Arabic
                processed_headers = [prepare_cell_value(h) if is_arabic_text(h) else h for h in headers]
                table_data = [processed_headers]
 
                for row in data:
                    table_row = []
                    for key in headers:
                        value = row[key]
                        table_row.append(prepare_cell_value(value))
                    table_data.append(table_row)
 
                # Calculate dynamic column widths
                total_width = landscape(letter)[0] - 80
                col_width = total_width / len(headers)
                table = Table(table_data, colWidths=[col_width] * len(headers), repeatRows=1)
 
                # Blue Themed Table Style (T009)
                ts = TableStyle([
                    ("BACKGROUND", (0, 0), (-1, 0), HEADER_BG_COLOR),
                    ("TEXTCOLOR", (0, 0), (-1, 0), HEADER_TEXT_COLOR),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("FONTSIZE", (0, 0), (-1, 0), 10),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                    ("TOPPADDING", (0, 0), (-1, 0), 12),
                    ("GRID", (0, 0), (-1, -1), 0.5, BORDER_COLOR),
                    ("FONTSIZE", (0, 1), (-1, -1), 9),
                    # Alternating Row Colors (Stripe)
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, STRIPE_COLOR]),
                ])
 
                # Font handling
                registered_fonts = pdfmetrics.getRegisteredFontNames()
                header_font = "Cairo-Bold" if "Cairo-Bold" in registered_fonts else "Helvetica-Bold"
                body_font = "Cairo" if "Cairo" in registered_fonts else "Helvetica"
                
                ts.add("FONTNAME", (0, 0), (-1, 0), header_font)
                ts.add("FONTNAME", (0, 1), (-1, -1), body_font)
                
                table.setStyle(ts)
                elements.append(table)
            else:
                styles = getSampleStyleSheet()
                msg = prepare_cell_value("لا توجد بيانات متاحة") if is_arabic_text("لا توجد بيانات متاحة") else "No data available"
                elements.append(Paragraph(msg, styles["Normal"]))
 
            # Add Stamp flowable at the end (T006)
            stamp_path = get_asset_path("stamp.png")
            if os.path.exists(stamp_path):
                elements.append(Spacer(1, 30))
                # Right aligned stamp
                stamp_img = Image(stamp_path, width=80, height=80, mask='auto')
                # Wrap in a small table for alignment if needed, or just append
                elements.append(stamp_img)
 
            # Build document with header/footer callbacks (T008)
            def header_footer_callback(canvas, doc):
                draw_report_header(canvas, doc, title, meta_data)
                draw_report_footer(canvas, doc)
 
            doc.build(elements, onFirstPage=header_footer_callback, onLaterPages=header_footer_callback)
            
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
                        "التاريخ": sale.get("Date", ""),
                        "المدفوعات": sale.get("Payment Methods", ""),
                        "الإجمالي": sale.get("Grand Total", Decimal("0")),
                        "إجمالي الربح": sale.get("Gross Profit", Decimal("0")),
                        "حصة الشريك": sale.get("Partner Share", Decimal("0")),
                        "صافي الربح": sale.get("Net Profit", Decimal("0")),
                        "ملاحظة": sale.get("Note", ""),
                    }
                )

            logger.info(
                f"Generating modernized sales PDF report: {len(sales_data)} records, "
                f"date range: {start_date} to {end_date}"
            )
            return await self.generate_pdf(
                data=formatted_data,
                title="تقرير المبيعات",
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
                        "الشريك": partner.get("name", ""),
                        "المبلغ المستثمر": partner.get("invested_amount", Decimal("0")),
                        "نسبة الربح %": f"{partner.get('profit_percentage', Decimal('0'))}%",
                        "المبلغ الموزع": partner.get("distributed_amount", Decimal("0")),
                        "التاريخ": partner.get("distribution_date", ""),
                    }
                )

            logger.info(f"Generating partners PDF report: {len(partners_data)} records")
            return await self.generate_pdf(
                data=formatted_data,
                title="تقرير الشركاء",
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
                        "المنتج": movement.get("product_name", ""),
                        "النوع": movement.get("movement_type", ""),
                        "الكمية": movement.get("quantity_delta", 0),
                        "السبب": movement.get("reason", ""),
                        "التاريخ": movement.get("created_at", ""),
                    }
                )

            logger.info(
                f"Generating inventory PDF report: {len(inventory_data)} records"
            )
            return await self.generate_pdf(
                data=formatted_data,
                title="تقرير حركة المخزون",
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
        # Note: CSV support removed as per user request. 
        # This method is kept for API compatibility if needed but redirects to XLSX or errors out.
        return await self.generate_dashboard_xlsx(data, filename_prefix)

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

                created_at = entry.get("created_at", "")
                if isinstance(created_at, (date, datetime)):
                    date_str = created_at.strftime("%Y-%m-%d")
                else:
                    # Try to parse iso string
                    try:
                        date_str = datetime.fromisoformat(str(created_at)).strftime("%Y-%m-%d")
                    except:
                        date_str = str(created_at)

                formatted_entries.append({
                    "التاريخ": date_str,
                    "النوع": type_label,
                    "المبلغ": entry.get("amount", 0),
                    "ملاحظة": entry.get("note", "") or "-",
                })

            customer_name = customer_data.get("name", "عميل")
            summary = customer_data.get("summary", {})

            title = f"كشف حساب عميل - {customer_name}"
            logger.info(f"Generating customer statement PDF: {customer_name}")
 
            meta_data = {
                "العميل": customer_name,
                "إجمالي المبيعات": summary.get("total_sales", 0),
                "إجمالي المدفوعات": summary.get("total_payments", 0),
                "إجمالي المرتجعات": summary.get("total_returns", 0),
                "الرصيد": summary.get("balance", 0),
            }
 
            return await self.generate_pdf(
                data=formatted_entries,
                title=title,
                start_date=start_date or date.today(),
                end_date=end_date or date.today(),
                generated_by=generated_by,
                meta_data=meta_data
            )
        except Exception as e:
            logger.error(f"Customer statement PDF generation failed: {str(e)}", exc_info=True)
            raise

    async def generate_customer_statement_xlsx(
        self,
        customer_data: dict,
        ledger_entries: list,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> BytesIO:
        """
        Generate Excel statement for a customer.
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

                created_at = entry.get("created_at", "")
                if isinstance(created_at, (date, datetime)):
                    date_str = created_at.strftime("%Y-%m-%d")
                else:
                    try:
                        date_str = datetime.fromisoformat(str(created_at)).strftime("%Y-%m-%d")
                    except:
                        date_str = str(created_at)

                formatted_entries.append({
                    "التاريخ": date_str,
                    "النوع": type_label,
                    "المبلغ": float(entry.get("amount", 0)),
                    "ملاحظة": entry.get("note", "") or "-",
                })

            customer_name = customer_data.get("name", "عميل")
            summary = customer_data.get("summary", {})
            
            meta_data = {
                "العميل": customer_name,
                "إجمالي المبيعات": float(summary.get("total_sales", 0)),
                "إجمالي المدفوعات": float(summary.get("total_payments", 0)),
                "إجمالي المرتجعات": float(summary.get("total_returns", 0)),
                "الرصيد": float(summary.get("balance", 0)),
            }

            return await self.generate_xlsx(
                data=formatted_entries,
                filename_prefix=f"customer_statement_{customer_name}",
                start_date=start_date or date.today(),
                end_date=end_date or date.today(),
                title=f"كشف حساب عميل - {customer_name}",
                meta_data=meta_data
            )
        except Exception as e:
            logger.error(f"Customer statement XLSX generation failed: {str(e)}", exc_info=True)
            raise

    async def generate_supplier_statement_pdf(
        self,
        supplier_data: dict,
        ledger_entries: list,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        generated_by: str = "system"
    ) -> bytes:
        """
        Generate PDF statement for a supplier.
        """
        try:
            formatted_entries = []
            for entry in ledger_entries:
                entry_type = entry.get("type", "")
                type_label = {
                    "PURCHASE": "شراء",
                    "PAYMENT": "دفعة",
                    "RETURN": "مرتجع",
                }.get(entry_type, entry_type)

                formatted_entries.append({
                    "التاريخ": entry.get("created_at", "").strftime("%Y-%m-%d") if isinstance(entry.get("created_at"), (date, datetime)) else str(entry.get("created_at", "")),
                    "النوع": type_label,
                    "المبلغ": entry.get("amount", 0),
                    "ملاحظة": entry.get("note", "") or "-",
                })

            supplier_name = supplier_data.get("supplier", {}).get("name", "مورد")
            summary = supplier_data.get("summary", {})

            title = f"كشف حساب مورد - {supplier_name}"
            logger.info(f"Generating supplier statement PDF: {supplier_name}")

            meta_data = {
                "المورد": supplier_name,
                "إجمالي المشتريات": summary.get("total_purchases", 0),
                "إجمالي المدفوعات": summary.get("total_payments", 0),
                "الرصيد": summary.get("balance", 0),
            }

            return await self.generate_pdf(
                data=formatted_entries,
                title=title,
                start_date=start_date or date.today(),
                end_date=end_date or date.today(),
                generated_by=generated_by,
                meta_data=meta_data
            )
        except Exception as e:
            logger.error(f"Supplier statement PDF generation failed: {str(e)}", exc_info=True)
            raise

    async def generate_supplier_statement_xlsx(
        self,
        supplier_data: dict,
        ledger_entries: list,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> BytesIO:
        """
        Generate Excel statement for a supplier.
        """
        try:
            formatted_entries = []
            for entry in ledger_entries:
                entry_type = entry.get("type", "")
                type_label = {
                    "PURCHASE": "شراء",
                    "PAYMENT": "دفعة",
                    "RETURN": "مرتجع",
                }.get(entry_type, entry_type)

                formatted_entries.append({
                    "التاريخ": entry.get("created_at", "").strftime("%Y-%m-%d") if isinstance(entry.get("created_at"), (date, datetime)) else str(entry.get("created_at", "")),
                    "النوع": type_label,
                    "المبلغ": float(entry.get("amount", 0)),
                    "ملاحظة": entry.get("note", "") or "-",
                })

            supplier_name = supplier_data.get("supplier", {}).get("name", "مورد")
            summary = supplier_data.get("summary", {})
            
            meta_data = {
                "المورد": supplier_name,
                "إجمالي المشتريات": float(summary.get("total_purchases", 0)),
                "إجمالي المدفوعات": float(summary.get("total_payments", 0)),
                "الرصيد": float(summary.get("balance", 0)),
            }

            return await self.generate_xlsx(
                data=formatted_entries,
                filename_prefix=f"supplier_statement_{supplier_name}",
                start_date=start_date or date.today(),
                end_date=end_date or date.today(),
                title=f"كشف حساب مورد - {supplier_name}",
                meta_data=meta_data
            )
        except Exception as e:
            logger.error(f"Supplier statement XLSX generation failed: {str(e)}", exc_info=True)
            raise

    async def generate_sale_invoice_pdf(
        self,
        sale_data: dict,
        generated_by: str = "system"
    ) -> bytes:
        """
        Generate a professional invoice PDF for a single sale.
        """
        try:
            items = sale_data.get("items", [])
            formatted_items = []
            for item in items:
                # Handle both dict (from API response) and Pydantic objects (from internal calls)
                is_dict = isinstance(item, dict)
                formatted_items.append({
                    "المنتج": item.get("product_name", "") if is_dict else getattr(item, "product_name", ""),
                    "الكمية": item.get("quantity", 0) if is_dict else getattr(item, "quantity", 0),
                    "سعر الوحدة": item.get("unit_price", 0) if is_dict else getattr(item, "unit_price", 0),
                    "الإجمالي": item.get("line_total", 0) if is_dict else getattr(item, "line_total", 0),
                })

            sale_id = sale_data.get("id", "")
            short_id = sale_id[:8].upper() if sale_id else "N/A"
            customer_name = sale_data.get("customer_name") or "عميل نقدي"
            
            title = f"فاتورة مبيعات #{short_id}"
            
            meta_data = {
                "رقم الفاتورة": short_id,
                "العميل": customer_name,
                "طريقة الدفع": sale_data.get("payment_method_name", ""),
                "الإجمالي": sale_data.get("grand_total", 0),
            }

            # Add more specific metadata if needed (e.g. fees, VAT)
            if (sale_data.get("fees_total") or 0) > 0:
                meta_data["الرسوم"] = sale_data.get("fees_total")
            
            if (sale_data.get("vat_total") or 0) > 0:
                meta_data["ضريبة القيمة المضافة"] = sale_data.get("vat_total")

            # We use landscape letter as in other reports for consistency
            # but a portrait A4 might be more traditional for invoices.
            # Keeping landscape for now to reuse draw_report_header/footer.
            return await self.generate_pdf(
                data=formatted_items,
                title=title,
                start_date=date.today(),
                end_date=date.today(),
                generated_by=generated_by,
                meta_data=meta_data
            )
        except Exception as e:
            logger.error(f"Sale invoice PDF generation failed: {str(e)}", exc_info=True)
            raise
