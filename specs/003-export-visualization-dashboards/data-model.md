# Data Model: Export Formats and Visualization Dashboards

**Date**: 2026-04-05  
**Feature**: 003-export-visualization-dashboards

## Overview

This feature extends the existing EZOO POS system with export and dashboard capabilities. **No new database tables or migrations are required**. All functionality reuses existing models and adds Pydantic schemas for request/response validation.

## Existing Models (Reused)

### Financial Snapshots (Immutable)

```python
# app/models/sale.py (existing)
class SaleSnapshot(Base):
    """Immutable sale record - source of truth for exports/dashboards"""
    __tablename__ = "sale_snapshots"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    sale_id: Mapped[int] = mapped_column(ForeignKey("sales.id"))
    snapshot_date: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    
    # Immutable financial data (DECIMAL precision)
    subtotal: Mapped[Decimal] = mapped_column(DECIMAL(19, 4))
    fees_total: Mapped[Decimal] = mapped_column(DECIMAL(19, 4))
    vat_amount: Mapped[Decimal] = mapped_column(DECIMAL(19, 4))
    total: Mapped[Decimal] = mapped_column(DECIMAL(19, 4))
    profit: Mapped[Decimal] = mapped_column(DECIMAL(19, 4))
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    
    # Relationships
    sale: Mapped["Sale"] = relationship()
    items: Mapped[list["SaleItemSnapshot"]] = relationship()
    fees: Mapped[list["SaleFeeSnapshot"]] = relationship()
```

```python
# app/models/project.py (existing)
class ProjectSnapshot(Base):
    """Immutable project record for exports/dashboards"""
    __tablename__ = "project_snapshots"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"))
    snapshot_date: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    
    # Financial data (DECIMAL precision)
    total_cost: Mapped[Decimal] = mapped_column(DECIMAL(19, 4))
    selling_price: Mapped[Decimal] = mapped_column(DECIMAL(19, 4))
    profit: Mapped[Decimal] = mapped_column(DECIMAL(19, 4))
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
```

```python
# app/models/partner.py (existing)
class PartnerDistribution(Base):
    """Partner dividend payments for dashboards"""
    __tablename__ = "partner_distributions"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    partner_id: Mapped[int] = mapped_column(ForeignKey("partners.id"))
    distribution_date: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    
    # Financial data (DECIMAL precision)
    invested_amount: Mapped[Decimal] = mapped_column(DECIMAL(19, 4))
    profit_percentage: Mapped[Decimal] = mapped_column(DECIMAL(5, 2))  # Stored at calculation time
    distributed_amount: Mapped[Decimal] = mapped_column(DECIMAL(19, 4))
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
```

```python
# app/models/inventory.py (existing)
class InventoryMovement(Base):
    """Inventory changes for dashboards"""
    __tablename__ = "inventory_movements"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    movement_type: Mapped[str]  # 'sale', 'restock', 'reversal'
    quantity_delta: Mapped[int]
    reason: Mapped[str]
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    
    # Relationship
    product: Mapped["Product"] = relationship()
```

**Key Points**:
- All monetary values use `DECIMAL(19, 4)` for precision
- Snapshots are immutable after creation
- No modifications needed for export/dashboard feature

---

## New Pydantic Schemas (Non-Persisted)

### Export Request/Response Schemas

```python
# app/schemas/export.py (NEW)

from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from pydantic import BaseModel, Field, validator

class ExportFormat(str, Enum):
    CSV = "csv"
    XLSX = "xlsx"
    PDF = "pdf"

class ExportRequest(BaseModel):
    """Request schema for all export endpoints"""
    format: ExportFormat
    start_date: date
    end_date: date
    
    @validator('end_date')
    def end_date_after_start(cls, v, values):
        if 'start_date' in values and v < values['start_date']:
            raise ValueError('end_date must be on or after start_date')
        return v

class ExportMetadata(BaseModel):
    """Metadata included in export file headers"""
    generated_at: datetime
    format: ExportFormat
    report_type: str
    row_count: int
    date_range: tuple[date, date]
    generated_by: str  # User email or ID
    
    class Config:
        json_encoders = {
            Decimal: float  # Convert to float for JSON serialization
        }

class ExportResponse(BaseModel):
    """Response schema for export status (WebSocket progress)"""
    export_id: str
    status: str  # 'started', 'processing', 'completed', 'failed'
    progress: int = Field(0, ge=0, le=100)
    download_url: str | None = None
    error_message: str | None = None
    metadata: ExportMetadata | None = None

class ExportLimits(BaseModel):
    """Configuration for export row limits"""
    CSV_MAX_ROWS: int = 100000
    XLSX_MAX_ROWS: int = 50000
    PDF_MAX_ROWS: int = 10000
    RATE_LIMIT_THRESHOLD: int = 5000  # Rows before rate limiting applies
```

### Dashboard Data Schemas

```python
# app/schemas/dashboard.py (NEW)

from datetime import date
from decimal import Decimal
from pydantic import BaseModel, Field
from typing import Literal

class DashboardFilter(BaseModel):
    """Base filter for all dashboards"""
    start_date: date
    end_date: date
    
class SalesDashboardFilter(DashboardFilter):
    """Filter for sales dashboard"""
    pass

class ProjectsDashboardFilter(DashboardFilter):
    """Filter for projects dashboard"""
    project_id: int | None = None  # Optional specific project filter

class PartnersDashboardFilter(DashboardFilter):
    """Filter for partners dashboard"""
    partner_id: int | None = None  # Optional specific partner filter

class InventoryDashboardFilter(DashboardFilter):
    """Filter for inventory dashboard"""
    pass

# Chart Data Point Schemas

class ChartDataPoint(BaseModel):
    """Single point in a time-series chart"""
    date: date
    value: Decimal
    
    class Config:
        json_encoders = {Decimal: float}

class SalesChartData(BaseModel):
    """Data for sales line chart"""
    dates: list[date]
    revenue: list[Decimal]
    profit: list[Decimal]
    vat: list[Decimal]
    
    @validator('revenue', 'profit', 'vat')
    def validate_length(cls, v, values):
        if 'dates' in values and len(v) != len(values['dates']):
            raise ValueError('All arrays must have same length')
        return v
    
    @validator('dates')
    def max_points(cls, v):
        if len(v) > 1000:
            raise ValueError('Maximum 1000 data points allowed')
        return v
    
    class Config:
        json_encoders = {Decimal: float}

class ProjectChartData(BaseModel):
    """Data for projects bar chart"""
    project_names: list[str]
    profits: list[Decimal]
    profit_margins: list[Decimal]  # Percentage
    project_ids: list[int]
    
    @validator('project_names', 'profits', 'profit_margins', 'project_ids')
    def max_points(cls, v):
        if len(v) > 1000:
            raise ValueError('Maximum 1000 projects allowed')
        return v
    
    class Config:
        json_encoders = {Decimal: float}

class PartnerChartData(BaseModel):
    """Data for partners pie chart"""
    partner_names: list[str]
    dividend_amounts: list[Decimal]
    percentages: list[Decimal]  # Percentage of total
    partner_ids: list[int]
    
    @validator('partner_names', 'dividend_amounts', 'percentages', 'partner_ids')
    def max_points(cls, v):
        if len(v) > 1000:
            raise ValueError('Maximum 1000 partners allowed')
        return v
    
    class Config:
        json_encoders = {Decimal: float}

class InventoryChartData(BaseModel):
    """Data for inventory stacked bar chart"""
    dates: list[date]
    sales: list[int]  # Quantities
    restocks: list[int]
    reversals: list[int]
    
    @validator('sales', 'restocks', 'reversals')
    def validate_length(cls, v, values):
        if 'dates' in values and len(v) != len(values['dates']):
            raise ValueError('All arrays must have same length')
        return v
    
    @validator('dates')
    def max_points(cls, v):
        if len(v) > 1000:
            raise ValueError('Maximum 1000 data points allowed')
        return v

class DashboardResponse(BaseModel):
    """Generic dashboard response with error handling"""
    success: bool
    data: SalesChartData | ProjectChartData | PartnerChartData | InventoryChartData | None
    error: str | None = None
    total_points: int | None = None
    filter_applied: DashboardFilter | None = None
```

### Error Schemas

```python
# app/schemas/errors.py (NEW)

from pydantic import BaseModel
from typing import Literal

class ExportError(BaseModel):
    """Export-specific errors"""
    error_type: Literal[
        "row_limit_exceeded",
        "rate_limit_exceeded",
        "invalid_date_range",
        "no_data_available",
        "generation_failed"
    ]
    message: str
    details: dict | None = None
    
    class Config:
        json_encoders = {Decimal: float}

class RowLimitExceededError(BaseModel):
    """Specific error for row limit violations"""
    error_type: Literal["row_limit_exceeded"] = "row_limit_exceeded"
    format: str
    requested_rows: int
    max_allowed: int
    message: str
    
    class Config:
        json_encoders = {Decimal: float}

class RateLimitExceededError(BaseModel):
    """Specific error for rate limiting"""
    error_type: Literal["rate_limit_exceeded"] = "rate_limit_exceeded"
    message: str
    retry_after: int  # Seconds until limit resets
    
    class Config:
        json_encoders = {Decimal: float}
```

---

## Data Flow

### Export Data Flow

```
1. User Request (Frontend)
   ↓ ExportRequest { format: "csv", start_date: "2026-01-01", end_date: "2026-03-31" }
   
2. API Validation (FastAPI)
   ↓ Validate format, date range
   
3. Row Count Check
   ↓ Query: SELECT COUNT(*) FROM sale_snapshots WHERE date BETWEEN ?
   ↓ If count > limit → return RowLimitExceededError
   ↓ If large request >5000 rows → check rate limit
   
4. Data Retrieval (ReportService)
   ↓ Reuse existing queries
   ↓ Return list[SaleSnapshot] with DECIMAL values preserved
   
5. Format Conversion (ExportService)
   ↓ CSV: pandas DataFrame → BytesIO
   ↓ XLSX: pandas DataFrame → BytesIO with xlsxwriter
   ↓ PDF: ReportLab → temp file
   
6. Response Streaming
   ↓ StreamingResponse (CSV/XLSX) or FileResponse (PDF)
   
7. Progress Updates (WebSocket)
   ↓ Progress: 0% (started) → 50% (processing) → 100% (completed)
   
8. Frontend Download
   ↓ File downloaded with proper MIME type
```

### Dashboard Data Flow

```
1. User Request (Frontend)
   ↓ DashboardFilter { start_date: "2026-01-01", end_date: "2026-03-31" }
   
2. API Validation
   ↓ Validate date range
   
3. Data Aggregation (DashboardService)
   ↓ SQLAlchemy GROUP BY on snapshots
   ↓ Preserve DECIMAL throughout
   
4. Point Limit Check
   ↓ If aggregated points > 1000 → return error with suggestion
   
5. Response
   ↓ DashboardResponse { data: SalesChartData, total_points: 90 }
   
6. Frontend Rendering
   ↓ Recharts renders with Decimal precision in tooltips
   ↓ Formatter: value.toFixed(2) for display
```

---

## Data Integrity Constraints

### Export Limits (Non-Database)

```python
# app/core/config.py

class Settings(BaseSettings):
    # Export row limits (FR-040)
    CSV_MAX_ROWS: int = 100000
    XLSX_MAX_ROWS: int = 50000
    PDF_MAX_ROWS: int = 10000
    
    # Rate limiting (FR-039)
    EXPORT_RATE_LIMIT_THRESHOLD: int = 5000
    EXPORT_RATE_LIMIT_PER_HOUR: int = 10
    
    # Dashboard limits (FR-028)
    DASHBOARD_MAX_POINTS: int = 1000
    
    # Performance thresholds (FR-035)
    EXPORT_TIMEOUT_SECONDS: int = 30
    DASHBOARD_TIMEOUT_SECONDS: int = 3
```

### Validation Rules

1. **Date Range Validation**:
   - End date must be >= start date
   - No future dates allowed
   - Maximum span: configurable (default: 1 year)

2. **Row Count Validation**:
   - Count rows before generation
   - Reject if exceeds format limit
   - Warn if approaches 80% of limit (FR-041)

3. **Data Point Limit**:
   - Aggregate at database level
   - Limit to 1000 points (FR-028)
   - Error with suggestion if exceeded

4. **Decimal Preservation**:
   - All monetary values remain DECIMAL until final serialization
   - JSON: Convert to float with precision control
   - CSV/XLSX: Use float_format='%.4f'
   - PDF: Render as string with to_eng_string()

---

## State Transitions

### Export Progress States

```
[Not Started]
      ↓ (request received)
[Validating]
      ↓ (valid format, date range)
[Checking Limits] ←──┐
      ↓ (within limits)│ (exceeds limits) → [Failed: Limit Exceeded]
[Processing]          │
      ↓ (generating file)
[Completed]           │
      ↓               │
[Downloaded]          │
                      │
[Cancelled] ──────────┘ (user action)
```

### Dashboard Filter States

```
[Initial Load] (default: current month)
      ↓
[User Filters] (date range, optional project/partner)
      ↓
[Validate Range]
      ↓ (valid)
[Fetch Data]
      ↓
[Check Point Limit] ←─┐ (exceeds limit)
      ↓ (within limit) │
[Render Chart]        │→ [Error: Limit Exceeded] + suggestion
      ↓
[Display with Tooltips]
```

---

## Migration Strategy

**No database migrations required** for this feature.

All new functionality uses:
1. Existing model tables (no schema changes)
2. Pydantic schemas for validation (non-persisted)
3. Configuration values for limits (settings.py)

**Future migrations** (if multi-tenant):
- Add `export_audit_log` table to track exports per user
- Add `user_id` foreign key to exports for per-user rate limits
- These would be additive migrations, not destructive

---

## Performance Considerations

### Query Optimization

```python
# Existing ReportService queries (reused)
# Use database-level aggregation for dashboards

async def get_sales_dashboard_data(
    self, start_date: date, end_date: date
) -> SalesChartData:
    # Single query with GROUP BY for minimal data transfer
    query = select(
        func.date(SaleSnapshot.snapshot_date).label('date'),
        func.sum(SaleSnapshot.subtotal).label('revenue'),
        func.sum(SaleSnapshot.profit).label('profit'),
        func.sum(SaleSnapshot.vat_amount).label('vat')
    ).where(
        SaleSnapshot.snapshot_date >= start_date,
        SaleSnapshot.snapshot_date <= end_date
    ).group_by(
        func.date(SaleSnapshot.snapshot_date)
    ).order_by(
        func.date(SaleSnapshot.snapshot_date)
    )
    
    # Returns only aggregated data (much smaller result set)
    results = await self.db.execute(query)
    return self._to_chart_data(results.all())
```

### Caching Strategy

**No caching required** for MVP:
- Exports are read-only, generated on-demand
- Dashboard data refreshes on filter change
- No shared state between requests

**Future optimization** (if needed):
- Cache dashboard aggregation results (5minute TTL)
- Cache export metadata for duplicate requests
- Add cache invalidation on new snapshot creation

---

## Summary

| Component | Type | Storage | Purpose |
|-----------|------|---------|---------|
| SaleSnapshot | Model | PostgreSQL | Source data for sales exports/dashboards |
| ProjectSnapshot | Model | PostgreSQL | Source data for project dashboards |
| PartnerDistribution | Model | PostgreSQL | Source data for partner dashboards |
| InventoryMovement | Model | PostgreSQL | Source data for inventory dashboards |
| ExportRequest | Schema | Non-persisted | Validate export API requests |
| ExportMetadata | Schema | Non-persisted | Metadata in export file headers |
| DashboardFilter | Schema | Non-persisted | Validate dashboard filter requests |
| ChartDataPoint | Schema | Non-persisted | Chart data point representation |
| [X]ChartData | Schema | Non-persisted | Typed chart data for each dashboard |
| ExportLimits | Config | Settings | Centralized limit configuration |

**Key Points**:
- ✅ Zero database schema changes
- ✅ All monetary values remain DECIMAL throughout
- ✅ Immutable snapshots are source of truth
- ✅ Configuration-driven limits
- ✅ Reuses existing models and queries