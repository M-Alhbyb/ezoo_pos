from decimal import Decimal
from typing import List, Optional
from uuid import UUID
from datetime import datetime, date

from pydantic import BaseModel, ConfigDict


class SalesSummaryGroup(BaseModel):
    """Aggregation of sales by day."""
    date: date
    count: int
    revenue: Decimal
    cost: Decimal
    profit: Decimal


class SalesReport(BaseModel):
    """Aggregate sales statistics."""
    total_revenue: Decimal
    total_cost: Decimal
    total_profit: Decimal
    sales_count: int
    daily_breakdown: List[SalesSummaryGroup]
    total: int
    page: int
    page_size: int


class ProjectSummary(BaseModel):
    """Summary of an individual project's financial status."""
    id: UUID
    name: str
    status: str
    selling_price: Decimal
    total_cost: Decimal
    total_expenses: Decimal
    profit: Decimal


class ProjectReport(BaseModel):
    """Aggregate project statistics."""
    total_projects: int
    total_selling_price: Decimal
    total_cost: Decimal
    total_expenses: Decimal
    total_profit: Decimal
    project_list: List[ProjectSummary]
    total: int
    page: int
    page_size: int


class PartnerPayoutSummary(BaseModel):
    """Aggregate distributions per partner."""
    partner_id: UUID
    partner_name: str
    total_payout: Decimal


class PartnerReport(BaseModel):
    """Aggregate partner statistics."""
    total_payout: Decimal
    payouts_by_partner: List[PartnerPayoutSummary]
    total: int
    page: int
    page_size: int


class InventoryMovement(BaseModel):
    """Aggregation of inventory changes by reason."""
    reason: str
    total_delta: int


class InventoryReport(BaseModel):
    """Aggregate inventory statistics."""
    total_movements: int
    movements_by_reason: List[InventoryMovement]
    total: int
    page: int
    page_size: int
