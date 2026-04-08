from decimal import Decimal
from typing import List, Dict, Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.partner import Partner
from app.models.partner_distribution import PartnerDistribution
from app.schemas.partner import PartnerCreate


class PartnerService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_partner(self, data: PartnerCreate) -> Partner:
        partner = Partner(
            name=data.name,
            investment_amount=data.investment_amount,
            share_percentage=data.share_percentage
        )
        self.db.add(partner)
        await self.db.commit()
        await self.db.refresh(partner)
        return partner

    async def get_partners(self) -> List[Partner]:
        query = select(Partner)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def calculate_distribution(self, total_profit: Decimal = Decimal('0')) -> Dict[str, Any]:
        """
        Calculates and locks distributions for a given profit amount.
        """
        if total_profit <= 0:
            raise ValueError("Profit must be greater than zero for distribution")

        distributed_total = Decimal('0')
        distributions_responses = []

        partners = await self.get_partners()
        
        for p in partners:
            payout_amount = total_profit * (p.share_percentage / Decimal('100'))
            distributed_total += payout_amount
            
            await self.create_snapshot(p, total_profit, payout_amount)
            
            distributions_responses.append({
                "partner_id": str(p.id),
                "name": p.name,
                "share_percentage": p.share_percentage,
                "amount": payout_amount
            })
        
        await self.db.commit()

        return {
            "total_profit": total_profit,
            "distributed_total": distributed_total,
            "distributions": distributions_responses
        }

    async def create_snapshot(self, partner: Partner, profit: Decimal, payout_amount: Decimal):
        """
        Generates and stores an immutable record of a payout.
        """
        snapshot = {
            "payout_profit_basis": str(profit),
            "partner_share_percentage": str(partner.share_percentage),
            "partner_investment_at_time": str(partner.investment_amount)
        }
        
        dist_record = PartnerDistribution(
            partner_id=partner.id,
            payout_amount=payout_amount,
            snapshot_fields=snapshot
        )
        self.db.add(dist_record)

