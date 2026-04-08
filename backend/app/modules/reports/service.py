from datetime import datetime, date
from decimal import Decimal
from typing import List, Optional, Dict, Any
from uuid import UUID

from sqlalchemy import select, func, cast, Date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.sale import Sale
from app.models.partner_distribution import PartnerDistribution
from app.models.partner import Partner
from app.models.inventory_log import InventoryLog
from app.schemas.report import (
    SalesReport,
    SalesSummaryGroup,
    PartnerReport,
    PartnerPayoutSummary,
    InventoryReport,
    InventoryMovement,
)


class ReportService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_sales_count(self, start_date: date, end_date: date) -> int:
        """
        Count total sales records in date range for export validation.
        """
        stmt = select(func.count(Sale.id))
        if start_date:
            stmt = stmt.where(Sale.created_at >= start_date)
        if end_date:
            stmt = stmt.where(Sale.created_at <= end_date)

        result = await self.db.execute(stmt)
        count = result.scalar()
        return count or 0


    async def get_partners_count(self, start_date: date, end_date: date) -> int:
        """
        Count total partner distributions in date range for export validation.
        """
        stmt = select(func.count(PartnerDistribution.id))
        if start_date:
            stmt = stmt.where(PartnerDistribution.distribution_date >= start_date)
        if end_date:
            stmt = stmt.where(PartnerDistribution.distribution_date <= end_date)

        result = await self.db.execute(stmt)
        count = result.scalar()
        return count or 0

    async def get_inventory_count(self, start_date: date, end_date: date) -> int:
        """
        Count total inventory movements in date range for export validation.
        """
        stmt = select(func.count(InventoryLog.id))
        if start_date:
            stmt = stmt.where(InventoryLog.created_at >= start_date)
        if end_date:
            stmt = stmt.where(InventoryLog.created_at <= end_date)

        result = await self.db.execute(stmt)
        count = result.scalar()
        return count or 0

    async def get_sales_report(
        self, start_date: Optional[datetime], end_date: Optional[datetime], page: int = 1, page_size: int = 50
    ) -> SalesReport:
        """
        Aggregate sales statistics with daily breakdown.
        """
        stmt = select(Sale)
        if start_date:
            stmt = stmt.where(Sale.created_at >= start_date)
        if end_date:
            stmt = stmt.where(Sale.created_at <= end_date)

        # Totals for summary cards (not paginated)
        total_stmt = select(
            func.sum(Sale.grand_total).label("revenue"),
            func.sum(Sale.total_cost).label("cost"),
            func.sum(Sale.profit).label("profit"),
            func.count(Sale.id).label("count")
        )
        if start_date:
            total_stmt = total_stmt.where(Sale.created_at >= start_date)
        if end_date:
            total_stmt = total_stmt.where(Sale.created_at <= end_date)
            
        total_result = await self.db.execute(total_stmt)
        total_row = total_result.one()
        
        # Daily breakdown via SQL aggregation for efficiency (Paginated)
        group_stmt = (
            select(
                cast(Sale.created_at, Date).label("day"),
                func.count(Sale.id).label("count"),
                func.sum(Sale.grand_total).label("revenue"),
                func.sum(Sale.total_cost).label("cost"),
                func.sum(Sale.profit).label("profit"),
            )
            .group_by("day")
            .order_by("day")
        )
        if start_date:
            group_stmt = group_stmt.where(Sale.created_at >= start_date)
        if end_date:
            group_stmt = group_stmt.where(Sale.created_at <= end_date)

        # Get total count of groups for pagination
        count_stmt = select(func.count()).select_from(group_stmt.alias("subquery"))
        count_result = await self.db.execute(count_stmt)
        total_groups = count_result.scalar() or 0

        # Apply pagination
        group_stmt = group_stmt.limit(page_size).offset((page - 1) * page_size)

        group_result = await self.db.execute(group_stmt)
        daily_breakdown = [
            SalesSummaryGroup(
                date=row.day,
                count=row.count,
                revenue=row.revenue or Decimal("0.00"),
                cost=row.cost or Decimal("0.00"),
                profit=row.profit or Decimal("0.00"),
            )
            for row in group_result
        ]

        return SalesReport(
            total_revenue=total_row.revenue or Decimal("0.00"),
            total_cost=total_row.cost or Decimal("0.00"),
            total_profit=total_row.profit or Decimal("0.00"),
            sales_count=total_row.count or 0,
            daily_breakdown=daily_breakdown,
            total=total_groups,
            page=page,
            page_size=page_size
        )


    async def get_partners_report(
        self, start_date: Optional[datetime], end_date: Optional[datetime], page: int = 1, page_size: int = 50
    ) -> PartnerReport:
        """
        Aggregate partner distributions grouped by partner.
        """
        payout_stmt = (
            select(
                Partner.id.label("partner_id"),
                Partner.name.label("partner_name"),
                func.sum(PartnerDistribution.payout_amount).label("total_payout"),
            )
            .join(Partner, Partner.id == PartnerDistribution.partner_id)
            .group_by(Partner.id, Partner.name)
        )

        if start_date:
            payout_stmt = payout_stmt.where(
                PartnerDistribution.created_at >= start_date
            )
        if end_date:
            payout_stmt = payout_stmt.where(PartnerDistribution.created_at <= end_date)

        # Get total for pagination
        count_stmt = select(func.count()).select_from(payout_stmt.alias("subquery"))
        count_result = await self.db.execute(count_stmt)
        total_count = count_result.scalar() or 0

        # Apply pagination
        payout_stmt = payout_stmt.limit(page_size).offset((page - 1) * page_size)

        result = await self.db.execute(payout_stmt)
        payouts_by_partner = [
            PartnerPayoutSummary(
                partner_id=row.partner_id,
                partner_name=row.partner_name,
                total_payout=row.total_payout or Decimal("0.00"),
            )
            for row in result
        ]

        # Overall total payout (not paginated)
        total_payout_stmt = select(func.sum(PartnerDistribution.payout_amount))
        if start_date:
            total_payout_stmt = total_payout_stmt.where(PartnerDistribution.created_at >= start_date)
        if end_date:
            total_payout_stmt = total_payout_stmt.where(PartnerDistribution.created_at <= end_date)
            
        total_payout_res = await self.db.execute(total_payout_stmt)
        overall_total_payout = total_payout_res.scalar() or Decimal("0.00")

        return PartnerReport(
            total_payout=overall_total_payout, 
            payouts_by_partner=payouts_by_partner,
            total=total_count,
            page=page,
            page_size=page_size
        )

    async def get_inventory_report(
        self, start_date: Optional[datetime], end_date: Optional[datetime], page: int = 1, page_size: int = 50
    ) -> InventoryReport:
        """
        Aggregate inventory movements by reason.
        """
        stmt = select(
            InventoryLog.reason,
            func.sum(InventoryLog.delta).label("total_delta"),
            func.count(InventoryLog.id).label("movement_count"),
        ).group_by(InventoryLog.reason)

        if start_date:
            stmt = stmt.where(InventoryLog.created_at >= start_date)
        if end_date:
            stmt = stmt.where(InventoryLog.created_at <= end_date)

        # Get total for pagination
        count_stmt = select(func.count()).select_from(stmt.alias("subquery"))
        count_result = await self.db.execute(count_stmt)
        total_count = count_result.scalar() or 0

        # Apply pagination
        stmt = stmt.limit(page_size).offset((page - 1) * page_size)

        result = await self.db.execute(stmt)
        movements = []
        total_delta_count = 0

        for row in result:
            total_delta_count += row.movement_count
            movements.append(
                InventoryMovement(
                    reason=row.reason,
                    total_delta=int(row.total_delta) if row.total_delta else 0,
                )
            )

        # Get total movements count (not paginated)
        total_mov_stmt = select(func.count(InventoryLog.id))
        if start_date:
            total_mov_stmt = total_mov_stmt.where(InventoryLog.created_at >= start_date)
        if end_date:
            total_mov_stmt = total_mov_stmt.where(InventoryLog.created_at <= end_date)
        total_mov_res = await self.db.execute(total_mov_stmt)
        overall_total_movements = total_mov_res.scalar() or 0

        return InventoryReport(
            total_movements=overall_total_movements, 
            movements_by_reason=movements,
            total=total_count,
            page=page,
            page_size=page_size
        )
