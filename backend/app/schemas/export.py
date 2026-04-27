from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from pydantic import BaseModel, Field, field_validator
from typing import Optional


class ExportFormat(str, Enum):
    XLSX = "xlsx"
    PDF = "pdf"


class ExportRequest(BaseModel):
    format: ExportFormat
    start_date: date
    end_date: date

    @field_validator("end_date")
    @classmethod
    def end_date_after_start(cls, v: date, info) -> date:
        if "start_date" in info.data and v < info.data["start_date"]:
            raise ValueError("end_date must be on or after start_date")
        return v


class ExportMetadata(BaseModel):
    generated_at: datetime
    format: ExportFormat
    report_type: str
    row_count: int
    date_range: tuple[date, date]
    generated_by: str

    class Config:
        json_encoders = {Decimal: float}


class ExportResponse(BaseModel):
    export_id: str
    status: str = Field(
        ..., description="Export status: started, processing, completed, failed"
    )
    progress: int = Field(0, ge=0, le=100)
    download_url: Optional[str] = None
    error_message: Optional[str] = None
    metadata: Optional[ExportMetadata] = None


class ExportLimits(BaseModel):
    xlsx_max_rows: int = 50000
    pdf_max_rows: int = 10000
    rate_limit_threshold: int = 5000
    rate_limit_per_hour: int = 10
