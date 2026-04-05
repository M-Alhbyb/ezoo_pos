from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.project import Project, ProjectStatus
from app.models.expense import Expense, ExpenseType
from app.schemas.project import ProjectCreate


class ProjectService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_projects(self) -> List[Project]:
        query = select(Project).options(selectinload(Project.items), selectinload(Project.expenses))
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_project(self, project_id: UUID) -> Optional[Project]:
        query = (
            select(Project)
            .options(selectinload(Project.items), selectinload(Project.expenses))
            .where(Project.id == project_id)
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def create_project(self, data: ProjectCreate) -> Project:
        project = Project(
            name=data.name,
            selling_price=data.selling_price,
            total_cost=data.cost if data.cost is not None else 0,
            status=data.status if data.status is not None else ProjectStatus.DRAFT,
        )
        self.db.add(project)
        await self.db.commit()
        return await self.get_project(project.id)

    async def mark_completed(self, project_id: UUID) -> Project:
        project = await self.get_project(project_id)
        if not project:
            raise ValueError(f"Project {project_id} not found")

        if project.status == ProjectStatus.COMPLETED:
            return project  # Already completed

        # 1. Freeze item costs (total_cost is calculated sum of base_cost * quantity)
        # Note: If no items, we might use predefined cost, else calculate items_cost.
        items_cost = Decimal('0')
        if project.items:
            for item in project.items:
                items_cost += (item.base_cost or 0) * item.quantity
        else:
            items_cost = project.total_cost # fallback to specified cost

        project.total_cost = items_cost

        # 2. Freeze expenses
        # Recalculate percent and sum all expenses
        total_expenses = Decimal('0')
        for expense in project.expenses:
            if expense.type == ExpenseType.PERCENT:
                # Percentage of selling price
                expense.calculated_amount = project.selling_price * (expense.value / Decimal('100'))
            elif expense.type == ExpenseType.FIXED:
                expense.calculated_amount = expense.value
            else:
                expense.calculated_amount = expense.value # Default fallback
            
            total_expenses += expense.calculated_amount
            
        project.total_expenses = total_expenses

        # 3. Calculate Profit: selling_price - (items_cost + total_expenses)
        project.profit = project.selling_price - (project.total_cost + project.total_expenses)
        
        # 4. Status update
        project.status = ProjectStatus.COMPLETED

        await self.db.commit()
        
        return await self.get_project(project.id)
