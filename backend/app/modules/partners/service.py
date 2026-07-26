from datetime import datetime, timezone
from decimal import Decimal
from typing import List, Dict, Any, Optional
import json
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.partner import Partner
from app.models.partner_distribution import PartnerDistribution
from app.models.partner_wallet_transaction import PartnerWalletTransaction
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

    async def get_partner(self, partner_id: int) -> Optional[Partner]:
        query = select(Partner).where(Partner.id == partner_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_partner_distributions(self, partner_id: int) -> List[PartnerDistribution]:
        query = select(PartnerDistribution).where(
            PartnerDistribution.partner_id == partner_id
        ).order_by(PartnerDistribution.created_at.desc(), PartnerDistribution.id.desc())
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

            # Also create a wallet transaction so the partner report can aggregate it
            previous_balance = await self._get_wallet_balance(p.id)
            new_balance = previous_balance + payout_amount

            wallet_txn = PartnerWalletTransaction(
                partner_id=p.id,
                amount=payout_amount,
                transaction_type="sale_profit",
                reference_type="distribution",
                description=f"Manual distribution: {p.share_percentage}% of {total_profit}",
                balance_after=new_balance,
                created_at=datetime.now(timezone.utc),
            )
            self.db.add(wallet_txn)
            
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

    async def _get_wallet_balance(self, partner_id: int) -> Decimal:
        """Get current wallet balance from the latest transaction."""
        query = (
            select(PartnerWalletTransaction)
            .where(PartnerWalletTransaction.partner_id == partner_id)
            .order_by(
                PartnerWalletTransaction.created_at.desc(),
                PartnerWalletTransaction.id.desc(),
            )
            .limit(1)
        )
        result = await self.db.execute(query)
        latest = result.scalar_one_or_none()
        return latest.balance_after if latest else Decimal("0.00")

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
            snapshot_fields=json.dumps(snapshot)
        )
        self.db.add(dist_record)

