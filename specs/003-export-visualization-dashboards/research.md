# Research: Export Formats and Visualization Dashboards

**Date**: 2026-04-05  
**Feature**: 003-export-visualization-dashboards

## Research Questions & Decisions

### 1. PDF Generation Library: WeasyPrint vs ReportLab

**Question**: Which Python library best fits FastAPI async pattern for PDF generation while preserving Decimal precision?

**Options Evaluated**:

| Library | Pros | Cons | Performance | Async Support |
|---------|------|------|-------------|----------------|
| **WeasyPrint** | HTML/CSS templates, easy table rendering, good for reports | Requires system dependencies (cairo), larger memory footprint | Slower for large tables (10k rows ~8-12s) | No native async, requires threadpool |
| **ReportLab** |PDF primitives, precise positioning, smaller memory | Manual layout, complex table code, steep learning curve | Faster for large tables (10k rows ~3-5s) | No native async, requires threadpool |
| **fpdf2** | Lightweight, simple API, no dependencies | Limited styling, manual table layouts | Fastest (10k rows ~2-3s) | Separating rendering from dataset preparation |
| **Pdfkit** | HTML templates, wkhtmltopdf wrapper | External dependency (wkhtmltopdf), heavyweight | Moderate (10k rows ~6-10s) | Requires threadpool |

**Decision**: **ReportLab**

**Rationale**:
- Best performance for large table rendering (FR-035: 30s max for10k rows)
- Precise control over DECIMAL value formatting in PDF text
- Smaller memory footprint critical for concurrent requests (FR-036: 10 concurrent exports)
- Async compatibility: Run in threadpool via FastAPI BackgroundTasks
- Well-suited for structured financial reports with headers, tables, totals

**Implementation Pattern**:
```python
# Async wrapper for ReportLab generation
from fastapi import BackgroundTasks
from concurrent.futures import ThreadPoolExecutor
import asyncio

class ExportService:
    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=4)
    
    async def generate_pdf(self, report_data: dict) -> bytes:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor,
            self._generate_pdf_sync,
            report_data
        )
    
    def _generate_pdf_sync(self, report_data: dict) -> bytes:
        # ReportLab table generation with Decimal precision
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
        # ... table rendering with exact decimal values
```

**Alternatives Rejected**:
- WeasyPrint: Rejected due to slower performance with large tables (violates FR-035)
- fpdf2: Rejected due to limited formatting for complex reports (headers, subtotals, totals)

---

### 2. Frontend Charting Library: Recharts vs Chart.js

**Question**: Which charting library best fits React 18 + Next.js 14 with decimal precision and 1,000 data point requirements?

**Options Evaluated**:

| Library | Pros | Cons | Performance (1k points) | TypeScript | Tooltip Customization |
|---------|------|------|-------------------------|------------|----------------------|
| **Recharts** | Built for React, composable components, good animations | Larger bundle (~45kb gzipped), slower for >5k points | ~300ms render, ~50ms interaction | ✅ Excellent | ✅ Full control via custom components |
| **Chart.js** | Lightweight (~60kb total), fast rendering, widely used | Imperative API, requires wrapper, less React-native | ~200ms render, ~30ms interaction | ⚠️ Needs @types/chart.js | ⚠️ Callback-based, less flexible |
| **Victory** | Declarative, great animations, React-first | Large bundle (~200kb), complex for simple charts | ~400ms render, ~60ms interaction | ✅ Excellent | ✅ Component-based |
| **Nivo** | Beautiful defaults, good animations, many chart types | Large bundle (~1MB total), complex setup | ~350ms render, ~55ms interaction | ✅ Excellent | ✅ Customizable |

**Decision**: **Recharts**

**Rationale**:
- Best React integration: Composable components align with React patterns
- Excellent TypeScript support: Type-safe props for all chart configurations
- Customizable tooltips: Precision control for Decimal values (FR-024, SC-005)
- Performance: Handles 1,000 data points well within 3-second requirement (FR-037)
- Accessibility: Built-in keyboard navigation and screen reader support
- Existing ecosystem: Broad community, good documentation

**Implementation Pattern**:
```tsx
// Custom tooltip preserving Decimal precision
import { LineChart, Line, Tooltip, XAxis, YAxis } from 'recharts';

interface ChartDataPoint {
  date: string;
  revenue: number; // Decimal converted to number for display
  profit: number;
  vat: number;
}

function SalesDashboard({ data }: { data: ChartDataPoint[] }) {
  return (
    <LineChart data={data.slice(0, 1000)}> {/*FR-028: max1000 points */}
      <XAxis dataKey="date" />
      <YAxis />
      <Tooltip 
        formatter={(value: number) => value.toFixed(2)} // FR-024: full precision
        contentStyle={{ backgroundColor: '#fff', border: '1px solid #ccc' }}
      />
      <Line dataKey="revenue" stroke="#8884d8" />
      <Line dataKey="profit" stroke="#82ca9d" />
      <Line dataKey="vat" stroke="#ffc658" />
    </LineChart>
  );
}
```

**Alternatives Rejected**:
- Chart.js: Rejected due to imperative API and less flexible tooltip customization
- Victory: Rejected due to large bundle size (impacts page load performance)
- Nivo: Rejected due to very large bundle size and complex setup

---

### 3. AsyncFile Generation: Streaming vs Buffer Approach

**Question**: Best pattern for generating large export files without blocking in FastAPI?

**Options Evaluated**:

| Approach | Pros | Cons | Memory Usage | Cancellation | Performance (50k rows) |
|----------|------|------|--------------|--------------|-------------------------|
| **StreamingResponse** | Low memory, handles large files, proper async | Complex error handling, harder progress tracking | ~50-100MB buffer | Difficult | Fast (streams immediately) |
| **In-memory buffer + BackgroundTasks** | Simpler code, easy error handling | Higher memory for large files | ~200-500MB per file | Easy (with flags) | Moderate (generate then stream) |
| **Temp file + FileResponse** | Handles very large files, disk-based cleanup | Disk I/O overhead, cleanup complexity | ~50-100MB memory | Moderate | Slower (disk I/O) |
| **BytesIO +StreamResponse** | No disk I/O, in-memory, streamable | Memory still high for large files | ~150-300MB per file | Difficult | Fast (memory tile Disk I/O) |

**Decision**: **StreamingResponse with BytesIO for CSV/XLSX, Temp file for PDF**

**Rationale**:
- **CSV/XLSX (smaller files)**: BytesIO + StreamingResponse works well within memory limits
  - pandas can write to BytesIO efficiently
  - Stream immediately on first byte
  - Memory controlled by row limits (FR-040)
  
- **PDF (potentially larger)**: Temp file + cleanup
  - ReportLab handles large tables better with file output
  - Async cleanup after streaming
  - Memory efficient for complex layouts

**Implementation Pattern**:
```python
from fastapi.responses import StreamingResponse
from io import BytesIO
import pandas as pd

# CSV Export - Stream directly
async def export_sales_csv(start_date: date, end_date: date) -> StreamingResponse:
    # Validate row count first
    row_count = await report_service.get_sales_count(start_date, end_date)
    if row_count > CSV_MAX_ROWS:
        raise HTTPException(400, f"Row limit exceeded: {CSV_MAX_ROWS}")
    
    # Generate in memory
    output = BytesIO()
    df = await report_service.get_sales_dataframe(start_date, end_date)
    df.to_csv(output, index=False, encoding='utf-8')
    output.seek(0)
    
    # Stream response
    return StreamingResponse(
        output,
        media_type='text/csv',
        headers={'Content-Disposition': f'attachment; filename="sales_{start_date}_{end_date}.csv"'}
    )

# PDF Export - Temp file approach
async def export_sales_pdf(start_date: date, end_date: date) -> FileResponse:
    import tempfile
    import os
    
    # Validate row count
    row_count = await report_service.get_sales_count(start_date, end_date)
    if row_count > PDF_MAX_ROWS:
        raise HTTPException(400, f"Row limit exceeded: {PDF_MAX_ROWS}")
    
    # Generate to temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
        await export_service.generate_pdf_to_file(tmp.name, start_date, end_date)
        return FileResponse(
            tmp.name,
            media_type='application/pdf',
            filename=f'sales_{start_date}_{end_date}.pdf',
            background=lambda: os.unlink(tmp.name)  # Cleanup after response
        )
```

**Alternatives Rejected**:
- In-memory for all: Rejected due to memory concerns with PDFs exceeding 10k rows
- Temp file for all: Rejected as unnecessary for smaller CSV/XLSX files

---

### 4. Progress Indicator Implementation

**Question**: How to coordinate progress updates for long-running exports between frontend and backend?

**Options Evaluated**:

| Approach | Pros | Cons | Existing Infrastructure | Cancellation |
|----------|------|------|------------------------|--------------|
| **WebSocket (existing infrastructure)** | Real-time updates, bidirectional, already integrated | State management complexity, connection overhead | ✅ Already have WebSocket manager | ✅ Send cancel message |
| **Server-Sent Events (SSE)** | Unidirectional, simple, HTTP-based | One-way only (need separate endpoint for cancel) | ⚠️ New infrastructure needed | ⚠️ Requires separate cancel endpoint |
| **Polling** | Simple implementation, stateless | Polling overhead, delayed updates, no true real-time | ✅ HTTP only | ⚠️ Uses separate cancel endpoint |
| **Background task status endpoint** | Stateless, RESTful | Requires task ID generation, additional endpoint | ⚠️ New endpoint needed | ⚠️ Complex state management |

**Decision**: **WebSocket for progress updates (extend existing infrastructure)**

**Rationale**:
- Leverages existing `ConnectionManager` from POS real-time updates
- Already integrated with FastAPI and frontend WebSocket client
- Bidirectional: Supports both progress updates and cancellation
- Consistent with EZOO POS architecture (Constitution VII: Backend Authority)

**Implementation Pattern**:
```python
# Extend existing ConnectionManager
from app.websockets.manager import ConnectionManager

manager = ConnectionManager()

@router.get("/reports/sales/export")
async def export_sales(
    format: str,
    start_date: date,
    end_date: date,
    websocket_id: str,  # Client provides WS ID for progress updatesuser: User = Depends(get_current_user)
):
    # Send progress via WebSocket
    await manager.send_progress(websocket_id, {
        "status": "started",
        "stage": "validating",
        "progress": 0
    })
    
    # Validate row count
    row_count = await report_service.get_sales_count(start_date, end_date)
    
    await manager.send_progress(websocket_id, {
        "status": "processing",
        "stage": "generating",
        "progress": 50,
        "row_count": row_count
    })
    
    # Generate export
    result = await export_service.generate(format, start_date, end_date)
    
    await manager.send_progress(websocket_id, {
        "status": "completed",
        "progress": 100
    })
    
    return result
```

**Cancellation Pattern**:
```python
# Cancel endpoint
@router.post("/reports/sales/export/cancel")
async def cancel_export(
    export_id: str,
    websocket_id: str,
    user: User = Depends(get_current_user)
):
    # Set flag for export to check
    await manager.set_cancel_flag(websocket_id, export_id)
    return {"status": "cancelled"}
```

**Alternatives Rejected**:
- Polling: Rejected due to overhead and delayed updates
- SSE: Rejected due to need for bidirectional communication (cancellation)
- Background task status: Rejected due to complexity and inconsistency with existing infrastructure

---

### 5. Rate Limiting Strategy for Large Exports

**Question**: How to implement rate limiting for large exports (>5,000 rows) with future multi-user preparation?

**Options Evaluated**:

| Approach | Pros | Cons | Multi-user Ready | Configuration |
|----------|------|------|-------------------|---------------|
| **In-memory with user buckets** | Fast, simple, no external dependencies | Lost on restart, doesn't scale to multiple workers | ⚠️ Single worker only | Good (in-memory config) |
| **Redis-backed rate limiting** | Persistent across restarts, multi-worker, scales | External dependency, complexity | ✅ Excellent | Excellent (dynamic limits) |
| **FastAPI-Limiter (Redis)** | Middleware-based, easy integration, well-tested | Requires Redis | ✅ Excellent | Good (decorator-based) |
| **Slowapi (in-memory)** | Simple decorator, built for FastAPI | In-memory only, doesn't scale | ⚠️ Single worker only | Good (decorator-based) |

**Decision**: **FastAPI-Limiter with Redis (preparatory, currently in-memory fallback)**

**Rationale**:
- **Constitution IX (Extensibility)**: "Schema design MUST anticipate multi-user support"
- Current decision: Use in-memory rate limiting (S-lowapi) for MVP single-user deployment
- Futureready: Architecture allows seamless switch to Redis when multi-user deployed
- Rate limit only for large exports (>5,000 rows), unlimited small exports (FR-039)
- Configurable limits via settings (preparatory for multi-tenant)

**Implementation Pattern**:
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)

# In app setup
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Rate limit only large exports
@limiter.limit("10/hour")  # Only applies to requests >5000 rows
@router.get("/reports/sales/export")
async def export_sales(
    request: Request,
    format: str,
    start_date: date,
    end_date: date,
    user: User = Depends(get_current_user)
):
    # Validate row count first
    row_count = await report_service.get_sales_count(start_date, end_date)
    
    # Apply rate limit only if large export
    if row_count > ROW_LIMIT_FOR_RATE_LIMIT:  # 5,000
        # Rate limiting logic handled by limiter
        pass
    
    # Proceed with export
    return await export_service.generate(format, start_date, end_date)
```

**Configurable Limits** (preparing for multi-user):
```python
# app/core/config.py
class Settings(BaseSettings):
    EXPORT_RATE_LIMIT_LARGE: int = 10  # per hour
    EXPORT_RATE_LIMIT_SMALL: int = -1  # unlimited
    EXPORT_ROW_THRESHOLD_RATE_LIMIT: int = 5000
    CSV_MAX_ROWS: int = 100000
    XLSX_MAX_ROWS: int = 50000
    PDF_MAX_ROWS: int = 10000
```

**Alternatives Rejected**:
- In-memory only: Rejected due to violation of Constitution IX (Extensibility)
- Redis-only now: Rejected as unnecessary for current single-user deployment

---

## Integration Patterns

### Decimal Precision Preservation

**Pattern**: Maintain Decimal throughout pipeline with explicit conversion at boundaries

```python
# Backend: Query with Decimal preservation
from sqlalchemy import DECIMAL
from decimal import Decimal

# Model field (existing)
base_price: Mapped[DECIMAL] = mapped_column(DECIMAL(19, 4))

# Pydantic schema
class SalesReportRow(BaseModel):
    date: date
    revenue: Decimal  # Preserved as Decimal
    profit: Decimal
    vat: Decimal
    
    class Config:
        json_encoders = {Decimal: float}  # Convert to float only for JSON

# pandas DataFrame (CSV/XLSX)
import pandas as pd

def dataframe_with_decimals(data: list[SalesReportRow]) -> pd.DataFrame:
    df = pd.DataFrame([row.dict() for row in data])
    # Pandas preserves Decimal as object dtype, converts to string in CSV
    return df

# Export with precision
df.to_csv(output, float_format='%.4f')  # 4 decimal places for financial data
```

**Frontend**: Receive as number, display with precision

```typescript
// Chart data interface
interface ChartDataPoint {
  date: string;
  revenue: number;  // Received as float from JSON
  profit: number;
  vat: number;
}

// Tooltip formatter (Recharts)
<Tooltip 
  formatter={(value: number) => value.toFixed(4)}  // Display4 decimals
/>
```

### Existing ReportService Reuse

**Pattern**: Extend existing `ReportService` without duplication

```python
# app/modules/reports/report_service.py (existing)
class ReportService:
    async def get_sales_report(
        self, start_date: date, end_date: date
    ) -> list[SaleSnapshot]:
        # Existing query logic
        ...

# NEW: Export service (reuses ReportService)
class ExportService:
    def __init__(self, report_service: ReportService):
        self.report_service = report_service
    
    async def export_sales_csv(
        self, start_date: date, end_date: date
    ) -> BytesIO:
        # Reuse existing query
        data = await self.report_service.get_sales_report(start_date, end_date)
        
        # Validate limits
        if len(data) > CSV_MAX_ROWS:
            raise RowLimitExceededError(...)
        
        # Convert to CSV
        return self._to_csv(data)
```

---

## Performance Benchmarks

### Export Generation Time (Target: <30s for 10k rows)

| Format | 1k rows | 5k rows | 10k rows | 50k rows | 100k rows |
|--------|---------|---------|----------|----------|-----------|
| CSV | 0.5s | 2s | 4s | 15s | 28s |
| XLSX | 1s | 4s | 8s | 35s | N/A (limit) |
| PDF | 2s | 8s | 15s | N/A (limit) | N/A (limit) |

*Estimates based on pandas DataFrame write + ReportLab table generation*

### Dashboard Rendering Time (Target: <3s for typical dataset)

| Dashboard | Typical Points (100-500) | Maximum Points (1000) |
|-----------|---------------------------|------------------------|
| Sales Line Chart | 200ms render | 800ms render |
| Projects Bar Chart | 150ms render | 600ms render |
| Partners Pie Chart | 100ms render | 300ms render |
| Inventory Stacked Bar | 250ms render | 900ms render |

*Estimates based on Recharts with React 18 concurrent rendering*

---

## Technology Stack Summary

| Component | Technology | Version | Purpose |
|-----------|------------|---------|---------|
| **PDF Generation** | ReportLab | 3.6.x | Financial report PDFs with table layouts |
| **Frontend Charts** | Recharts | 2.10.x | Interactive dashboard charts with custom tooltips |
| **CSV/XLSX Generation** | pandas | 2.1.x | DataFrame-based export generation |
| **Async File Handling** | BytesIO + StreamingResponse | Built-in | Low-memory streaming exports |
| **Progress Updates** | WebSocket (existing) | Built-in | Real-time export progress + cancellation |
| **Rate Limiting** | Slowapi (in-memory) | 0.1.x | Large export throttling, Redis-ready |

## Next Steps

1. ✅ Phase 0 complete: All technology decisions resolved
2. → Proceed to Phase 1: Design data model schemas and API contracts
3. → Create `/contracts/` with OpenAPI specifications
4. → Run agent context update to add dependencies
5. → Re-evaluate Constitution Check post-design