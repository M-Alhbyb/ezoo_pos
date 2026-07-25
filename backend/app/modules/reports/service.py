from datetime import datetime, date
from decimal import Decimal
from typing import List, Optional, Dict, Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.reports.sales_queries import (
    get_sales_count as _get_sales_count,
    get_sales_report as _get_sales_report,
    get_sales_export_data as _get_sales_export_data,
)
from app.modules.reports.partner_queries import (
    get_partners_count as _get_partners_count,
    get_partners_report as _get_partners_report,
    get_partners_export_data as _get_partners_export_data,
)
from app.modules.reports.inventory_queries import (
    get_inventory_count as _get_inventory_count,
    get_inventory_report as _get_inventory_report,
    get_inventory_export_data as _get_inventory_export_data,
)
from app.modules.reports.supplier_queries import (
    get_supplier_summary_report as _get_supplier_summary_report,
    get_supplier_statement as _get_supplier_statement,
)
from app.schemas.report import (
    SalesReport,
    PartnerReport,
    InventoryReport,
)


class ReportService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_sales_count(self, start_date: date, end_date: date) -> int:
        return await _get_sales_count(self.db, start_date, end_date)

    async def get_partners_count(self, start_date: date, end_date: date) -> int:
        return await _get_partners_count(self.db, start_date, end_date)

    async def get_inventory_count(self, start_date: date, end_date: date) -> int:
        return await _get_inventory_count(self.db, start_date, end_date)

    async def get_sales_report(
        self,
        start_date: Optional[datetime],
        end_date: Optional[datetime],
        page: int = 1,
        page_size: int = 50,
    ) -> SalesReport:
        return await _get_sales_report(self.db, start_date, end_date, page, page_size)

    async def get_partners_report(
        self,
        start_date: Optional[datetime],
        end_date: Optional[datetime],
        page: int = 1,
        page_size: int = 50,
    ) -> PartnerReport:
        return await _get_partners_report(self.db, start_date, end_date, page, page_size)

    async def get_inventory_report(
        self,
        start_date: Optional[datetime],
        end_date: Optional[datetime],
        page: int = 1,
        page_size: int = 50,
    ) -> InventoryReport:
        return await _get_inventory_report(self.db, start_date, end_date, page, page_size)

    async def get_sales_export_data(
        self, start_date: Optional[date], end_date: Optional[date]
    ) -> List[Dict[str, Any]]:
        return await _get_sales_export_data(self.db, start_date, end_date)

    async def get_partners_export_data(
        self, start_date: Optional[date], end_date: Optional[date]
    ) -> List[Dict[str, Any]]:
        return await _get_partners_export_data(self.db, start_date, end_date)

    async def get_inventory_export_data(
        self, start_date: Optional[date], end_date: Optional[date]
    ) -> List[Dict[str, Any]]:
        return await _get_inventory_export_data(self.db, start_date, end_date)

    async def get_supplier_summary_report(
        self,
    ) -> List[Dict[str, Any]]:
        return await _get_supplier_summary_report(self.db)

    async def get_supplier_statement(
        self,
        supplier_id: UUID,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> Dict[str, Any]:
        return await _get_supplier_statement(self.db, supplier_id, start_date, end_date)
