from datetime import datetime, date
from decimal import Decimal
from typing import List, Optional, Dict, Any

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.partner_wallet_transaction import PartnerWalletTransaction
from app.models.partner import Partner
from app.schemas.report import (
    PartnerReport,
    PartnerPayoutSummary,
)


async def get_partners_count(db: AsyncSession, start_date: date, end_date: date) -> int:
    """
    Count total partner profit transactions in date range for export validation.
    """
    stmt = select(func.count(PartnerWalletTransaction.id)).where(
        PartnerWalletTransaction.transaction_type == "sale_profit"
    )
    if start_date:
        stmt = stmt.where(
            func.date(PartnerWalletTransaction.created_at) >= start_date
        )
    if end_date:
        stmt = stmt.where(
            func.date(PartnerWalletTransaction.created_at) <= end_date
        )

    result = await db.execute(stmt)
    count = result.scalar()
    return count or 0


async def get_partners_report(
    db: AsyncSession,
    start_date: Optional[datetime],
    end_date: Optional[datetime],
    page: int = 1,
    page_size: int = 50,
) -> PartnerReport:
    """
    Aggregate partner distributions grouped by partner.
    """
    payout_stmt = (
        select(
            Partner.id.label("partner_id"),
            Partner.name.label("partner_name"),
            func.sum(PartnerWalletTransaction.amount).label("total_payout"),
        )
        .join(Partner, Partner.id == PartnerWalletTransaction.partner_id)
        .where(PartnerWalletTransaction.transaction_type == "sale_profit")
        .group_by(Partner.id, Partner.name)
    )

    if start_date:
        payout_stmt = payout_stmt.where(
            func.date(PartnerWalletTransaction.created_at) >= start_date
        )
    if end_date:
        payout_stmt = payout_stmt.where(
            func.date(PartnerWalletTransaction.created_at) <= end_date
        )

    # Get total for pagination
    count_stmt = select(func.count()).select_from(payout_stmt.alias("subquery"))
    count_result = await db.execute(count_stmt)
    total_count = count_result.scalar() or 0

    # Apply pagination
    payout_stmt = payout_stmt.limit(page_size).offset((page - 1) * page_size)

    result = await db.execute(payout_stmt)
    payouts_by_partner = [
        PartnerPayoutSummary(
            partner_id=row.partner_id,
            partner_name=row.partner_name,
            total_payout=row.total_payout or Decimal("0.00"),
        )
        for row in result
    ]

    # Overall total payout (not paginated)
    total_payout_stmt = select(func.sum(PartnerWalletTransaction.amount)).where(
        PartnerWalletTransaction.transaction_type == "sale_profit"
    )
    if start_date:
        total_payout_stmt = total_payout_stmt.where(
            func.date(PartnerWalletTransaction.created_at) >= start_date
        )
    if end_date:
        total_payout_stmt = total_payout_stmt.where(
            func.date(PartnerWalletTransaction.created_at) <= end_date
        )

    total_payout_res = await db.execute(total_payout_stmt)
    overall_total_payout = total_payout_res.scalar() or Decimal("0.00")

    return PartnerReport(
        total_payout=overall_total_payout,
        payouts_by_partner=payouts_by_partner,
        total=total_count,
        page=page,
        page_size=page_size,
    )


async def get_partners_export_data(
    db: AsyncSession, start_date: Optional[date], end_date: Optional[date]
) -> List[Dict[str, Any]]:
    stmt = (
        select(
            PartnerWalletTransaction,
            Partner.name.label("partner_name"),
            Partner.investment_amount.label("invested_amount"),
            Partner.share_percentage.label("profit_percentage"),
        )
        .join(Partner, Partner.id == PartnerWalletTransaction.partner_id)
        .where(PartnerWalletTransaction.transaction_type == "sale_profit")
        .order_by(PartnerWalletTransaction.created_at.desc(), PartnerWalletTransaction.id.desc())
    )
    if start_date:
        stmt = stmt.where(
            func.date(PartnerWalletTransaction.created_at) >= start_date
        )
    if end_date:
        stmt = stmt.where(
            func.date(PartnerWalletTransaction.created_at) <= end_date
        )

    result = await db.execute(stmt)
    data = []
    for row in result:
        trans = row.PartnerWalletTransaction
        data.append(
            {
                "name": row.partner_name,
                "invested_amount": row.invested_amount,
                "profit_percentage": row.profit_percentage,
                "distributed_amount": trans.amount,
                "distribution_date": str(trans.created_at),
            }
        )
    return data
