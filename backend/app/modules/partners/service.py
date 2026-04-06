from datetime import datetime
from decimal import Decimal
from typing import List, Dict, Optional, Any
from uuid import UUID

from sqlalchemy import select, not_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.partner import Partner
from app.models.partner_distribution import PartnerDistribution
from app.models.project import Project, ProjectStatus
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

    async def calculate_distribution(self, project_ids: Optional[List[UUID]] = None, date_range: Optional[Dict[str, datetime]] = None) -> Dict[str, Any]:
        """
        Calculates and locks distributions for un-distributed completed projects.
        """
        # 1. Identify which projects have already been distributed
        dist_query = select(PartnerDistribution.project_id).distinct()
        dist_result = await self.db.execute(dist_query)
        distributed_project_ids = list(dist_result.scalars().all())

        # 2. Get target COMPLETED projects
        stmt = select(Project).where(Project.status == ProjectStatus.COMPLETED)
        if distributed_project_ids:
            stmt = stmt.where(Project.id.not_in(distributed_project_ids))
            
        if project_ids:
            stmt = stmt.where(Project.id.in_(project_ids))
            
        if date_range:
            if "start" in date_range:
                stmt = stmt.where(Project.created_at >= date_range["start"])
            if "end" in date_range:
                stmt = stmt.where(Project.created_at <= date_range["end"])
                
        result = await self.db.execute(stmt)
        projects = list(result.scalars().all())
        
        if not projects:
            raise ValueError("No un-distributed completed projects found")

        total_profit = Decimal('0')
        distributed_total = Decimal('0')
        distributions_responses = []

        partners = await self.get_partners()
        
        # 3. For each project, apply distributions and commit exact snapshots immutably
        for project in projects:
            project_profit = project.profit
            total_profit += project_profit
            
            for p in partners:
                payout_amount = project_profit * (p.share_percentage / Decimal('100'))
                distributed_total += payout_amount
                
                await self.create_snapshot(p, project, payout_amount)
                
                distributions_responses.append({
                    "partner_id": str(p.id),
                    "name": p.name,
                    "share_percentage": p.share_percentage,
                    "amount": payout_amount
                })
        
        await self.db.commit()

        # Combine identical partner distributions into a final list
        final_distributions = {}
        for d in distributions_responses:
            pid = d["partner_id"]
            if pid not in final_distributions:
                final_distributions[pid] = d
            else:
                final_distributions[pid]["amount"] += d["amount"]

        return {
            "project_id": str(projects[0].id), 
            "total_profit": total_profit,
            "distributed_total": distributed_total,
            "distributions": list(final_distributions.values())
        }

    async def create_snapshot(self, partner: Partner, project: Project, payout_amount: Decimal):
        """
        Generates and stores an immutable record of a payout.
        """
        snapshot = {
            "project_profit": str(project.profit),
            "partner_share_percentage": str(partner.share_percentage),
            "partner_investment_at_time": str(partner.investment_amount)
        }
        
        dist_record = PartnerDistribution(
            partner_id=partner.id,
            project_id=project.id,
            payout_amount=payout_amount,
            snapshot_fields=snapshot
        )
        self.db.add(dist_record)

