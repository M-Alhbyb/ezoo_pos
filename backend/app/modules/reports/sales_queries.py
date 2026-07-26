from datetime import datetime, date
from decimal import Decimal
from typing import List, Optional, Dict, Any

from sqlalchemy import select, func, String
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.sale import Sale
from app.models.partner_wallet_transaction import PartnerWalletTransaction
from app.models.sale_payment import SalePayment
from app.schemas.report import (
    SalesReport,
    SalesSummaryGroup,
)


def _date_col(col):
    """Extract date from a datetime column, compatible with SQLite."""
    return func.date(col)


async def get_sales_count(db: AsyncSession, start_date: date, end_date: date) -> int:
    """
    Count total sales records in date range for export validation.
    """
    stmt = select(func.count(Sale.id))
    if start_date:
        stmt = stmt.where(func.date(Sale.created_at) >= start_date)
    if end_date:
        stmt = stmt.where(func.date(Sale.created_at) <= end_date)

    result = await db.execute(stmt)
    count = result.scalar()
    return count or 0


async def get_sales_report(
    db: AsyncSession,
    start_date: Optional[datetime],
    end_date: Optional[datetime],
    page: int = 1,
    page_size: int = 50,
) -> SalesReport:
    """
    Aggregate sales statistics with daily breakdown.
    """
    stmt = select(Sale)
    if start_date:
        stmt = stmt.where(func.date(Sale.created_at) >= start_date)
    if end_date:
        stmt = stmt.where(func.date(Sale.created_at) <= end_date)

    # Totals for summary cards (not paginated)
    total_stmt = select(
        func.sum(Sale.grand_total).label("revenue"),
        func.sum(Sale.total_cost).label("cost"),
        func.sum(Sale.profit).label("profit"),
        func.count(Sale.id).label("count"),
    )
    if start_date:
        total_stmt = total_stmt.where(func.date(Sale.created_at) >= start_date)
    if end_date:
        total_stmt = total_stmt.where(func.date(Sale.created_at) <= end_date)

    total_result = await db.execute(total_stmt)
    total_row = total_result.one()

    # Daily breakdown via SQL aggregation for efficiency (Paginated)
    group_stmt = (
        select(
            _date_col(Sale.created_at).label("day"),
            func.count(Sale.id).label("count"),
            func.sum(Sale.grand_total).label("revenue"),
            func.sum(Sale.total_cost).label("cost"),
            func.sum(Sale.profit).label("profit"),
        )
        .group_by("day")
        .order_by("day")
    )
    if start_date:
        group_stmt = group_stmt.where(func.date(Sale.created_at) >= start_date)
    if end_date:
        group_stmt = group_stmt.where(func.date(Sale.created_at) <= end_date)

    # Get total count of groups for pagination
    count_stmt = select(func.count()).select_from(group_stmt.alias("subquery"))
    count_result = await db.execute(count_stmt)
    total_groups = count_result.scalar() or 0

    # Apply pagination
    group_stmt = group_stmt.limit(page_size).offset((page - 1) * page_size)

    group_result = await db.execute(group_stmt)
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

    # Calculate total partner payouts for net profit calculation
    payout_stmt = select(func.sum(PartnerWalletTransaction.amount)).where(
        PartnerWalletTransaction.transaction_type == "sale_profit"
    )
    if start_date:
        payout_stmt = payout_stmt.where(
            func.date(PartnerWalletTransaction.created_at) >= start_date
        )
    if end_date:
        payout_stmt = payout_stmt.where(
            func.date(PartnerWalletTransaction.created_at) <= end_date
        )

    payout_res = await db.execute(payout_stmt)
    total_partner_profit = payout_res.scalar() or Decimal("0.00")

    gross_profit = total_row.profit or Decimal("0.00")
    total_net_profit = gross_profit - total_partner_profit

    return SalesReport(
        total_revenue=total_row.revenue or Decimal("0.00"),
        total_cost=total_row.cost or Decimal("0.00"),
        total_profit=gross_profit,
        total_partner_profit=total_partner_profit,
        total_net_profit=total_net_profit,
        sales_count=total_row.count or 0,
        daily_breakdown=daily_breakdown,
        total=total_groups,
        page=page,
        page_size=page_size,
    )


async def get_sales_export_data(
    db: AsyncSession, start_date: Optional[date], end_date: Optional[date]
) -> List[Dict[str, Any]]:
    # Load sales with payments and their associated method names
    stmt = (
        select(Sale)
        .options(
            selectinload(Sale.payments).selectinload(SalePayment.payment_method)
        )
        .order_by(Sale.created_at.desc(), Sale.id.desc())
    )
    if start_date:
        stmt = stmt.where(func.date(Sale.created_at) >= start_date)
    if end_date:
        stmt = stmt.where(func.date(Sale.created_at) <= end_date)

    result = await db.execute(stmt)
    sales = result.scalars().all()

    # Fetch partner payouts for these sales
    # Map sale_id -> sum(amount)
    sale_ids = [sale.id for sale in sales]
    payouts_by_sale = {}
    if sale_ids:
        payout_stmt = (
            select(
                PartnerWalletTransaction.reference_id,
                func.sum(PartnerWalletTransaction.amount),
            )
            .where(PartnerWalletTransaction.reference_id.in_(sale_ids))
            .where(PartnerWalletTransaction.transaction_type == "sale_profit")
            .group_by(PartnerWalletTransaction.reference_id)
        )
        payout_res = await db.execute(payout_stmt)
        for row in payout_res:
            payouts_by_sale[row[0]] = row[1]

    data = []
    for sale in sales:
        partner_share = payouts_by_sale.get(sale.id, Decimal("0.00"))
        gross_profit = sale.profit or Decimal("0.00")
        net_profit = gross_profit - partner_share

        # Combine payment methods into a string
        methods = (
            ", ".join([p.payment_method_name for p in sale.payments])
            if sale.payments
            else ""
        )

        data.append(
            {
                "Date": str(sale.created_at),
                "Payment Methods": methods,
                "Subtotal": sale.subtotal,
                "Fees": sale.fees_total,
                "VAT": sale.vat_total,
                "Grand Total": sale.grand_total,
                "Gross Profit": gross_profit,
                "Partner Share": partner_share,
                "Net Profit": net_profit,
                "Note": sale.note or "",
            }
        )
    return data
