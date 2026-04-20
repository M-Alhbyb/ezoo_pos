from datetime import datetime
from decimal import Decimal
from typing import List, Optional, Dict, Any
from uuid import UUID

from sqlalchemy import select, func, cast, Date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.sale import Sale
from app.models.project import Project, ProjectStatus
from app.models.partner_distribution import PartnerDistribution
from app.models.partner import Partner
from app.models.inventory_log import InventoryLog
from app.schemas.report import (
    SalesReport, SalesSummaryGroup, 
    ProjectReport, ProjectSummary,
    PartnerReport, PartnerPayoutSummary,
    InventoryReport, InventoryMovement
)


class ReportService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_sales_report(
        self, start_date: Optional[datetime], end_date: Optional[datetime]
    ) -> SalesReport:
        """
        Aggregate sales statistics with daily breakdown.
        """
        stmt = select(Sale)
        if start_date:
            stmt = stmt.where(Sale.created_at >= start_date)
        if end_date:
            stmt = stmt.where(Sale.created_at <= end_date)

        result = await self.db.execute(stmt)
        sales = list(result.scalars().all())

        total_revenue = sum((s.grand_total for s in sales), Decimal("0.00"))
        total_cost = sum((s.total_cost for s in sales), Decimal("0.00"))
        total_profit = sum((s.profit for s in sales), Decimal("0.00"))

        # Daily breakdown via SQL aggregation for efficiency
        group_stmt = (
            select(
                cast(Sale.created_at, Date).label("day"),
                func.count(Sale.id).label("count"),
                func.sum(Sale.grand_total).label("revenue"),
                func.sum(Sale.total_cost).label("cost"),
                func.sum(Sale.profit).label("profit")
            )
            .group_by("day")
            .order_by("day")
        )
        if start_date:
            group_stmt = group_stmt.where(Sale.created_at >= start_date)
        if end_date:
            group_stmt = group_stmt.where(Sale.created_at <= end_date)

        group_result = await self.db.execute(group_stmt)
        daily_breakdown = [
            SalesSummaryGroup(
                date=row.day,
                count=row.count,
                revenue=row.revenue or Decimal("0.00"),
                cost=row.cost or Decimal("0.00"),
                profit=row.profit or Decimal("0.00")
            )
            for row in group_result
        ]

        return SalesReport(
            total_revenue=total_revenue,
            total_cost=total_cost,
            total_profit=total_profit,
            sales_count=len(sales),
            daily_breakdown=daily_breakdown
        )

    async def get_projects_report(
        self, start_date: Optional[datetime], end_date: Optional[datetime]
    ) -> ProjectReport:
        """
        Aggregate project statistics including individual project status.
        """
        stmt = select(Project)
        if start_date:
            stmt = stmt.where(Project.created_at >= start_date)
        if end_date:
            stmt = stmt.where(Project.created_at <= end_date)

        result = await self.db.execute(stmt)
        projects = list(result.scalars().all())

        total_selling_price = sum((p.selling_price for p in projects), Decimal("0.00"))
        total_cost = sum((p.total_cost for p in projects), Decimal("0.00"))
        total_expenses = sum((p.total_expenses for p in projects), Decimal("0.00"))
        total_profit = sum((p.profit for p in projects), Decimal("0.00"))

        project_list = [
            ProjectSummary(
                id=p.id,
                name=p.name,
                status=p.status,
                selling_price=p.selling_price,
                total_cost=p.total_cost,
                total_expenses=p.total_expenses,
                profit=p.profit
            )
            for p in projects
        ]

        return ProjectReport(
            total_projects=len(projects),
            total_selling_price=total_selling_price,
            total_cost=total_cost,
            total_expenses=total_expenses,
            total_profit=total_profit,
            project_list=project_list
        )

    async def get_partners_report(
        self, start_date: Optional[datetime], end_date: Optional[datetime]
    ) -> PartnerReport:
        """
        Aggregate partner distributions grouped by partner.
        """
        payout_stmt = (
            select(
                Partner.id.label("partner_id"),
                Partner.name.label("partner_name"),
                func.sum(PartnerDistribution.payout_amount).label("total_payout")
            )
            .join(Partner, Partner.id == PartnerDistribution.partner_id)
            .group_by(Partner.id, Partner.name)
        )
        
        if start_date:
            payout_stmt = payout_stmt.where(PartnerDistribution.created_at >= start_date)
        if end_date:
            payout_stmt = payout_stmt.where(PartnerDistribution.created_at <= end_date)

        result = await self.db.execute(payout_stmt)
        payouts_by_partner = [
            PartnerPayoutSummary(
                partner_id=row.partner_id,
                partner_name=row.partner_name,
                total_payout=row.total_payout or Decimal("0.00")
            )
            for row in result
        ]

        total_payout = sum((p.total_payout for p in payouts_by_partner), Decimal("0.00"))

        return PartnerReport(
            total_payout=total_payout,
            payouts_by_partner=payouts_by_partner
        )

    async def get_inventory_report(
        self, start_date: Optional[datetime], end_date: Optional[datetime]
    ) -> InventoryReport:
        """
        Aggregate inventory movements by reason.
        """
        stmt = (
            select(
                InventoryLog.reason,
                func.sum(InventoryLog.delta).label("total_delta"),
                func.count(InventoryLog.id).label("movement_count")
            )
            .group_by(InventoryLog.reason)
        )

        if start_date:
            stmt = stmt.where(InventoryLog.created_at >= start_date)
        if end_date:
            stmt = stmt.where(InventoryLog.created_at <= end_date)

        result = await self.db.execute(stmt)
        movements = []
        total_count = 0
        
        for row in result:
            total_count += row.movement_count
            movements.append(
                InventoryMovement(
                    reason=row.reason,
                    total_delta=int(row.total_delta) if row.total_delta else 0
                )
            )

        return InventoryReport(
            total_movements=total_count,
            movements_by_reason=movements
        )
