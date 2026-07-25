from datetime import date, datetime
from decimal import Decimal
from io import BytesIO
from typing import Optional
import logging

from .export_generators import generate_xlsx, generate_pdf

logger = logging.getLogger(__name__)


async def generate_sales_pdf_report(
    db, sales_data: list, start_date: date, end_date: date, generated_by: str
) -> bytes:
    """Generate PDF report specifically for sales data with proper formatting."""
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
        return await generate_pdf(
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
    db, partners_data: list, start_date: date, end_date: date, generated_by: str
) -> bytes:
    """Generate PDF report specifically for partners data."""
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
        return await generate_pdf(
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
    db, inventory_data: list, start_date: date, end_date: date, generated_by: str
) -> bytes:
    """Generate PDF report specifically for inventory movements."""
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
        return await generate_pdf(
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
    db, data: list[dict], filename_prefix: str
) -> BytesIO:
    """Generate CSV export for dashboard chart data. Redirects to XLSX."""
    return await generate_dashboard_xlsx(db, data, filename_prefix)


async def generate_dashboard_xlsx(
    db, data: list[dict], filename_prefix: str
) -> BytesIO:
    """Generate Excel export for dashboard chart data."""
    return await generate_xlsx(
        data=data,
        filename_prefix=filename_prefix,
        start_date=date.today(),
        end_date=date.today(),
    )


async def generate_dashboard_pdf(
    db, data: list[dict], title: str, generated_by: str = "system"
) -> bytes:
    """Generate PDF export for dashboard chart data."""
    return await generate_pdf(
        data=data,
        title=title,
        start_date=date.today(),
        end_date=date.today(),
        generated_by=generated_by,
    )


async def generate_customer_statement_pdf(
    db,
    customer_data: dict,
    ledger_entries: list,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    generated_by: str = "system",
) -> bytes:
    """Generate PDF statement for a customer."""
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

        return await generate_pdf(
            data=formatted_entries,
            title=title,
            start_date=start_date or date.today(),
            end_date=end_date or date.today(),
            generated_by=generated_by,
            meta_data=meta_data,
        )
    except Exception as e:
        logger.error(f"Customer statement PDF generation failed: {str(e)}", exc_info=True)
        raise


async def generate_customer_statement_xlsx(
    db,
    customer_data: dict,
    ledger_entries: list,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
) -> BytesIO:
    """Generate Excel statement for a customer."""
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

        return await generate_xlsx(
            data=formatted_entries,
            filename_prefix=f"customer_statement_{customer_name}",
            start_date=start_date or date.today(),
            end_date=end_date or date.today(),
            title=f"كشف حساب عميل - {customer_name}",
            meta_data=meta_data,
        )
    except Exception as e:
        logger.error(f"Customer statement XLSX generation failed: {str(e)}", exc_info=True)
        raise


async def generate_supplier_statement_pdf(
    db,
    supplier_data: dict,
    ledger_entries: list,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    generated_by: str = "system",
) -> bytes:
    """Generate PDF statement for a supplier."""
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

        return await generate_pdf(
            data=formatted_entries,
            title=title,
            start_date=start_date or date.today(),
            end_date=end_date or date.today(),
            generated_by=generated_by,
            meta_data=meta_data,
        )
    except Exception as e:
        logger.error(f"Supplier statement PDF generation failed: {str(e)}", exc_info=True)
        raise


async def generate_supplier_statement_xlsx(
    db,
    supplier_data: dict,
    ledger_entries: list,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
) -> BytesIO:
    """Generate Excel statement for a supplier."""
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

        return await generate_xlsx(
            data=formatted_entries,
            filename_prefix=f"supplier_statement_{supplier_name}",
            start_date=start_date or date.today(),
            end_date=end_date or date.today(),
            title=f"كشف حساب مورد - {supplier_name}",
            meta_data=meta_data,
        )
    except Exception as e:
        logger.error(f"Supplier statement XLSX generation failed: {str(e)}", exc_info=True)
        raise


async def generate_sale_invoice_pdf(
    db,
    sale_data: dict,
    generated_by: str = "system",
) -> bytes:
    """Generate a professional invoice PDF for a single sale."""
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

        return await generate_pdf(
            data=formatted_items,
            title=title,
            start_date=date.today(),
            end_date=date.today(),
            generated_by=generated_by,
            meta_data=meta_data,
        )
    except Exception as e:
        logger.error(f"Sale invoice PDF generation failed: {str(e)}", exc_info=True)
        raise
