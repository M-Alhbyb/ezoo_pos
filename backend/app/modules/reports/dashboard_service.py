
from datetime import date, datetime
from decimal import Decimal
from typing import Optional
import logging

from sqlalchemy import select, func, cast, Date, literal
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.schemas.dashboard import (
    SalesChartData,
    PartnerChartData,
    InventoryChartData,
    DashboardFilter,
)
from app.models.sale import Sale

from app.models.partner import Partner
from app.models.partner_distribution import PartnerDistribution
from app.models.inventory_log import InventoryLog

logger = logging.getLogger(__name__)


class DashboardService:
    """Service for aggregating dashboard chart data."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_sales_dashboard_data(
        self, start_date: date, end_date: date
    ) -> SalesChartData:
        """
        Get aggregated sales data for line chart visualization.
        Groups data by day and returns revenue, profit, and VAT totals.

        Args:
            start_date: Start of date range
            end_date: End of date range

        Returns:
            SalesChartData with dates, revenue, profit, and vat arrays

        Raises:
            ValueError: If data points exceed 1000
        """
        try:
            stmt = (
                select(
                    cast(Sale.created_at, Date).label("date"),
                    func.sum(Sale.grand_total).label("revenue"),
                    func.sum(Sale.profit).label("profit"),
                    func.coalesce(func.sum(Sale.vat_total), 0).label("vat"),
                )
                .where(Sale.created_at >= start_date)
                .where(Sale.created_at <= end_date)
                .group_by(cast(Sale.created_at, Date))
                .order_by(cast(Sale.created_at, Date))
            )

            result = await self.db.execute(stmt)
            rows = result.all()

            if len(rows) > settings.dashboard_max_points:
                logger.warning(
                    f"Sales dashboard data points exceed limit: "
                    f"{len(rows)} points (max: {settings.dashboard_max_points})"
                )
                raise ValueError(
                    f"Date range would result in {len(rows)} data points. "
                    f"Maximum allowed is {settings.dashboard_max_points}. "
                    "Please narrow your date range."
                )

            dates = [row.date for row in rows]
            revenue = [Decimal(str(row.revenue or 0)) for row in rows]
            profit = [Decimal(str(row.profit or 0)) for row in rows]
            vat = [Decimal(str(row.vat or 0)) for row in rows]

            logger.info(
                f"Sales dashboard rendered successfully: {len(rows)} data points"
            )
            return SalesChartData(dates=dates, revenue=revenue, profit=profit, vat=vat)
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Sales dashboard rendering failed: {str(e)}", exc_info=True)
            raise ValueError(f"Failed to render sales dashboard: {str(e)}")


    async def get_partners_dashboard_data(
        self, start_date: date, end_date: date, partner_id: Optional[int] = None
    ) -> PartnerChartData:
        """
        Get aggregated partner dividend data for pie chart visualization.

        Args:
            start_date: Start of date range
            end_date: End of date range
            partner_id: Optional specific partner filter

        Returns:
            PartnerChartData with partner names, dividend amounts, percentages, and IDs
        """
        try:
            stmt = (
                select(
                    Partner.id,
                    Partner.name,
                    func.sum(PartnerDistribution.payout_amount).label(
                        "total_dividends"
                    ),
                )
                .join(Partner, Partner.id == PartnerDistribution.partner_id)
                .where(PartnerDistribution.created_at >= start_date)
                .where(PartnerDistribution.created_at <= end_date)
                .group_by(Partner.id, Partner.name)
            )

            if partner_id:
                stmt = stmt.where(Partner.id == partner_id)

            stmt = stmt.limit(settings.dashboard_max_points)

            result = await self.db.execute(stmt)
            rows = result.all()

            total_dividends = sum(row.total_dividends for row in rows) if rows else 0

            partner_names = [row.name for row in rows]
            dividend_amounts = [Decimal(str(row.total_dividends)) for row in rows]

            share_percentages = []
            for row in rows:
                if total_dividends > 0:
                    percentage = (row.total_dividends / total_dividends) * 100
                    share_percentages.append(Decimal(str(round(percentage, 2))))
                else:
                    share_percentages.append(Decimal("0.00"))

            partner_ids = [row.id for row in rows]

            logger.info(
                f"Partners dashboard rendered successfully: {len(rows)} partners"
            )
            return PartnerChartData(
                partner_names=partner_names,
                dividend_amounts=dividend_amounts,
                share_percentages=share_percentages,
                partner_ids=partner_ids,
            )
        except ValueError:
            raise
        except Exception as e:
            logger.error(
                f"Partners dashboard rendering failed: {str(e)}", exc_info=True
            )
            raise ValueError(f"Failed to render partners dashboard: {str(e)}")

    async def get_inventory_dashboard_data(
        self, start_date: date, end_date: date
    ) -> InventoryChartData:
        """
        Get aggregated inventory movement data for stacked bar chart visualization.

        Args:
            start_date: Start of date range
            end_date: End of date range

        Returns:
            InventoryChartData with dates, sales, restocks, and reversals arrays
        """
        try:
            stmt = (
                select(
                    cast(InventoryLog.created_at, Date).label("date"),
                    InventoryLog.reason,
                    func.sum(InventoryLog.delta).label("total_quantity"),
                )
                .where(InventoryLog.created_at >= start_date)
                .where(InventoryLog.created_at <= end_date)
                .group_by(
                    cast(InventoryLog.created_at, Date), InventoryLog.reason
                )
                .order_by(cast(InventoryLog.created_at, Date))
            )

            result = await self.db.execute(stmt)
            rows = result.all()

            date_movement_map = {}
            movement_types = {
                "sale": "sales",
                "restock": "restocks",
                "reversal": "reversals",
            }

            for row in rows:
                date_key = row.date
                if date_key not in date_movement_map:
                    date_movement_map[date_key] = {
                        "sales": 0,
                        "restocks": 0,
                        "reversals": 0,
                    }

                movement_key = movement_types.get(row.reason, "sales")
                date_movement_map[date_key][movement_key] = abs(row.total_quantity)

            if len(date_movement_map) > settings.dashboard_max_points:
                logger.warning(
                    f"Inventory dashboard data points exceed limit: "
                    f"{len(date_movement_map)} points (max: {settings.dashboard_max_points})"
                )
                raise ValueError(
                    f"Date range would result in {len(date_movement_map)} data points. "
                    f"Maximum allowed is {settings.dashboard_max_points}. "
                    "Please narrow your date range."
                )

            dates = sorted(date_movement_map.keys())
            sales = [date_movement_map[d]["sales"] for d in dates]
            restocks = [date_movement_map[d]["restocks"] for d in dates]
            reversals = [date_movement_map[d]["reversals"] for d in dates]

            logger.info(
                f"Inventory dashboard rendered successfully: {len(dates)} data points"
            )
            return InventoryChartData(
                dates=dates, sales=sales, restocks=restocks, reversals=reversals
            )
        except ValueError:
            raise
        except Exception as e:
            logger.error(
                f"Inventory dashboard rendering failed: {str(e)}", exc_info=True
            )
            raise ValueError(f"Failed to render inventory dashboard: {str(e)}")
