from datetime import date
from decimal import Decimal
from pydantic import BaseModel, Field, field_validator
from typing import Optional, Literal


class DashboardFilter(BaseModel):
    start_date: date
    end_date: date


class SalesDashboardFilter(DashboardFilter):
    pass


class ProjectsDashboardFilter(DashboardFilter):
    project_id: Optional[int] = None


class PartnersDashboardFilter(DashboardFilter):
    partner_id: Optional[int] = None


class InventoryDashboardFilter(DashboardFilter):
    pass


class ChartDataPoint(BaseModel):
    date: date
    value: Decimal

    class Config:
        json_encoders = {Decimal: float}


class SalesChartData(BaseModel):
    dates: list[date]
    revenue: list[Decimal]
    profit: list[Decimal]
    vat: list[Decimal]

    @field_validator("revenue", "profit", "vat")
    @classmethod
    def validate_length(cls, v: list, info) -> list:
        if "dates" in info.data and len(v) != len(info.data["dates"]):
            raise ValueError("All arrays must have same length")
        return v

    @field_validator("dates")
    @classmethod
    def max_points(cls, v: list) -> list:
        if len(v) > 1000:
            raise ValueError("Maximum 1000 data points allowed")
        return v

    class Config:
        json_encoders = {Decimal: float}


class ProjectChartData(BaseModel):
    project_names: list[str]
    profits: list[Decimal]
    profit_margins: list[Decimal]
    project_ids: list[int]

    @field_validator("project_names", "profits", "profit_margins", "project_ids")
    @classmethod
    def max_points(cls, v: list) -> list:
        if len(v) > 1000:
            raise ValueError("Maximum 1000 projects allowed")
        return v

    class Config:
        json_encoders = {Decimal: float}


class PartnerChartData(BaseModel):
    partner_names: list[str]
    dividend_amounts: list[Decimal]
    share_percentages: list[Decimal]
    partner_ids: list[int]

    @field_validator("partner_names", "dividend_amounts", "share_percentages", "partner_ids")
    @classmethod
    def max_points(cls, v: list) -> list:
        if len(v) > 1000:
            raise ValueError("Maximum 1000 partners allowed")
        return v

    class Config:
        json_encoders = {Decimal: float}


class InventoryChartData(BaseModel):
    dates: list[date]
    sales: list[int]
    restocks: list[int]
    reversals: list[int]

    @field_validator("sales", "restocks", "reversals")
    @classmethod
    def validate_length(cls, v: list, info) -> list:
        if "dates" in info.data and len(v) != len(info.data["dates"]):
            raise ValueError("All arrays must have same length")
        return v

    @field_validator("dates")
    @classmethod
    def max_points(cls, v: list) -> list:
        if len(v) > 1000:
            raise ValueError("Maximum 1000 data points allowed")
        return v


class DashboardResponse(BaseModel):
    success: bool
    data: Optional[
        SalesChartData | ProjectChartData | PartnerChartData | InventoryChartData
    ] = None
    error: Optional[str] = None
    total_points: Optional[int] = None
    filter_applied: Optional[DashboardFilter] = None
